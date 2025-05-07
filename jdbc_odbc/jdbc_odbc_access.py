import os
import time
import pyodbc
import jaydebeapi
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

JDBC_DRIVER = os.getenv("JDBC_DRIVER")
JDBC_URL    = os.getenv("JDBC_URL")
JDBC_JAR    = os.getenv("JDBC_JAR")

ODBC_CONN_STR = (
    f"DRIVER={os.getenv('ODBC_DRIVER')};"
    f"SERVER={os.getenv('ODBC_SERVER')};"
    f"PORT={os.getenv('ODBC_PORT')};"
    f"DATABASE={os.getenv('ODBC_DATABASE')};"
    f"UID={os.getenv('ODBC_UID')};"
    f"PWD={os.getenv('ODBC_PWD')}"
)

def run_query(method: str, query: str):
    start = time.time()
    try:
        if method == "JDBC":
            conn = jaydebeapi.connect(
                JDBC_DRIVER, JDBC_URL,
                [os.getenv("PG_USER"), os.getenv("PG_PASSWORD")],
                JDBC_JAR
            )
        elif method == "ODBC":
            conn = pyodbc.connect(ODBC_CONN_STR)
        else:
            raise ValueError("Incorrect connection type")

        curs = conn.cursor()
        curs.execute(query)
        rows    = curs.fetchall()
        columns = [desc[0] for desc in curs.description]

        df = pd.DataFrame.from_records(rows, columns=columns)

        curs.close()
        conn.close()
        duration = time.time() - start
        return df, duration, None

    except Exception as e:
        return None, None, str(e)
