import sqlite3
import pytest
from text_to_sql.adapters import SQLiteAdapter, SQLAlchemyAdapter

@pytest.fixture
def temp_db_path(tmp_path):
    db_file = tmp_path / "test.db"
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT);")
    cursor.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY, user_id INTEGER, amount REAL);")
    cursor.execute("INSERT INTO users (id, name, email) VALUES (1, 'Alice', 'alice@example.com'), (2, 'Bob', 'bob@example.com');")
    cursor.execute("INSERT INTO orders (id, user_id, amount) VALUES (10, 1, 99.99);")
    conn.commit()
    conn.close()
    return str(db_file)

def test_sqlite_adapter_schema(temp_db_path):
    adapter = SQLiteAdapter(temp_db_path)
    schema = adapter.get_schema()
    
    assert "Table: users" in schema
    assert "id (INTEGER)" in schema or "id" in schema
    assert "name (TEXT)" in schema or "name" in schema
    assert "Table: orders" in schema

def test_sqlite_adapter_query_success(temp_db_path):
    adapter = SQLiteAdapter(temp_db_path)
    result = adapter.execute_query("SELECT name, email FROM users ORDER BY name ASC;")
    
    assert result["success"] is True
    assert result["columns"] == ["name", "email"]
    assert len(result["data"]) == 2
    assert result["data"][0] == {"name": "Alice", "email": "alice@example.com"}
    assert result["data"][1] == {"name": "Bob", "email": "bob@example.com"}

def test_sqlite_adapter_query_failure(temp_db_path):
    adapter = SQLiteAdapter(temp_db_path)
    result = adapter.execute_query("SELECT * FROM non_existent_table;")
    
    assert result["success"] is False
    assert "error" in result
    assert "no such table" in result["error"]

def test_sqlalchemy_adapter_schema(temp_db_path):
    db_uri = f"sqlite:///{temp_db_path}"
    adapter = SQLAlchemyAdapter(db_uri)
    schema = adapter.get_schema()
    
    assert "Table: users" in schema
    assert "id (INTEGER)" in schema or "id" in schema
    assert "Table: orders" in schema

def test_sqlalchemy_adapter_query_success(temp_db_path):
    db_uri = f"sqlite:///{temp_db_path}"
    adapter = SQLAlchemyAdapter(db_uri)
    result = adapter.execute_query("SELECT name, email FROM users ORDER BY name ASC;")
    
    assert result["success"] is True
    assert result["columns"] == ["name", "email"]
    assert len(result["data"]) == 2
    assert result["data"][0] == {"name": "Alice", "email": "alice@example.com"}
    assert result["data"][1] == {"name": "Bob", "email": "bob@example.com"}

def test_sqlalchemy_adapter_query_failure(temp_db_path):
    db_uri = f"sqlite:///{temp_db_path}"
    adapter = SQLAlchemyAdapter(db_uri)
    result = adapter.execute_query("SELECT * FROM non_existent_table;")
    
    assert result["success"] is False
    assert "error" in result
