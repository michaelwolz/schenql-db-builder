"""
This file downloads and builds the database for the schenql-query language
"""

import argparse
import configparser
import gzip
import os
import urllib.request
import re

import mysql.connector
from lxml import etree


class DBConnection:
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
    table_cur.execute("SET FOREIGN_KEY_CHECKS = 0")
    table_cur.execute("SHOW TABLES")
    for table in table_cur:
        print("TRUNCATE TABLE " + table[0])
        cur2.execute("TRUNCATE TABLE " + table[0])
    table_cur.execute("SET FOREIGN_KEY_CHECKS = 1")
    table_cur.close()
    cur2.close()
    print("Cleanup DONE!")


def build_db_from_dblp(conn, dblp_path):
    """
    Builds mysql-database from dblp.xml
    :param conn: database connection
    :param dblp_path: path to dblp.xml.gz
    """
    print("Parsing dblp data and feeding mysql database. This may take a while...")
    # Add all persons to db
    add_person_records_to_db(conn, dblp_path)
    print("All person records added to the database.")
    # Add publications to db
    add_publications_to_db(conn, dblp_path)
    print("All publications added to the database.")

    print("Building database DONE!")


def add_person_records_to_db(conn, dblp_path):
    """
    Parses the dblp file one time to extract all person-records (www-tags) and add them to the database
    :param conn: database connection
    :param dblp_path: path to the dblp.xml
    """
    print("Adding person records...")
    counter = 0
    cur = conn.cursor()
    context = etree.iterparse(gzip.GzipFile(os.path.join(dblp_path, "dblp.xml.gz")), tag="www", load_dtd=True)
    for _, elem in context:
        counter += 1
        if counter % 10000 == 0:
            print("Entry: ", counter)

        dblp_key = elem.get("key")
        if dblp_key and dblp_key.startswith("homepages/"):
            authors = elem.findall("author")
            # Trying to find orcid for author !!! DOESNT WORK SINCE orcid is not available in www-tag !!!
            # orcid = None
            # for author in authors:
            #     orcid = author.get("orcid")
            #     if orcid:
            #         break
            # if not orcid:
            #     orcid = None

            # Add person record to database
            query = """INSERT INTO `person` (`dblpKey`) VALUES (%s)"""
            cur.execute(query, (dblp_key,))
            conn.commit()

            # Add all available names to person record
            for author in authors:
                query = """INSERT INTO `person_names` (`name`, `personKey`) VALUES (%s, %s)"""
                cur.execute(query, (author.text, dblp_key))
                conn.commit()

            # Add institutions
        elem.clear()
    cur.close()


def add_publications_to_db(conn, dblp_path):
    """
    Parses the dblp file a second time and extracts all publications
    :param conn: database connection
    :param dblp_path: path to the dblp.xml
    """
    print("Adding publications...")
    counter = 0
    cur = conn.cursor()
    # TODO: Add master and phdthesises
    context = etree.iterparse(gzip.GzipFile(os.path.join(dblp_path, "dblp.xml.gz")),
                              tag=('article', 'inproceedings', 'proceedings'), load_dtd=True)
    for _, elem in context:
        counter += 1
        if counter % 10000 == 0:
            print("Entry: ", counter)

        dblp_key = elem.get('key')

        title = None
        ee = None
        url = None
        year = None
        conference_key = None
        journal_key = None
        volume = None

        if elem.find("title") is not None:
            title = elem.find("title").text
        if elem.find("ee") is not None:
            ee = elem.find("ee").text
        if elem.find("url") is not None:
            url = elem.find("url").text
        if elem.find("year") is not None:
            year = int(elem.find("year").text)
        if elem.find("volume") is not None:
            volume = elem.find("volume").text

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

                # Add journal to database if not exist
                query = """SELECT `dblpKey` from `journal` 
                        WHERE `dblpKey` = %s"""
                cur.execute(query, (journal_key,))
                result = cur.fetchone()
                if not result:
                    query = """INSERT INTO `journal` 
                            (`dblpKey`, `acronym`) 
                            VALUES (%s, %s)"""
                    cur.execute(query, (journal_key, acronym))
                    conn.commit()

                    # Check if journal name already exists otherwise add it
                    query = """SELECT `journalKey` from `journal_name` 
                            WHERE `journalKey` = %s AND `name` = %s"""
                    cur.execute(query, (journal_key, journal))
                    result = cur.fetchone()
                    if not result:
                        query = """INSERT INTO `journal_name` 
                                   (`name`, `journalKey`) 
                                   VALUES (%s, %s)"""
                        cur.execute(query, (journal, journal_key))
                        conn.commit()

        if elem.tag == "inproceedings" or elem.tag == "proceedings":
            conference_key = dblp_key.rsplit("/", 1)[0]

        authors = elem.findall("author")
        editors = elem.findall("editor")

        # Adding the publication to the database
        if dblp_key:
            query = """INSERT IGNORE INTO `publication` 
                    (`dblpKey`, `title`, `ee`, `url`, `year`, `volume`, `conference_dblpKey`, `journal_dblpKey`) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            cur.execute(query, (dblp_key, title, ee, url, year, volume, conference_key, journal_key))
            conn.commit()

            # Adding authors to the publication
            add_persons_to_publication(conn, cur, "author", authors, dblp_key)

            # Adding editors to the publication
            add_persons_to_publication(conn, cur, "editor", editors, dblp_key)

        elem.clear()
    cur.close()


def add_persons_to_publication(conn, cur, type, persons, dblp_key):
    """
    Connects a person record to a publication in the database
    :param conn: connection to database
    :param cur: cursor
    :param type: 'author' or 'editor'
    :param persons: list of persons to add
    :param dblp_key: dblp_key of the publication to connect to
    """
    for person in persons:
        query = """SELECT `dblpKey` FROM `person` 
                INNER JOIN `person_names` 
                ON `person_names`.`personKey` = `person`.`dblpKey`
                WHERE `person_names`.`name` = %s"""
        cur.execute(query, (person.text,))
        person_key = cur.fetchone()
        if person_key:
            person_key = person_key[0]
            if type == "author":
                query = """INSERT IGNORE INTO `person_authored_publication` (`personKey`, `publicationKey`) 
                        VALUES (%s, %s)"""
            elif type == "editor":
                query = """INSERT IGNORE INTO `person_edited_publication` (`personKey`, `publicationKey`) 
                        VALUES (%s, %s)"""
            cur.execute(query, (person_key, dblp_key))
            conn.commit()
        else:
            print("Error: Author or Editor not found in person table!")


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
    # cleanup_db(db_connection.db_connection)

    # Build database
    # build_db_from_dblp(db_connection.db_connection, data_path)
    add_inst_data(db_connection.db_connection, data_path)
    add_s2_data(db_connection.db_connection, data_path)


if __name__ == '__main__':
    main()
