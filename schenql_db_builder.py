"""
This file downloads and builds the database for the schenql-query language
"""

import argparse
import configparser
import gzip
import os
import re
import time
import urllib.request

import mysql.connector
import progressbar
from lxml import etree

# Defines how many SQL Insert statements will be executed at once
BATCH_SIZE = 256

# Database connection
db_connection = None


def download_dblp(dblp_url, dblp_dtd_url, data_path):
    """
    Downloading the dblp.xml.gz to the specified data_path for further processing
    :param url: URL to the dblp.xml.gz file (probably: https://dblp.uni-trier.de/xml/dblp.xml.gz)
    :param data_path: Path where the dblp.xml.gz file is saved to
    """
    print("Downloading dblp.xml.gz...")
    urllib.request.urlretrieve(dblp_url, os.path.join(data_path, "dblp.xml.gz"))
    urllib.request.urlretrieve(dblp_dtd_url, os.path.join(data_path, "dblp.dtd"))
    print("Downloading dblp DONE!")


def cleanup_db():
    """
    Clean up the database for a new build
    :param conn: database connection
    """
    table_cur = db_connection.cursor(buffered=True)
    cur2 = db_connection.cursor()
    print("Cleaning up database...")
    table_cur.execute("""SET FOREIGN_KEY_CHECKS = 0""")
    table_cur.execute("""SHOW TABLES""")
    for table in table_cur:
        print("""TRUNCATE TABLE """ + table[0])
        cur2.execute("""TRUNCATE TABLE """ + table[0])
    table_cur.execute("""SET FOREIGN_KEY_CHECKS = 1""")
    table_cur.close()
    cur2.close()
    print("""Cleanup DONE!""")


def build_db_from_dblp(data_path, inst_names):
    """
    Builds mysql-database from dblp.xml
    :param conn: database connection
    :param inst_names: dictionary of institution names
    :param data_path: path to dblp.xml.gz
    """
    print("Processing dblp file...")

    affiliations = []
    conference_key_dict = {}
    journal_key_dict = {}
    journal_name_dict = {}
    publications = []
    person_authored = []
    person_edited = []
    person_keys = []
    person_names = {}
    orcids = {}

    context = etree.iterparse(gzip.GzipFile(os.path.join(data_path, "dblp.xml.gz")),
                              tag=("article", "masterthesis", "phdthesis", "inproceedings", "book", "www"),
                              load_dtd=True,
                              encoding='iso-8859-1')
    bar = progressbar.ProgressBar(max_value=progressbar.UnknownLength)
    counter = 0

    for _, elem in context:
        counter += 1
        bar.update(counter)

        dblp_key = elem.get("key")
        type = elem.tag

        # Processing publications
        if elem.tag in ("article", "inproceedings", "masterthesis", "phdthesis", "book"):
            title = elem.find("title").text if elem.find("title") is not None else None
            ee = elem.find("ee").text if elem.find("ee") is not None else None
            url = elem.find("url").text if elem.find("url") is not None else None
            year = int(elem.find("year").text) if elem.find("year") is not None else None
            volume = elem.find("volume").text if elem.find("volume") is not None else None
            conference_key = None
            journal_key = None

            if title:
                title = title.encode('utf-8').decode('latin-1')

            if elem.find("journal") is not None:
                journal = elem.find("journal").text
                # Use the url tag if its available and starts with "db/journals"
                if url and url.startswith("db/journals/"):
                    result = re.search("db/(.*)/.*", url)
                    if result:
                        journal_key = result.group(1)
                elif dblp_key.startswith("journals"):
                    try:
                        journal_key = dblp_key.rsplit("/", 1)[0]
                    except IndexError:
                        print("\nError finding journal key for journal", journal)

                if journal_key:
                    try:
                        acronym = journal_key.rsplit("/", 1)[1]
                    except IndexError:
                        print("Error: ", journal_key)
                        acronym = None

                    # Add journal if not exist
                    if journal_key not in journal_key_dict:
                        journal_key_dict[journal_key] = acronym

                    # Check if journal name already exists otherwise add it
                    if journal not in journal_name_dict:
                        journal_name_dict[journal] = journal_key

            elif elem.tag == "inproceedings":
                if url and url.startswith("db/conf/"):
                    result = re.search("db/(.*)/.*", url)
                    if result:
                        conference_key = result.group(1)
                elif dblp_key.startswith("conf"):
                    try:
                        conference_key = dblp_key.rsplit("/", 1)[0]
                    except IndexError:
                        print("\nError finding conference key for journal", dblp_key)

                if conference_key:
                    try:
                        acronym = conference_key.rsplit("/", 1)[1]
                    except IndexError:
                        print("Error: ", conference_key)
                        acronym = None

                    # Add conference if not exist
                    if conference_key not in conference_key_dict:
                        conference_key_dict[conference_key] = acronym

            authors = elem.findall("author")
            editors = elem.findall("editor")

            # Adding the publications
            publications.append((dblp_key, title, ee, url, year, volume, type, conference_key, journal_key))

            # Adding authors to the publication
            for person in authors:
                if person.get("orcid"):
                    # TODO: This is not 100% correct, but it will work for most cases
                    orcids[person.text] = person.get("orcid")
                person_authored.append((person.text, dblp_key))

            # Adding editors to the publication
            for person in editors:
                person_edited.append((person.text, dblp_key))

        # Processing person records
        if elem.tag == "www":
            if dblp_key and dblp_key.startswith("homepages/"):
                primary_name = elem.find("author").text if elem.find("author") is not None else None

                # Add all available names to person record
                orcid = None
                persons = elem.findall("author")
                for person in persons:
                    if orcid is None and person.text in orcids:
                        orcid = orcids[person.text]
                    person_names[person.text] = dblp_key

                person_keys.append((dblp_key, primary_name, orcid))

                # Add institutions
                notes = elem.findall("note")
                for note in notes:
                    if note.get("type") == "affiliation":
                        if note.text in inst_names:
                            affiliations.append((dblp_key, inst_names[note.text]))

        # Freeing the element since it is not needed anymore
        elem.clear()

    # Finishing the progressbar
    bar.finish()

    # Replace author names with dblpKeys in person_authored
    for i in range(0, len(person_authored)):
        person_authored[i] = (person_names[person_authored[i][0]], person_authored[i][1])

    # Replace author names with dblpKeys in person_edited
    for i in range(0, len(person_edited)):
        person_edited[i] = (person_names[person_edited[i][0]], person_edited[i][1])

    ##################################################
    #        INSERTING DATA INTO DATABASE            #
    ##################################################

    print("\nInserting dblp data into the database...")
    print("\nPerson keys:")
    cur = db_connection.cursor()

    cur.execute("SET FOREIGN_KEY_CHECKS=0;")
    cur.execute("SET UNIQUE_CHECKS=0;")

    with progressbar.ProgressBar(max_value=len(person_keys)) as bar:
        query = """INSERT INTO `person` (`dblpKey`, `orcid`, `primary_name`) VALUES (%s, %s)"""
        for i in range(0, len(person_keys), BATCH_SIZE):
            cur.executemany(query, person_keys[i:i + BATCH_SIZE])
            bar.update(i)

    print("\nAdding person names:")
    person_names_list = list(person_names.items())
    with progressbar.ProgressBar(max_value=len(person_names_list)) as bar:
        query = """INSERT INTO `person_names` (`name`, `personKey`) VALUES (%s, %s)"""
        for i in range(0, len(person_names_list), BATCH_SIZE):
            params = [tuple(el) for el in person_names_list[i: i + BATCH_SIZE]]
            cur.executemany(query, params)
            bar.update(i)

    print("\nAdding affiliations of persons:")
    with progressbar.ProgressBar(max_value=len(affiliations)) as bar:
        query = """INSERT INTO `person_works_for_institution` (`personKey`, `institutionKey`)
                               VALUES (%s, %s)"""
        for i in range(0, len(affiliations), BATCH_SIZE):
            cur.executemany(query, affiliations[i:i + BATCH_SIZE])
            bar.update(i)

    print("\nAdding journals:")
    journal_key_dict_list = list(journal_key_dict.items())
    with progressbar.ProgressBar(max_value=len(journal_key_dict_list)) as bar:
        query = """INSERT INTO `journal` (`dblpKey`, `acronym`) VALUES (%s, %s)"""
        for i in range(0, len(journal_key_dict_list), BATCH_SIZE):
            params = [tuple(el) for el in journal_key_dict_list[i: i + BATCH_SIZE]]
            cur.executemany(query, params)
            bar.update(i)

    print("\nAdding journal names:")
    journal_name_dict_list = list(journal_name_dict.items())
    with progressbar.ProgressBar(max_value=len(journal_name_dict_list)) as bar:
        query = """INSERT INTO `journal_name` (`name`, `journalKey`) VALUES (%s, %s)"""
        for i in range(0, len(journal_name_dict_list), BATCH_SIZE):
            params = [tuple(el) for el in journal_name_dict_list[i: i + BATCH_SIZE]]
            cur.executemany(query, params)
            bar.update(i)

    print("\nAdding conferences:")
    conference_key_dict_list = list(conference_key_dict.items())
    with progressbar.ProgressBar(max_value=len(conference_key_dict_list)) as bar:
        query = """INSERT INTO `conference` (`dblpKey`, `acronym`) VALUES (%s, %s)"""
        for i in range(0, len(conference_key_dict_list), BATCH_SIZE):
            try:
                params = [tuple(el) for el in conference_key_dict_list[i: i + BATCH_SIZE]]
                cur.executemany(query, params)
            except mysql.connector.errors.IntegrityError:
                pass
            bar.update(i)

    print("\nAdding publications:")
    with progressbar.ProgressBar(max_value=len(publications)) as bar:
        query = """INSERT INTO `publication` 
                    (`dblpKey`, `title`, `ee`, `url`, `year`, `volume`, `type`, `conference_dblpKey`, `journal_dblpKey`) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        for i in range(0, len(publications), BATCH_SIZE):
            cur.executemany(query, publications[i:i + BATCH_SIZE])
            bar.update(i)

    print("\nAdding authors of publications:")
    with progressbar.ProgressBar(max_value=len(person_authored)) as bar:
        query = """INSERT INTO `person_authored_publication` (`personKey`, `publicationKey`)
                            VALUES (%s, %s)"""
        for i in range(0, len(person_authored), BATCH_SIZE):
            cur.executemany(query, person_authored[i:i + BATCH_SIZE])
            bar.update(i)

    print("\nAdding editors of publications:")
    with progressbar.ProgressBar(max_value=len(person_edited)) as bar:
        query = """INSERT INTO `person_edited_publication` (`personKey`, `publicationKey`) 
                                VALUES (%s, %s)"""
        for i in range(0, len(person_edited), BATCH_SIZE):
            cur.executemany(query, person_edited[i:i + BATCH_SIZE])
            bar.update(i)

    print("\nCommitting changes:")
    db_connection.commit()

    cur.execute("SET FOREIGN_KEY_CHECKS=1;")
    cur.execute("SET UNIQUE_CHECKS=1;")
    cur.close()


def add_inst_data(data_path):
    parser = etree.XMLParser(ns_clean=True, load_dtd=True, collect_ids=False)
    tree = etree.parse(os.path.join(data_path, "inst.xml"), parser)
    inst_names = {}
    institutions = []
    xml_root = tree.getroot()

    for elem in xml_root.getchildren():
        inst_key = elem.get("key")
        country = None
        city = None
        lat = None
        lon = None
        location_text = None
        if inst_key:
            location = elem.find("location")
            if location is not None:
                country = location.get("country")
                city = location.get("city")
                lat = location.get("lat")
                lon = location.get("lon")
                location_text = location.text

            names = elem.findall("name")
            for name in names:
                inst_names[name.text] = inst_key

            institutions.append((inst_key, location_text, country, city, lat, lon))
        elem.clear()

    ##################################################
    #        INSERTING DATA INTO DATABASE            #
    ##################################################

    print("\nInserting inst data into database...")
    cur = db_connection.cursor()

    print("\nAdding institution keys...")
    query = """INSERT INTO `institution` (`key`, `location`, `country`, `city`, `lat` ,`lon`)
            VALUES (%s, %s, %s, %s, %s, %s)"""
    cur.executemany(query, institutions)

    print("\nAdding institution names...")
    inst_names_list = list(inst_names.items())
    query = """INSERT INTO `institution_name` (`name`, `institutionKey`) VALUES (%s, %s)"""
    cur.executemany(query, inst_names_list)

    print("\nCommitting changes...")
    db_connection.commit()

    cur.close()

    return inst_names


def add_s2_data(data_path):
    print("\nProcessing semantic scholar data. This may take even longer...")
    pub_references_pub2 = []
    keywords = set()
    pub_keywords = []
    abstracts = []
    folder_regex = re.compile("/(journals|conf|phd|books)/")

    bar = progressbar.ProgressBar(max_value=progressbar.UnknownLength)
    counter = 0

    for root, dirs, files in os.walk(os.path.join(data_path, "s2-aux")):
        for name in files:
            if folder_regex.search(root):
                file_path = os.path.join(root, name)
                try:
                    tree = etree.parse(file_path)
                except etree.XMLSyntaxError:
                    print("\nXML Syntax Error in:", file_path)
                    continue
                xml_root = tree.getroot()
                pub_key = xml_root.get("key")
                counter += 1
                bar.update(counter)
                if pub_key:
                    # Sometimes there are two abstracts for one publication, just using the first to find
                    abstract = xml_root.find("abstract")
                    if abstract is not None:
                        abstracts.append((abstract.text.strip(), pub_key))

                    # Sometimes there are cites to same publication
                    cites = xml_root.findall("cite")
                    cited_pubs = set()
                    for cite in cites:
                        cited_pub = cite.get("key")
                        if cited_pub:
                            cited_pubs.add(cited_pub)
                    for cite in cited_pubs:
                        pub_references_pub2.append((pub_key, cite))

                    # Getting all unique keywords for the publication
                    keyword_tags = xml_root.findall("keyword")
                    keywords_of_pub = set()
                    for k_tag in keyword_tags:
                        keyword = k_tag.text
                        if keyword:
                            keywords_of_pub.add(keyword)
                    for keyword in keywords_of_pub:
                        keywords.add((keyword,))
                        pub_keywords.append((pub_key, keyword))
    bar.finish()

    ##################################################
    #        INSERTING DATA INTO DATABASE            #
    ##################################################

    print("\nInserting semantic scholar data into database...")
    cur = db_connection.cursor()
    cur.execute("SET FOREIGN_KEY_CHECKS=0;")
    cur.execute("SET UNIQUE_CHECKS=0;")

    print("\nAdding references:")
    with progressbar.ProgressBar(max_value=len(pub_references_pub2)) as bar:
        query = """INSERT INTO `publication_references` (`pub_id`, `pub2_id`) VALUES (%s, %s)"""
        for i in range(0, len(pub_references_pub2), BATCH_SIZE):
            cur.executemany(query, pub_references_pub2[i:i + BATCH_SIZE])
            bar.update(i)

    print("\nAdding abstracts:")
    with progressbar.ProgressBar(max_value=len(abstracts)) as bar:
        query = """UPDATE IGNORE `publication` SET `abstract` = %s WHERE `dblpKey` = %s"""
        for i in range(0, len(abstracts), BATCH_SIZE):
            try:
                cur.executemany(query, abstracts[i: i + BATCH_SIZE])
            except mysql.connector.errors.DatabaseError:
                print("Error in batch:", i)
            bar.update(i)

    print("\nAdding keywords:")
    keyword_list = list(keywords)
    with progressbar.ProgressBar(max_value=len(keyword_list)) as bar:
        for i in range(0, len(keyword_list), BATCH_SIZE):
            query = """INSERT INTO `keyword` (`keyword`) VALUES (%s)"""
            cur.executemany(query, keyword_list[i:i + BATCH_SIZE])
            bar.update(i)

    print("\nAdding keywords to publications:")
    with progressbar.ProgressBar(max_value=len(pub_keywords)) as bar:
        query = """INSERT INTO `publication_has_keyword` (`dblpKey`, `keyword`) VALUES (%s, %s)"""
        for i in range(0, len(pub_keywords), BATCH_SIZE):
            cur.executemany(query, pub_keywords[i:i + BATCH_SIZE])
            bar.update(i)

    print("\nCommitting changes:")
    db_connection.commit()

    cur.execute("SET FOREIGN_KEY_CHECKS=1;")
    cur.execute("SET UNIQUE_CHECKS=1;")
    cur.close()


def main():
    # Parsing command-line arguments
    parser = argparse.ArgumentParser(description="Bulding relational database from DBLP-xml file")
    parser.add_argument("-d", "--download", action="store_true", help="Download the current version of the DBLP")
    parser.add_argument("-c", "--cleardatabase", action="store_true", help="TRUNCATES ALL TABLES!!!")
    parser.add_argument("--dblp", action="store_true", help="Build dblp data")
    parser.add_argument("--cites", action="store_true", help="Build cites data")
    parser.add_argument("--all", action="store_true", help="Build all data")
    args = parser.parse_args()

    # Reading config file
    config = configparser.ConfigParser()
    config.read("config.ini")
    data_path = config["PATHS"]["DATA-PATH"]
    dblp_url = config["PATHS"]["DBLP-XML"]
    dblp_dtd_url = config["PATHS"]["DBLP-DTD"]

    # Download data
    download = False
    if args.download:
        download = True
    if not os.path.exists(os.path.join(data_path, "dblp.xml.gz")):
        download = True
        print("DBLP file not available. Current version of DBLP will be downloaded.")
    if download:
        download_dblp(dblp_url, dblp_dtd_url, data_path)

    # Connect to database
    global db_connection
    db_connection = mysql.connector.connect(
        host=config["DATABASE"]["HOST"],
        user=config["DATABASE"]["USER"],
        passwd=config["DATABASE"]["PASS"],
        database=config["DATABASE"]["DB"]
    )

    # Cleanup database
    if args.cleardatabase:
        cleanup_db()

    # Build database
    start = time.time()
    print("\n###############################\nStart %s\n###############################\n" % (time.ctime()))

    if args.dblp or args.all:
        inst_names = add_inst_data(data_path)
        build_db_from_dblp(data_path, inst_names)
    if args.cites or args.all:
        add_s2_data(data_path)

    end = time.time()
    print("Time spent:", end - start, "s")

    # Closing connection to database
    db_connection.close()


if __name__ == '__main__':
    main()
