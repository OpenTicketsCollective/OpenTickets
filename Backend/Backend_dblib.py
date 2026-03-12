from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Sequence, TypeVar

from dotenv import load_dotenv
from mysql.connector import Error, errorcode
from mysql.connector.connection import MySQLConnection
from mysql.connector.pooling import MySQLConnectionPool


#global variables for connection pool caching and environment loading
_POOL: MySQLConnectionPool | None = None
_ENV_LOADED = False


def _load_env() -> None:
    #load environment variables from .env file only once
    global _ENV_LOADED
    if _ENV_LOADED:
        return
    load_dotenv()
    _ENV_LOADED = True


def _get_pool() -> MySQLConnectionPool:
    #get or create the connection pool (lazy initialization)
    global _POOL
    if _POOL is not None:
        return _POOL
    
    #load environment variables
    _load_env()
    
    #initialize database connection parameters from environment variables
    db_host = os.getenv("OT_DB_HOST")
    db_port = int(os.getenv("OT_DB_PORT"))
    db_name = os.getenv("OT_DB_NAME")
    db_user = os.getenv("OT_DB_USER")
    db_password = os.getenv("OT_DB_PASSWORD")
    db_pool_name = os.getenv("OT_DB_POOL_NAME")
    db_pool_size = int(os.getenv("OT_DB_POOL_SIZE"))
    db_connect_timeout = int(os.getenv("OT_DB_CONNECT_TIMEOUT"))

    try:
        #create the connection pool
        _POOL = MySQLConnectionPool(
            pool_name=db_pool_name,
            pool_size=db_pool_size,
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name,
            connection_timeout=db_connect_timeout
        )
        return _POOL
    except Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your credentials, check your .env file")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist or is not accessible, check your .env file and docker setup")
        else:
            print(err)
        raise


def get_connection() -> MySQLConnection:
    #get a connection from the pool for use in queries
    return _get_pool().get_connection()

def execute_query(
    sql: str,
    params: Sequence[Any] | None = None,
) -> Sequence[Any]:
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params or (),  multi=True)
        results = cursor.fetchall() if cursor.with_rows else []
        # commit non-selects just in case the caller doesn't
        if not cursor.with_rows:
            conn.commit()
        return results
    finally:
        cursor.close()
        conn.close()

def get_user_by_ID(user_id):
    if not isinstance(user_id, int):
        raise TypeError(f"user_id must be int, got {type(user_id).__name__}")
    results = execute_query("SELECT first_name, last_name FROM User WHERE user_id = %s", (user_id,))
    if results:
        return results[0]
    return None
