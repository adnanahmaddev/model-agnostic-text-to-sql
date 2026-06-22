import struct
import sys
from azure.identity import DefaultAzureCredential
from sqlalchemy import create_engine
from text_to_sql.adapters import SQLAlchemyAdapter

def main():
    print("Initializing Azure AD/Entra token credential...")
    try:
        credential = DefaultAzureCredential()
        # Request access token for Azure SQL
        token_obj = credential.get_token("https://database.windows.net/.default")
        token_bytes = token_obj.token.encode("utf-16-le")
        print("Successfully retrieved token from DefaultAzureCredential.")
    except Exception as e:
        print(f"Error acquiring Azure credential token: {e}", file=sys.stderr)
        print("Please make sure you are logged in (e.g., via 'az login') and your VPN is connected.", file=sys.stderr)
        sys.exit(1)

    # connection configuration
    driver = "ODBC Driver 17 for SQL Server"
    server = "fastcrib-dev-sql-001.database.windows.net,1433"
    database = "fastcrib-dev-sqldb-001"
    
    conn_str = f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    
    # SQL_COPT_SS_ACCESS_TOKEN = 1256 (pyodbc constant for setting the access token attribute)
    SQL_COPT_SS_ACCESS_TOKEN = 1256
    packed_token = struct.pack("=i", len(token_bytes)) + token_bytes

    print(f"Connecting to SQL Server: {server}...")
    try:
        # Create SQLAlchemy engine passing packed token in connection arguments
        engine = create_engine(
            f"mssql+pyodbc:///?odbc_connect={conn_str}",
            connect_args={"attrs_before": {SQL_COPT_SS_ACCESS_TOKEN: packed_token}}
        )
        
        # Instantiate SQLAlchemyAdapter with this engine
        adapter = SQLAlchemyAdapter(engine)
        
        # Test 1: Fetch metadata schema
        print("Reflecting schema (tables and columns)...")
        schema = adapter.get_schema()
        print("\n--- REFLECTED SCHEMA SAMPLE ---")
        lines = schema.split("\n")
        # Print the first 20 lines of schema to verify
        print("\n".join(lines[:20]))
        print("... (truncated) ...")
        
        # Test 2: Execute query via adapter
        query = "SELECT TOP 5 TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'awo' ORDER BY TABLE_NAME;"
        print(f"\nExecuting query: {query}")
        result = adapter.execute_query(query)
        
        print("\n--- QUERY RESULT ---")
        print(result)
        
        if result["success"]:
            print("\nDatabase connection test passed successfully!")
        else:
            print("\nQuery execution failed:", result.get("error"), file=sys.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"\nDatabase connection failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
