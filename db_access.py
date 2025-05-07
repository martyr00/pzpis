import time
import mysql.connector
import psycopg2
from mysql.connector import Error as MySQLError
from psycopg2 import DatabaseError as PGError

MYSQL_CONFIG = {
    "host":     "localhost",
    "port":     9696,
    "user":     "root",
    "password": "",
    "database": "music_app",
}

PG_CONFIG = {
    "host":     "localhost",
    "port":     6969,
    "user":     "martyr",
    "password": "123321",
}

def connect_mysql():
    return mysql.connector.connect(**MYSQL_CONFIG)

def connect_postgresql():
    return psycopg2.connect(**PG_CONFIG)

def run_single_query(db_type: str, query: str):
    start = time.time()
    if db_type == "MySQL":
        conn = connect_mysql()
    elif db_type == "PostgreSQL":
        conn = connect_postgresql()
    else:
        raise ValueError(f"Unknown database type: {db_type}")

    try:
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description] if cur.description else []
        exec_time = time.time() - start
        return rows, cols, exec_time
    finally:
        cur.close()
        conn.close()

def distributed_transaction(mysql_query: str, mysql_table: str,
                            pg_query: str, pg_table: str):
    m_conn = connect_mysql()
    p_conn = connect_postgresql()
    m_cur = m_conn.cursor()
    p_cur = p_conn.cursor()

    start = time.time()
    try:
        m_conn.start_transaction()
        p_conn.autocommit = False

        m_cur.execute(mysql_query)
        p_cur.execute(pg_query)

        m_conn.commit()
        p_conn.commit()

        m_cur.execute(f"SELECT * FROM {mysql_table}")
        m_rows = m_cur.fetchall()
        m_cols = [d[0] for d in m_cur.description]

        p_cur.execute(f"SELECT * FROM {pg_table}")
        pg_rows = p_cur.fetchall()
        pg_cols = [d[0] for d in p_cur.description]

        exec_time = time.time() - start
        return {
            "mysql":      (m_rows, m_cols),
            "postgresql": (pg_rows, pg_cols),
        }, exec_time

    except (MySQLError, PGError) as e:
        m_conn.rollback()
        p_conn.rollback()
        raise
    finally:
        m_cur.close()
        m_conn.close()
        p_cur.close()
        p_conn.close()
