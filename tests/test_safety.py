import pytest
from text_to_sql.safety import SafetyValidator

def test_markdown_code_block_stripping():
    validator = SafetyValidator()
    
    sql_with_block = "```sql\nSELECT * FROM users;\n```"
    assert validator.validate_and_sanitize(sql_with_block) == "SELECT * FROM users;"
    
    sql_plain_block = "```\nSELECT * FROM users;\n```"
    assert validator.validate_and_sanitize(sql_plain_block) == "SELECT * FROM users;"

def test_read_only_blocks_modifications():
    validator = SafetyValidator()
    
    with pytest.raises(PermissionError) as excinfo:
        validator.validate_and_sanitize("DROP TABLE users;")
    assert "Safety Check Failed" in str(excinfo.value)
    
    with pytest.raises(PermissionError):
        validator.validate_and_sanitize("DELETE FROM users WHERE id=1;")
        
    with pytest.raises(PermissionError):
        validator.validate_and_sanitize("INSERT INTO users (id) VALUES (1);")

def test_partial_match_allowed():
    validator = SafetyValidator()
    
    # "created_at" has "create"
    # "update_time" has "update"
    # "rename_flag" has "rename"
    sql = "SELECT created_at, update_time, rename_flag FROM users;"
    sanitized = validator.validate_and_sanitize(sql)
    assert sanitized == sql

def test_comment_stripping():
    validator = SafetyValidator()
    
    # Inline comment bypass attempt
    sql_inline = "SELECT * FROM users; -- delete from users"
    with pytest.raises(PermissionError):
        validator.validate_and_sanitize(sql_inline)
        
    # Block comment bypass attempt
    sql_block = "SELECT * FROM users; /* update users set role = 'admin' */"
    with pytest.raises(PermissionError):
        validator.validate_and_sanitize(sql_block)

def test_disabled_read_only():
    validator = SafetyValidator(read_only=False)
    
    # Allows modifications
    sql = "INSERT INTO users (name) VALUES ('Charlie');"
    assert validator.validate_and_sanitize(sql) == sql
