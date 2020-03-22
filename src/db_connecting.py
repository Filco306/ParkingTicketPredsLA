import psycopg2
import os
import pandas as pd
import logging
import gc

logging.basicConfig(level=os.environ.get("LOGGING_LEVEL", "INFO"))


def get_postgis_conn():
    conn = psycopg2.connect(
        "dbname='postgres' user='{}' host='{}' password='postgres'".format(
            os.environ.get("POSTGRES_USER", ""), os.environ.get("DBHOST", "")
        )
    )
    return conn


def ingest_addresses(conn=None):
    if conn is None:
        conn = get_postgis_conn()
    chunksize = int(5e5)
    table = "ADDRESSES"
    cur = conn.cursor()
    for chunk in pd.read_csv(
        "Data/addresses-in-the-city-of-los-angeles.csv", chunksize=chunksize
    ):
        df = fill_nas(chunk)
        df_dict = df.to_dict(orient="records")
        cur.executemany(
            """INSERT INTO {}({}) VALUES ({})""".format(
                table,
                ",".join(list(df.columns)),
                "%(" + ")s,%(".join(list(df.columns)) + ")s",
            ),
            df_dict,
        )
        conn.commit()
        logging.info("Ingested {} addresses into the db".format(chunk.shape[0]))
    conn.close()


def ingest_raw_parkingtickets(conn=None):
    colmapping = {
        "Ticket number": "TICKETNUMBER",
        "Issue Date": "ISSUEDATE",
        "Issue time": "ISSUETIME",
        "Meter Id": "METERID",
        "Marked Time": "MARKEDTIME",
        "RP State Plate": "RPSTATEPLATE",
        "Plate Expiry Date": "PLATEEXPIRYDATE",
        "VIN": "VIN",
        "Make": "MAKE",
        "Body Style": "BODYSTYLE",
        "Color": "COLOR",
        "Location": "LOCATION",
        "Route": "ROUTE",
        "Agency": "AGENCYCODE",
        "Violation code": "VIOLATIONCODE",
        "Violation Description": "VIOLATIONDESC",
        "Fine amount": "FINEAMOUNT",
        "Latitude": "LATITUDE",
        "Longitude": "LONGITUDE",
        "Agency Description": "AGENCYDESCRIPTION",
        "Color Description": "COLORDESCRIPTION",
        "Body Style Description": "BODYSTYLEDESC",
    }
    if conn is None:
        conn = get_postgis_conn()
    chunksize = int(5e5)
    table = "PARKINGTICKET_RAW"
    cur = conn.cursor()
    max_to_insert = int(os.environ.get("MAX_TO_PROCESS", 1e9))
    count = 0
    for chunk in pd.read_csv("Data/parking-citations.csv", chunksize=chunksize):
        df = fill_nas(chunk.rename(colmapping, axis=1))
        df_dict = df.to_dict(orient="records")
        logging.info("Ingesting {} elements into the db".format(df.shape[0]))
        cur.executemany(
            """INSERT INTO {}({}) VALUES ({})""".format(
                table,
                ",".join(list(df.columns)),
                "%(" + ")s,%(".join(list(df.columns)) + ")s",
            ),
            df_dict,
        )
        conn.commit()
        gc.collect()
        logging.info("Ingested {} elements into the db".format(df.shape[0]))
        count += 1
        if max_to_insert < count * chunksize:
            break
    conn.close()
    # Now, this db


def get_all_between_dates(conn, startdate, enddate, limit=None):
    if limit is None:
        limit = int(10e9)
    limit = str(int(limit))
    with open("sql/get_all_between_dates.sql", "r") as f:
        sql = f.read().format(
            startdate=startdate.strftime("%Y-%m-%d"),
            enddate=enddate.strftime("%Y-%m-%d"),
            limit=limit,
        )
    df = pd.read_sql(sql, conn)
    df["exactissuingtime"] = df["exactissuingtime"].dt.tz_convert(None)
    return df


def get_per_location(conn, startdate, enddate, limit=None):
    if limit is None:
        limit = int(10e9)
    limit = str(int(limit))
    with open("sql/get_per_location.sql", "r") as f:
        sql = f.read().format(
            startdate=startdate.strftime("%Y-%m-%d"),
            enddate=enddate.strftime("%Y-%m-%d"),
            limit=limit,
        )
    return pd.read_sql(sql, conn)


def groupby(conn, cols, startdate, enddate, limit=None):
    if limit is None:
        limit = int(10e9)
    limit = str(int(limit))
    with open("sql/get_all_between_dates.sql", "r") as f:
        sql = f.read().format(
            startdate=startdate.strftime("%Y-%m-%d"),
            enddate=enddate.strftime("%Y-%m-%d"),
            cols=",".join(cols),
            limit=limit,
        )
    return pd.read_sql(sql, conn)


def fill_nas(df):
    logging.info("Filling NAs")
    df = df.where(pd.notnull(df), None)
    return df
