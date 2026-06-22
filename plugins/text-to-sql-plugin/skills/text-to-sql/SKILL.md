---
name: text-to-sql
description: "Translate natural language questions into database SQL queries and execute them against the live database."
argument-hint: "natural language question"
---

# Text to SQL Integration Skill

Use this skill when you want to translate a natural language query into a database SQL query and run it on a database.

## Prerequisites
1. **Installation**: Ensure the package is installed:
   ```bash
   pip install harness-agnostic-text-to-sql
   ```
2. **Database URI**: You must have the database connection URI or connection string (usually available in the environment as `DATABASE_URL` or provided by the user).

## Core Rules
- **Schema Discovery**: First run the `get-schema` command to inspect table structures, columns, and types before writing your SQL query.
- **Strict Read-Only**: The execution script strictly validates queries against SQL modification keywords (DROP, DELETE, UPDATE, INSERT, ALTER, etc.) and comment-based bypass attempts. Only SELECT queries are permitted.
- **Dialect**: Ensure you generate query syntax compatible with the target database dialect (e.g., SQLite, PostgreSQL, MS SQL Server). For MS SQL Server, use `TOP N` instead of `LIMIT N` to restrict rows.

## Commands

Execute these commands directly using the global command-line tool `text-to-sql-query` (or `python -m text_to_sql.cli` or `.venv/bin/text-to-sql-query` when running in virtual environments).

If `DATABASE_URL` is set in your environment, you do not need to provide the `--db-uri` / `-d` argument:

### 1. Retrieve Database Schema
```bash
text-to-sql-query get-schema --db-uri "YOUR_DATABASE_URI" [--schema "TARGET_SCHEMA"]
```

### 2. Validate Safety of Query
```bash
text-to-sql-query validate "YOUR SQL QUERY"
```

### 3. Execute Query
```bash
text-to-sql-query execute "YOUR SQL QUERY" --db-uri "YOUR_DATABASE_URI" [--schema "TARGET_SCHEMA"]
```
Or to return JSON:
```bash
text-to-sql-query execute "YOUR SQL QUERY" --db-uri "YOUR_DATABASE_URI" [--schema "TARGET_SCHEMA"] --json
```

## Workflow Guide
When you receive a natural language request (e.g., "how many assets exist?"):
1. Get the database connection URI (from `DATABASE_URL` environment variable or user input).
2. Run the `get-schema` command with the DB URI to fetch the active database metadata.
3. Review table columns (e.g. `awo.Asset`, `awo.AssetTransaction`).
4. Construct the query matching the database's SQL dialect.
5. Execute the query using the `execute` command.
6. Present the resulting Markdown table or JSON to the user cleanly.
