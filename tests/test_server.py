import tempfile
from pathlib import Path

import pytest

from mcp_server_starrocks.config import Config
from mcp_server_starrocks.server import StarRocksDatabase


def test_create_database_in_nonexistent_directory():
    """
    Ensure that when running in non-readonly mode, a missing directory
    can be created, and the database file is also created.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "subdir" / "test.db"
        config = Config(db_path=db_path, readonly=False)
        db = StarRocksDatabase(config)
        assert db_path.exists(), "Database file should be created automatically in non-readonly mode."
        # Optionally verify basic queries:
        db.execute_query("CREATE TABLE test (id INTEGER)")
        db.execute_query("INSERT INTO test VALUES (1)")
        result = db.execute_query("SELECT * FROM test")
        assert result == [(1,)], "Should be able to insert data when readonly=False."


def test_readonly_mode_missing_directory():
    """
    If the target directory does not exist and readonly=True,
    an exception should be raised.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "subdir" / "test.db"
        config = Config(db_path=db_path, readonly=True)
        # The directory 'subdir' does not exist, so it should raise an error.
        with pytest.raises(ValueError, match="Database directory does not exist"):
            StarRocksDatabase(config)


def test_readonly_mode_missing_db_file():
    """
    If the directory exists but the DB file itself does not exist and readonly=True,
    an exception should be raised.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        subdir = Path(tmpdir) / "subdir"
        subdir.mkdir(exist_ok=True)
        db_path = subdir / "test.db"
        config = Config(db_path=db_path, readonly=True)
        with pytest.raises(ValueError, match="Database file does not exist"):
            StarRocksDatabase(config)


def test_normal_mode_create_and_write():
    """
    In non-readonly mode, we should be able to create a table and perform write operations.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        config = Config(db_path=db_path, readonly=False)
        db = StarRocksDatabase(config)

        db.execute_query("CREATE TABLE users (id INTEGER, name VARCHAR)")
        db.execute_query("INSERT INTO users VALUES (1, 'Alice'), (2, 'Bob')")

        result = db.execute_query("SELECT * FROM users ORDER BY id")
        assert result == [(1, "Alice"), (2, "Bob")], "Data insertion in non-readonly mode should succeed."


def test_readonly_mode_write_query_error():
    """
    In readonly mode, attempting a write operation (INSERT) should raise an Error.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # First, create the database in writable mode
        db_path = Path(tmpdir) / "test.db"
        config_writable = Config(db_path=db_path, readonly=False)
        db_writable = StarRocksDatabase(config_writable)
        db_writable.execute_query("CREATE TABLE test (val INTEGER)")

        # Now open the same DB in readonly mode
        config_readonly = Config(db_path=db_path, readonly=True)
        db_readonly = StarRocksDatabase(config_readonly)

        # Attempting to write should fail
        with pytest.raises(Exception):
            db_readonly.execute_query("INSERT INTO test VALUES (42)")


def test_readonly_flag_behavior():
    """
    Tests behavior for readonly=True vs. readonly=False.

    1) readonly=False: should allow table creation and data insertion.
    2) readonly=True: should raise an error when attempting to insert data.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # 1) Writable configuration
        db_path_writable = Path(tmpdir) / "writable.db"
        config_writable = Config(db_path=db_path_writable, readonly=False)
        db_writable = StarRocksDatabase(config_writable)

        db_writable.execute_query("CREATE TABLE items (id INTEGER)")
        db_writable.execute_query("INSERT INTO items VALUES (100)")
        result = db_writable.execute_query("SELECT * FROM items")
        assert result == [(100,)], "Should successfully write when readonly=False"

        # 2) Readonly configuration
        db_path_readonly = Path(tmpdir) / "readonly.db"
        # Create the DB file in non-readonly mode first
        config_init = Config(db_path=db_path_readonly, readonly=False)
        StarRocksDatabase(config_init).execute_query("CREATE TABLE ro_test (val INTEGER)")

        # Reopen in readonly mode
        config_ro = Config(db_path=db_path_readonly, readonly=True)
        db_ro = StarRocksDatabase(config_ro)

        # Attempt to write should fail
        with pytest.raises(Exception):
            db_ro.execute_query("INSERT INTO ro_test VALUES (999)")

