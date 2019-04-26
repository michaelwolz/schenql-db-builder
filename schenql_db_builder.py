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
BATCH_SIZE = 10000


class DBConnection:
    """
    Connection to the database
    """
    def __init__(self, host, user, passwd, db):
        self.db_connection = mysql.connector.connect(host=host, user=user, passwd=passwd, database=db)

    def __del__(self):
        self.db_connection.close()


def download_dblp(url, data_path):
    """
    Downloading the dblp.xml.gz to the specified data_path for further processing
    :param url: URL to the dblp.xml.gz file (probably: https://dblp.uni-trier.de/xml/dblp.xml.gz)
    :param data_path: Path where the dblp.xml.gz file is saved to
    """
    print("Downloading dblp.xml.gz...")
    urllib.request.urlretrieve(url, os.path.join(data_path, "dblp.xml.gz"))
    print("Downloading dblp DONE!")


def cleanup_db(conn):
    """
    Clean up the database for a new build
    :param conn: database connection
    """
    table_cur = conn.cursor(buffered=True)
    cur2 = conn.cursor()
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


def build_db_from_dblp(conn, dblp_path):
    """
    Builds mysql-database from dblp.xml
    :param conn: database connection
    :param dblp_path: path to dblp.xml.gz
    """
    print("Parsing dblp data and feeding mysql database. This may take a while...")
    pk, pn, jkd, jnd, ckd, p, pa, pe = process_dblp_file(dblp_path)
    add_dblp_data_to_database(conn, pk, pn, jkd, jnd, ckd, p, pa, pe)
    print("All dblp data added to the database.")


def process_dblp_file(dblp_path):
    """
    Processes the dblp file. Important data will be loaded into memory to reduce the amount of SQL Statements.
    :param dblp_path: Path to the dblp.xml.gz
    """
    print("Processing dblp file...")

    journal_key_dict = {}
    journal_name_dict = {}
    conference_key_dict = {}
    publications = []
    person_authored = []
    person_edited = []
    person_keys = []
    person_names = {}

    context = etree.iterparse(gzip.GzipFile(os.path.join(dblp_path, "dblp.xml.gz")),
                              tag=("article", "masterthesis", "phdthesis", "inproceedings", "www"), load_dtd=True)
    bar = progressbar.ProgressBar(max_value=progressbar.UnknownLength)
    counter = 0

    for _, elem in context:
        counter += 1
        bar.update(counter)

        dblp_key = elem.get("key")
        type = elem.tag

        # Processing publications
        if elem.tag in ("article", "inproceedings", "masterthesis", "phdthesis"):
            title = elem.find("title").text if elem.find("title") is not None else None
            ee = elem.find("ee").text if elem.find("ee") is not None else None
            url = elem.find("url").text if elem.find("url") is not None else None
            year = int(elem.find("year").text) if elem.find("year") is not None else None
            volume = elem.find("volume").text if elem.find("volume") is not None else None
            conference_key = None
            journal_key = None

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
                        print("Error finding journal key for journal", journal)

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
                        print("Error finding conference key for journal", dblp_key)

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
                if person.text in person_names:
                    person_authored.append((person_names[person.text], dblp_key))

            # Adding editors to the publication
            for person in editors:
                if person.text in person_names:
                    person_edited.append((person_names[person.text], dblp_key))

        # Processing person records
        if elem.tag == "www":
            if dblp_key and dblp_key.startswith("homepages/"):
                person_keys.append((dblp_key,))

                # Add all available names to person record
                persons = elem.findall("author")
                for person in persons:
                    person_names[person.text] = dblp_key

                # Add institutions

        # Freeing the element since it is not needed anymore
        elem.clear()

    # Finishing the progressbar
    bar.finish()

    return person_keys, person_names, journal_key_dict, journal_name_dict, conference_key_dict, publications, person_authored, person_edited


def add_dblp_data_to_database(conn, person_keys, person_names, journal_key_dict, journal_name_dict, conference_key_dict,
                              publications, person_authored, person_edited):
    """
    Loads the dblp data from memory and inserts it as batches into the database
    :param conn: Connection to database
    :param person_keys: dblpKeys of Persons
    :param person_names: Names of Persons
    :param journal_key_dict: dblpKeys of journals
    :param journal_name_dict: Names of journals
    :param conference_key_dict: dblpKeys of conferences
    :param publications: Publications
    :param person_authored: Authors of publications
    :param person_edited: Editors of publications
    """
    print("\nInserting dblp data into the database...")
    print("Person keys:")
    cur = conn.cursor()
    with progressbar.ProgressBar(max_value=len(person_keys)) as bar:
        for i in range(0, len(person_keys), BATCH_SIZE):
            query = """INSERT INTO `person` (`dblpKey`) VALUES (%s)"""
            cur.executemany(query, person_keys[i:i + BATCH_SIZE])
            conn.commit()
            bar.update(i)

    print("Person names:")
    person_names_list = list(person_names.items())
    with progressbar.ProgressBar(max_value=len(person_names_list)) as bar:
        for i in range(0, len(person_names_list), BATCH_SIZE):
            query = """INSERT INTO `person_names` (`name`, `personKey`) VALUES (%s, %s)"""
            params = [tuple(el) for el in person_names_list[i: i + BATCH_SIZE]]
            cur.executemany(query, params)
            conn.commit()
            bar.update(i)

    print("Journals:")
    journal_key_dict_list = list(journal_key_dict.items())
    with progressbar.ProgressBar(max_value=len(journal_key_dict_list)) as bar:
        for i in range(0, len(journal_key_dict_list), BATCH_SIZE):
            query = """INSERT INTO `journal` (`dblpKey`, `acronym`) VALUES (%s, %s)"""
            params = [tuple(el) for el in journal_key_dict_list[i: i + BATCH_SIZE]]
            cur.executemany(query, params)
            conn.commit()
            bar.update(i)

    print("Journal names:")
    journal_name_dict_list = list(journal_name_dict.items())
    with progressbar.ProgressBar(max_value=len(journal_name_dict_list)) as bar:
        for i in range(0, len(journal_name_dict_list), BATCH_SIZE):
            query = """INSERT INTO `journal_name` (`name`, `journalKey`) VALUES (%s, %s)"""
            params = [tuple(el) for el in journal_name_dict_list[i: i + BATCH_SIZE]]
            cur.executemany(query, params)
            conn.commit()
            bar.update(i)

    print("Conferences:")
    conference_key_dict_list = list(conference_key_dict.items())
    with progressbar.ProgressBar(max_value=len(conference_key_dict_list)) as bar:
        for i in range(0, len(conference_key_dict_list), BATCH_SIZE):
            try:
                query = """INSERT INTO `conference` (`dblpKey`, `acronym`) VALUES (%s, %s)"""
                params = [tuple(el) for el in conference_key_dict_list[i: i + BATCH_SIZE]]
                cur.executemany(query, params)
                conn.commit()
            except mysql.connector.errors.IntegrityError:
                print(params)
            bar.update(i)

    print("Publications:")
    with progressbar.ProgressBar(max_value=len(publications)) as bar:
        for i in range(0, len(publications), BATCH_SIZE):
            query = """INSERT IGNORE INTO `publication` 
                    (`dblpKey`, `title`, `ee`, `url`, `year`, `volume`, `type`, `conference_dblpKey`, `journal_dblpKey`) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            cur.executemany(query, publications[i:i + BATCH_SIZE])
            conn.commit()
            bar.update(i)

    print("Authors of publications:")
    with progressbar.ProgressBar(max_value=len(person_authored)) as bar:
        for i in range(0, len(person_authored), BATCH_SIZE):
            query = """INSERT IGNORE INTO `person_authored_publication` (`personKey`, `publicationKey`) 
                    VALUES (%s, %s)"""
            cur.executemany(query, person_authored[i:i + BATCH_SIZE])
            conn.commit()
            bar.update(i)

    print("Editors of publications:")
    with progressbar.ProgressBar(max_value=len(person_edited)) as bar:
        for i in range(0, len(person_edited), BATCH_SIZE):
            query = """INSERT IGNORE INTO `person_edited_publication` (`personKey`, `publicationKey`) 
                            VALUES (%s, %s)"""
            cur.executemany(query, person_edited[i:i + BATCH_SIZE])
            conn.commit()
            bar.update(i)
    cur.close()


def add_inst_data(conn, inst_path):
    pass


def add_s2_data(conn, path):
    pass


def main():
    # Parsing command-line arguments
    parser = argparse.ArgumentParser(description="Bulding relational database from DBLP-xml file")
    parser.add_argument("-d", "--download", help="Download the current version of the DBLP")
    args = parser.parse_args()

    # Reading config file
    config = configparser.ConfigParser()
    config.read("config.ini")
    data_path = config["PATHS"]["DATA-PATH"]
    dblp_url = config["PATHS"]["DBLP-XML"]

    # Download data
    download = False
    if args.download:
        download = True
    if not os.path.exists(os.path.join(data_path, "dblp.xml.gz")):
        download = True
        print("DBLP file not available. Current version of DBLP will be downloaded.")
    if download:
        download_dblp(dblp_url, data_path)

    # Connect to database
    db_connection = DBConnection(
        config["DATABASE"]["HOST"],
        config["DATABASE"]["USER"],
        config["DATABASE"]["PASS"],
        config["DATABASE"]["DB"]
    )

    # Cleanup database
    cleanup_db(db_connection.db_connection)

    # Build database
    start = time.time()
    print("\n###############################\nStart %s\n###############################\n" % (time.ctime()))

    build_db_from_dblp(db_connection.db_connection, data_path)
    add_inst_data(db_connection.db_connection, data_path)
    add_s2_data(db_connection.db_connection, data_path)

    end = time.time()
    print("Time spent:", end - start, "s")


if __name__ == '__main__':
    main()
