from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Sequence, TypeVar

from mysql.connector import Error
from mysql.connector.connection import MySQLConnection
from mysql.connector.pooling import MySQLConnectionPool


_ENV_LOADED = False
_POOL: MySQLConnectionPool | None = None
_T = TypeVar("_T")


@dataclass(frozen=True)
class DBConfig:
    host: str
    port: int
    user: str
    password: str
    database: str
    pool_name: str
    pool_size: int
    connect_timeout: int


def _load_env() -> None:
    global _ENV_LOADED
    if _ENV_LOADED:
        return

    backend_env = Path(__file__).resolve().parent / ".env"
    project_env = Path(__file__).resolve().parent.parent / ".env"

    _load_env_file(project_env)
    _load_env_file(backend_env)
    _ENV_LOADED = True


def _load_env_file(env_path: Path) -> None:
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if line.startswith("export "):
            line = line[len("export ") :].strip()

        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue

        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]

        os.environ.setdefault(key, value)


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def _get_int_env(name: str, default: int | None = None) -> int:
    raw_value = os.getenv(name)
    if raw_value is None or raw_value.strip() == "":
        if default is not None:
            return default
        raise ValueError(f"Missing required environment variable: {name}")

    try:
        return int(raw_value)
    except ValueError as exc:
        raise ValueError(f"Environment variable {name} must be an integer") from exc


def get_db_config() -> DBConfig:
    _load_env()
    return DBConfig(
        host=_require_env("OT_DB_HOST"),
        port=_get_int_env("OT_DB_PORT"),
        user=_require_env("OT_DB_USER"),
        password=_require_env("OT_DB_PASSWORD"),
        database=_require_env("OT_DB_NAME"),
        pool_name=os.getenv("OT_DB_POOL_NAME", "opentickets_pool"),
        pool_size=_get_int_env("OT_DB_POOL_SIZE", default=5),
        connect_timeout=_get_int_env("OT_DB_CONNECT_TIMEOUT", default=10),
    )


def _get_pool() -> MySQLConnectionPool:
    global _POOL
    if _POOL is not None:
        return _POOL

    cfg = get_db_config()
    _POOL = MySQLConnectionPool(
        pool_name=cfg.pool_name,
        pool_size=cfg.pool_size,
        pool_reset_session=True,
        host=cfg.host,
        port=cfg.port,
        user=cfg.user,
        password=cfg.password,
        database=cfg.database,
        connection_timeout=cfg.connect_timeout,
        autocommit=False,
    )
    return _POOL


def get_connection() -> MySQLConnection:
    return _get_pool().get_connection()


def _normalize_params(params: Sequence[Any] | None) -> Sequence[Any]:
    return () if params is None else params


def _execute_dict_query(
    query: str,
    params: Sequence[Any] | None,
    handler: Callable[[Any], _T],
) -> _T:
    connection = get_connection()
    try:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(query, _normalize_params(params))
            return handler(cursor)
    finally:
        connection.close()


def test_connection() -> bool:
    try:
        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                row = cursor.fetchone()
                return bool(row and row[0] == 1)
        finally:
            connection.close()
    except Error:
        return False


def fetch_all(query: str, params: Sequence[Any] | None = None) -> list[dict[str, Any]]:
    return _execute_dict_query(query, params, lambda cursor: list(cursor.fetchall()))


def fetch_one(query: str, params: Sequence[Any] | None = None) -> dict[str, Any] | None:
    return _execute_dict_query(query, params, lambda cursor: cursor.fetchone())


def execute_write(query: str, params: Sequence[Any] | None = None) -> int:
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, _normalize_params(params))
            connection.commit()
            return cursor.rowcount
    except Error:
        connection.rollback()
        raise
    finally:
        connection.close()