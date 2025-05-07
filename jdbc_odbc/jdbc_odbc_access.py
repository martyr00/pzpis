import os
import time
import pyodbc
import jaydebeapi
import pandas as pd

BASE_DIR    = os.path.dirname(__file__)
JDBC_JAR    = os.path.join(BASE_DIR, "postgresql-42.7.5.jar")
JDBC_DRIVER = "org.postgresql.Driver"
JDBC_URL    = "jdbc:postgresql://localhost:6969/martyr"
USER        = "martyr"
PASSWORD    = "123321"

ODBC_CONN_STR = (
    "DRIVER=PostgreSQL;"
    "SERVER=localhost;"
    "PORT=6969;"
    "DATABASE=martyr;"
    "UID=martyr;"
    "PWD=123321"
)

def run_query(method: str, query: str):
    start = time.time()
    try:
        if method == "JDBC":
            conn = jaydebeapi.connect(
                JDBC_DRIVER, JDBC_URL, [USER, PASSWORD], JDBC_JAR
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
