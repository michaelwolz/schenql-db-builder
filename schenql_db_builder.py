"""
This file downloads and builds the database for the schenql-query language
"""

import argparse
import configparser
import gzip
import os
import shutil
import urllib.request

import mysql.connector


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


def unzip_dblp(path):
    """
    Unzip the dblp since it is gzipped
    :param path: path to dblp.xml.gz
    """
    print("Extacting dblp.xml.gz...")
    with gzip.open(os.path.join(path, "dblp.xml.gz"), 'rb') as f_in:
        with open(os.path.join(path, "dblp.xml"), 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    print("Unzipping dblp.xml.gz DONE!")


def cleanup_db(conn):
    """
    Clean up the database for a new build
    :param conn: database connection
    """
    cur1 = conn.cursor(buffered=True)
    cur2 = conn.cursor()
    print("Cleaning up database...")
    cur1.execute("SET FOREIGN_KEY_CHECKS = 0")
    cur1.execute("SHOW TABLES")
    for table in cur1:
        print("TRUNCATE TABLE " + table[0])
        cur2.execute("TRUNCATE TABLE " + table[0])
    cur1.execute("SET FOREIGN_KEY_CHECKS = 1")
    cur1.close()
    cur2.close()
    print("Cleanup DONE!")


def build_db_from_dblp(conn, dblp_path):
    """
    Builds mysql-database from dblp.xml
    :param conn: database connection
    :param dblp_path: path to dblp.xml.gz
    """
    print("Parsing dblp data and feeding mysql databse. This may take a while...")
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

    # Download data
    download = False
    if args.download:
        download = True
    if not os.path.exists(os.path.join(config["PATHS"]["OUTPATH"], "dblp.xml")):
        download = True
        print("DBLP file not available. Current version of DBLP will be downloaded.")
    if download:
        download_dblp(config["PATHS"]["DBLP-XML"], config["PATHS"]["OUTPATH"])
        unzip_dblp(config["PATHS"]["OUTPATH"])

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
    build_db_from_dblp(db_connection.db_connection, config["PATHS"]["OUTPATH"])
    add_inst_data(db_connection.db_connection, config["PATHS"]["OUTPATH"])
    add_additional_data(db_connection.db_connection, config["PATHS"]["OUTPATH"])

    # Verify database


if __name__ == '__main__':
    main()
