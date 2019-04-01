"""
This file downloads and builds the database for the schenql-query language
"""

import argparse
import configparser
import gzip
import os
import urllib.request

import mysql.connector
from lxml import etree


class DBConnection:
    def __init__(self, host, user, passwd, db):
        self.db_connection = mysql.connector.connect(host=host, user=user, passwd=passwd, database=db)

    def __del__(self):
        self.db_connection.close()


def download_dblp(url, outpath):
    """
    Downloading the dblp.xml.gz to the specified outpath for further processing
    :param url: URL to the dblp.xml.gz file (probably: https://dblp.uni-trier.de/xml/dblp.xml.gz)
    :param outpath: Path where the dblp.xml.gz file is saved to
    """
    print("Downloading dblp.xml.gz...")
    urllib.request.urlretrieve(url, os.path.join(outpath, "dblp.xml.gz"))
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
    print("Parsing dblp data and feeding mysql databse. This may take a while...")
    context = etree.iterparse(gzip.GzipFile(os.path.join(dblp_path, "dblp.xml.gz")))
    for action, elem in context:
        print("%s: %s" % (action, elem.tag))
    print("Building database DONE!")
    pass


def add_inst_data(conn, inst_path):
    pass


def add_additional_data(conn, path):
    pass


def main():
    # Parsing command-line arguments
    parser = argparse.ArgumentParser(description="Bulding relational database from DBLP-xml file")
    parser.add_argument("-d", "--download", help="Download the current version of the DBLP")
    args = parser.parse_args()

    # Reading config file
    config = configparser.ConfigParser()
    config.read("config.ini")
    outpath = config["PATHS"]["OUTPATH"]
    dblp_url = config["PATHS"]["DBLP-XML"]

    # Download data
    download = False
    if args.download:
        download = True
    if not os.path.exists(os.path.join(outpath, "dblp.xml.gz")):
        download = True
        print("DBLP file not available. Current version of DBLP will be downloaded.")
    if download:
        download_dblp(dblp_url, outpath)

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
    build_db_from_dblp(db_connection.db_connection, outpath)
    add_inst_data(db_connection.db_connection, outpath)
    add_additional_data(db_connection.db_connection, outpath)

    # Verify database


if __name__ == '__main__':
    main()
