from abc import ABC, abstractmethod
from typing import List, Dict, Any, Union
import sqlite3

class DatabaseAdapter(ABC):
    @abstractmethod
    def get_schema(self) -> str:
        """
        Extracts database schema (tables, columns, types).
        Returns a formatted schema representation suitable for the prompt.
        """
        pass

    @abstractmethod
    def execute_query(self, sql: str) -> dict:
        """
        Executes the SQL query against the database and returns a dictionary with execution results.
        Format:
        {
            "success": bool,
            "sql": str,
            "columns": List[str],      # column names (on success)
            "data": List[Dict[str, Any]], # rows as dictionary mapping column name -> value (on success)
            "error": str               # error message (on failure)
        }
        """
        pass

class SQLiteAdapter(DatabaseAdapter):
    def __init__(self, db_path: str):
        """
        Initialize SQLiteAdapter.
        
        :param db_path: Path to the SQLite database file.
        """
        self.db_path = db_path

    def get_schema(self) -> str:
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
            schema_lines = []
            for table in tables:
                cursor.execute(f"PRAGMA table_info({table});")
                columns = cursor.fetchall()
                col_strings = [f"{col[1]} ({col[2]})" for col in columns]
                schema_lines.append(f"Table: {table}\nColumns: {', '.join(col_strings)}")
            return "\n\n".join(schema_lines)
        finally:
            conn.close()

    def execute_query(self, sql: str) -> dict:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute(sql)
            description = cursor.description
            columns = [col[0] for col in description] if description else []
            rows = [dict(row) for row in cursor.fetchall()] if description else []
            return {
                "success": True,
                "sql": sql,
                "columns": columns,
                "data": rows
            }
        except Exception as e:
            return {
                "success": False,
                "sql": sql,
                "error": str(e)
            }
        finally:
            conn.close()

try:
    from sqlalchemy import create_engine, MetaData, text
    from sqlalchemy.engine import Engine
    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False

if HAS_SQLALCHEMY:
    class SQLAlchemyAdapter(DatabaseAdapter):
        def __init__(self, engine_or_uri: Union[Engine, str], schema: str = None):
            """
            Initialize SQLAlchemyAdapter.
            
            :param engine_or_uri: Either an active SQLAlchemy Engine instance or a connection URI string.
            :param schema: Optional database schema name to reflect.
            """
            if isinstance(engine_or_uri, str):
                self.engine = create_engine(engine_or_uri)
            else:
                self.engine = engine_or_uri
            self.schema = schema

        def get_schema(self) -> str:
            metadata = MetaData()
            if self.schema:
                metadata.reflect(bind=self.engine, schema=self.schema)
            else:
                metadata.reflect(bind=self.engine)
            schema_lines = []
            for table_name, table in metadata.tables.items():
                col_strings = [f"{col.name} ({col.type})" for col in table.columns]
                schema_lines.append(f"Table: {table_name}\nColumns: {', '.join(col_strings)}")
            return "\n\n".join(schema_lines)

        def execute_query(self, sql: str) -> dict:
            try:
                with self.engine.connect() as conn:
                    result = conn.execute(text(sql))
                    if result.returns_rows:
                        columns = list(result.keys())
                        rows = [dict(row._mapping) for row in result.fetchall()]
                        return {
                            "success": True,
                            "sql": sql,
                            "columns": columns,
                            "data": rows
                        }
                    else:
                        # DDL or modification queries (if read_only = False was specified)
                        conn.commit()
                        return {
                            "success": True,
                            "sql": sql,
                            "columns": [],
                            "data": [],
                            "rowcount": result.rowcount
                        }
            except Exception as e:
                return {
                    "success": False,
                    "sql": sql,
                    "error": str(e)
                }
else:
    class SQLAlchemyAdapter(DatabaseAdapter):
        def __init__(self, engine_or_uri: Any):
            raise ImportError("SQLAlchemy is not installed. Please install it to use SQLAlchemyAdapter.")

        def get_schema(self) -> str:
            pass

        def execute_query(self, sql: str) -> dict:
            pass
