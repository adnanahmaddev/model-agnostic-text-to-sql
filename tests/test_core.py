import sqlite3
import pytest
from text_to_sql.core import TextToSQL
from text_to_sql.adapters import SQLiteAdapter
from text_to_sql.prompts import PromptBuilder

@pytest.fixture
def temp_db(tmp_path):
    db_file = tmp_path / "core_test.db"
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE products (id INTEGER PRIMARY KEY, title TEXT, price REAL);")
    cursor.execute("INSERT INTO products (id, title, price) VALUES (1, 'Widget', 19.99), (2, 'Gizmo', 29.99);")
    conn.commit()
    conn.close()
    return str(db_file)

def test_core_translation_and_execution(temp_db):
    adapter = SQLiteAdapter(temp_db)
    
    received_prompts = []
    def mock_llm(prompt: str) -> str:
        received_prompts.append(prompt)
        return "SELECT title, price FROM products WHERE price > 20.0;"
        
    translator = TextToSQL(adapter, mock_llm)
    result = translator.query("Get products costing more than 20 dollars")
    
    assert result["success"] is True
    assert len(received_prompts) == 1
    assert "products" in received_prompts[0]
    assert "title" in received_prompts[0]
    
    assert result["columns"] == ["title", "price"]
    assert result["data"] == [{"title": "Gizmo", "price": 29.99}]
    assert "prompt" in result
    assert result["prompt"] == received_prompts[0]

def test_core_custom_prompt_builder(temp_db):
    adapter = SQLiteAdapter(temp_db)
    
    custom_pb = PromptBuilder(custom_instructions="CUSTOM INSTRUCTION HERE", dialect="SQLite")
    
    received_prompts = []
    def mock_llm(prompt: str) -> str:
        received_prompts.append(prompt)
        return "SELECT * FROM products;"
        
    translator = TextToSQL(adapter, mock_llm, prompt_builder=custom_pb)
    translator.query("All products")
    
    assert len(received_prompts) == 1
    assert "CUSTOM INSTRUCTION HERE" in received_prompts[0]
    assert "SQLite Query:" in received_prompts[0]

def test_core_safety_error_handling(temp_db):
    adapter = SQLiteAdapter(temp_db)
    
    def mock_malicious_llm(prompt: str) -> str:
        return "DROP TABLE products;"
        
    translator = TextToSQL(adapter, mock_malicious_llm)
    result = translator.query("Reset database")
    
    assert result["success"] is False
    assert "Safety Check Failed" in result["error"]
