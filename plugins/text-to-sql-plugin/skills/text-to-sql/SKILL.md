---
name: text-to-sql
description: "Translate natural language questions into database SQL queries and execute them against the live Azure Database."
argument-hint: "natural language question"
---

# Text to SQL Integration Skill

Use this skill when you want to translate a natural language query into a database SQL query and run it on the live database.

## Prerequisites
1. **VPN**: Ensure you are connected to the corporate VPN.
2. **Environment**: Ensure a python environment with required database drivers (`pyodbc`, `sqlalchemy`) is active.

## Core Rules
- **Schema Discovery**: First run the `get-schema` command to inspect table structures, columns, and types before writing your SQL query.
- **Strict Read-Only**: The execution script strictly validates queries against SQL modification keywords (DROP, DELETE, UPDATE, INSERT, ALTER, etc.) and comment-based bypass attempts. Only SELECT queries are permitted.
- **Dialect**: The target database is Microsoft SQL Server (T-SQL). Ensure you generate query syntax compatible with MS SQL Server (e.g. use `TOP N` instead of `LIMIT N` to restrict rows).

## Commands

For running these commands, determine the path to the active python interpreter (e.g. `python` or virtualenv path) and run:

### 1. Retrieve Database Schema
```bash
python <skill-dir>/scripts/query_db.py get-schema
```

### 2. Validate Safety of Query
```bash
python <skill-dir>/scripts/query_db.py validate "YOUR SQL QUERY"
```

### 3. Execute Query
```bash
python <skill-dir>/scripts/query_db.py execute "YOUR SQL QUERY"
```
Or to return JSON:
```bash
python <skill-dir>/scripts/query_db.py execute "YOUR SQL QUERY" --json
```

## Workflow Guide
When you receive a natural language request (e.g., "how many assets exist?"):
1. Run the `get-schema` command to fetch the active database metadata.
2. Review table columns (e.g. `awo.Asset`, `awo.AssetTransaction`). Remember that table names in SQL are singular (like `awo.Asset`, not `awo.Assets`).
3. Construct the MS SQL Server compatible query (e.g. `SELECT COUNT(*) FROM awo.Asset;`).
4. Execute the query using the `execute` command.
5. Present the resulting Markdown table or JSON to the user cleanly without adding long explanations.
