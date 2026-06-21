# Model-Agnostic Text-to-SQL

A production-grade, model-agnostic, and database-agnostic Python library that translates natural language queries into safe SQL statements and executes them against a database.

## Features

- **Database-Agnostic**: Works out of the box with standard SQLite databases (`SQLiteAdapter`) and any major database supported by SQLAlchemy (`SQLAlchemyAdapter`), including MS SQL Server, PostgreSQL, MySQL, Oracle, etc.
- **Model-Agnostic**: Decouples prompt formulation from specific LLM vendors (OpenAI, Gemini, Anthropic, etc.). You simply pass a callback function that handles the model text completion.
- **Strict Safety Layer**: Enforces query rules (such as read-only SELECT constraints), sanitizes markdown blocks, scrubs comments, and protects against DDL/DML injection keywords (e.g. `DROP`, `DELETE`, `UPDATE`, `ALTER`).

---

## Installation

You can install the stable release directly from [PyPI](https://pypi.org/project/model-agnostic-text-to-sql/):

```bash
pip install model-agnostic-text-to-sql
```

For local development or installing from source:

```bash
# Clone the repository
git clone https://github.com/adnanahmaddev/model-agnostic-text-to-sql.git
cd model-agnostic-text-to-sql

# Install in editable mode
pip install -e .
```

---

## Getting Started

### 1. Basic SQLite Example (Model-Agnostic Callback)

```python
import sqlite3
from text_to_sql import TextToSQL, SQLiteAdapter

# Initialize a demo database
conn = sqlite3.connect("demo.db")
conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, role TEXT);")
conn.execute("INSERT INTO users VALUES (1, 'Alice', 'Admin'), (2, 'Bob', 'User');")
conn.commit()
conn.close()

# 1. Define your custom LLM callback
def gemini_or_openai_callback(prompt: str) -> str:
    # Connect to your preferred model SDK here (e.g. Gemini, OpenAI, Claude)
    # response = client.generate_content(prompt)
    # return response.text
    return "SELECT name FROM users WHERE role = 'Admin';"

# 2. Instantiate adapter and query
adapter = SQLiteAdapter("demo.db")
translator = TextToSQL(adapter, gemini_or_openai_callback)

result = translator.query("Get the names of all admin users")
print(result)
# Output:
# {
#     'success': True,
#     'sql': 'SELECT name FROM users WHERE role = \'Admin\';',
#     'columns': ['name'],
#     'data': [{'name': 'Alice'}]
# }
```

### 2. Live Azure SQL Server Connection Example (Active Directory/Entra Token)

If you are querying a secure corporate database like Microsoft SQL Server using Entra ID token authentication (e.g., Azure SQL DB), you can pass a configured SQLAlchemy engine:

```python
import struct
from azure.identity import DefaultAzureCredential
from sqlalchemy import create_engine
from text_to_sql import TextToSQL, SQLAlchemyAdapter

# 1. Retrieve the Entra ID active token
credential = DefaultAzureCredential()
token_obj = credential.get_token("https://database.windows.net/.default")
token_bytes = token_obj.token.encode("utf-16-le")

# 2. Setup your SQL Server connection properties
driver = "ODBC Driver 17 for SQL Server"
server = "your-sql-server.database.windows.net,1433"
database = "your-database-db"
conn_str = f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"

# SQL_COPT_SS_ACCESS_TOKEN = 1256 (pyodbc constant for setting the access token)
SQL_COPT_SS_ACCESS_TOKEN = 1256
packed_token = struct.pack("=i", len(token_bytes)) + token_bytes

# 3. Create the SQLAlchemy Engine
engine = create_engine(
    f"mssql+pyodbc:///?odbc_connect={conn_str}",
    connect_args={"attrs_before": {SQL_COPT_SS_ACCESS_TOKEN: packed_token}}
)

# 4. Initialize adapter (target schema 'awo')
adapter = SQLAlchemyAdapter(engine, schema="awo")

# 5. Define LLM callback
def llm_callback(prompt: str) -> str:
    # Your model call goes here
    return "SELECT TOP 3 * FROM awo.Asset;"

# 6. Execute query
translator = TextToSQL(adapter, llm_callback)
result = translator.query("Get first 3 assets")
print(result)
```

---

## Security & Safety

The `SafetyValidator` intercepts query executions and validates safety constraints:

- By default, it operates in `read_only=True` mode, blocking any modification queries (`INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `TRUNCATE`, `REPLACE`, `GRANT`, `REVOKE`, `SCHEMA`, `RENAME`).
- Regular expression keyword validation uses word boundaries (`\b`) to ensure column names containing keywords (e.g. `created_at` or `update_flag`) are not false-positives.
- Comments (single-line `--` and multi-line `/* */`) are cleaned from the returned statement, and searched for keywords to prevent injection bypasses.

---

## Running Tests

Tests are written using `pytest`. To run the test suite:

```bash
# Install test requirements
pip install -e ".[test]"

# Execute tests
PYTHONPATH=. pytest -v
```

---

## Antigravity Agent Plugin Integration

This repository includes a custom **Plugin & Skill** wrapper for Antigravity-supported IDE environments.

### 1. Global Installation (IDE-wide)
To expose this skill to all local workspace agents globally:
1. Clone this repository:
   ```bash
   git clone https://github.com/adnanahmaddev/model-agnostic-text-to-sql.git
   ```
2. Copy or symlink the `plugins/text-to-sql-plugin` directory to your local configuration folder:
   ```bash
   ln -s "$(pwd)/plugins/text-to-sql-plugin" ~/.gemini/config/plugins/text-to-sql-plugin
   ```

### 2. Repository-level Installation (Recommended for Teams)
If you want to commit the skill configuration directly into your project repository:
1. Create a directory `.agents/skills/text-to-sql/` inside your target project repository.
2. Download or copy the [SKILL.md](plugins/text-to-sql-plugin/skills/text-to-sql/SKILL.md) file directly into that directory:
   ```bash
   mkdir -p .agents/skills/text-to-sql
   curl -o .agents/skills/text-to-sql/SKILL.md https://raw.githubusercontent.com/adnanahmaddev/model-agnostic-text-to-sql/main/plugins/text-to-sql-plugin/skills/text-to-sql/SKILL.md
   ```
3. Register it in your repository's local `AGENTS.md` file:
   ```markdown
   | Skill | Path | When To Use |
   |---|---|---|
   | `text-to-sql` | `.agents/skills/text-to-sql/` | Translate natural language queries into SQL and query the database |
   ```
