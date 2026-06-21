import re

class SafetyValidator:
    def __init__(self, read_only: bool = True, custom_blacklist: list = None):
        """
        Initialize SafetyValidator.
        
        :param read_only: If True, blocks any queries containing modifications.
        :param custom_blacklist: Custom list of forbidden SQL keywords (case-insensitive).
        """
        self.read_only = read_only
        self.blacklist = custom_blacklist if custom_blacklist is not None else [
            "insert", "update", "delete", "drop", "alter", "create", 
            "truncate", "replace", "grant", "revoke", "schema", "rename"
        ]

    def validate_and_sanitize(self, raw_sql: str) -> str:
        """
        Clean, parse, and validate safety checks on the SQL statement.
        
        :param raw_sql: The query returned by the LLM (which might contain markdown formatting).
        :return: Clean, sanitized SQL string.
        :raises PermissionError: If read-only mode is active and any forbidden keyword is matched.
        """
        # Strip markdown syntax (e.g., ```sql ... ``` or ``` ...)
        sql = raw_sql.strip()
        sql = re.sub(r"^```(?:sql)?\s*", "", sql, flags=re.IGNORECASE)
        sql = re.sub(r"\s*```$", "", sql)
        sql = sql.strip()
        
        # Safety check if read-only is enabled
        if self.read_only:
            sql_lower = sql.lower()
            
            for keyword in self.blacklist:
                # Search using word boundaries to catch keywords even inside comments
                if re.search(rf"\b{re.escape(keyword.lower())}\b", sql_lower):
                    raise PermissionError(
                        f"Safety Check Failed: SQL query contains prohibited keyword '{keyword}' under read-only mode."
                    )
                    
        # Strip comments from the final returned SQL statement
        sql_clean = re.sub(r"--.*", "", sql)
        sql_clean = re.sub(r"/\*.*?\*/", "", sql_clean, flags=re.DOTALL)
        return sql_clean.strip()
