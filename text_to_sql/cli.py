import sys
import os
import argparse
import struct
import json

from text_to_sql.adapters import SQLAlchemyAdapter
from text_to_sql.safety import SafetyValidator

# SQL Server credentials setup
from azure.identity import DefaultAzureCredential
from sqlalchemy import create_engine

def get_engine():
    # Retrieve Azure AD Token
    credential = DefaultAzureCredential()
    token_obj = credential.get_token("https://database.windows.net/.default")
    token_bytes = token_obj.token.encode("utf-16-le")
    
    driver = "ODBC Driver 17 for SQL Server"
    server = "fastcrib-dev-sql-001.database.windows.net,1433"
    database = "fastcrib-dev-sqldb-001"
    
    conn_str = f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    
    SQL_COPT_SS_ACCESS_TOKEN = 1256
    packed_token = struct.pack("=i", len(token_bytes)) + token_bytes
    
    engine = create_engine(
        f"mssql+pyodbc:///?odbc_connect={conn_str}",
        connect_args={"attrs_before": {SQL_COPT_SS_ACCESS_TOKEN: packed_token}}
    )
    return engine

def main():
    parser = argparse.ArgumentParser(description="Text-to-SQL Azure DB interface.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # get-schema command
    subparsers.add_parser("get-schema", help="Reflect database schema.")
    
    # validate command
    val_parser = subparsers.add_parser("validate", help="Validate safety rules on SQL query.")
    val_parser.add_argument("sql", help="The raw SQL query to validate.")
    
    # execute command
    exec_parser = subparsers.add_parser("execute", help="Sanitize, validate, and run SQL query.")
    exec_parser.add_argument("sql", help="The raw SQL query to run.")
    exec_parser.add_argument("--json", action="store_true", help="Output results in raw JSON format.")
    
    args = parser.parse_args()
    
    if args.command == "get-schema":
        try:
            engine = get_engine()
            adapter = SQLAlchemyAdapter(engine, schema="awo")
            schema = adapter.get_schema()
            print(schema)
        except Exception as e:
            print(f"Error fetching schema: {e}", file=sys.stderr)
            sys.exit(1)
            
    elif args.command == "validate":
        validator = SafetyValidator(read_only=True)
        try:
            clean_sql = validator.validate_and_sanitize(args.sql)
            print("Validation Passed. Clean SQL:")
            print(clean_sql)
        except Exception as e:
            print(f"Validation Failed: {e}", file=sys.stderr)
            sys.exit(1)
            
    elif args.command == "execute":
        validator = SafetyValidator(read_only=True)
        try:
            # 1. Sanitize & Validate
            clean_sql = validator.validate_and_sanitize(args.sql)
        except Exception as e:
            print(f"Validation Failed: {e}", file=sys.stderr)
            sys.exit(1)
            
        try:
            # 2. Connect & Execute
            engine = get_engine()
            adapter = SQLAlchemyAdapter(engine, schema="awo")
            result = adapter.execute_query(clean_sql)
            
            if not result["success"]:
                print(f"Query execution failed: {result.get('error')}", file=sys.stderr)
                sys.exit(1)
                
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                # Pretty print as a Markdown table
                columns = result["columns"]
                data = result["data"]
                
                if not columns:
                    print("Query executed successfully. No rows returned.")
                    return
                    
                # Header row
                header = "| " + " | ".join(columns) + " |"
                divider = "| " + " | ".join(["---"] * len(columns)) + " |"
                print(header)
                print(divider)
                
                # Data rows
                for row in data:
                    row_str = "| " + " | ".join(str(row.get(col, "")) for col in columns) + " |"
                    print(row_str)
        except Exception as e:
            print(f"Query execution error: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()
