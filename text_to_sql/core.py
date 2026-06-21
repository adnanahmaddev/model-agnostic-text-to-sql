from typing import Callable
from text_to_sql.adapters import DatabaseAdapter
from text_to_sql.safety import SafetyValidator
from text_to_sql.prompts import PromptBuilder

class TextToSQL:
    def __init__(
        self,
        adapter: DatabaseAdapter,
        llm_callback: Callable[[str], str],
        safety_validator: SafetyValidator = None,
        prompt_builder: PromptBuilder = None
    ):
        """
        Initialize the TextToSQL manager.
        
        :param adapter: Concrete DatabaseAdapter instance.
        :param llm_callback: Function that takes a prompt string and returns the LLM response string.
        :param safety_validator: Custom SafetyValidator. Defaults to read-only validator if None.
        :param prompt_builder: Custom PromptBuilder. Defaults to standard builder if None.
        """
        self.adapter = adapter
        self.llm_call = llm_callback
        self.safety_validator = safety_validator if safety_validator is not None else SafetyValidator()
        self.prompt_builder = prompt_builder if prompt_builder is not None else PromptBuilder()

    def query(self, user_query: str) -> dict:
        """
        Translates a natural language user query to SQL, validates its safety,
        executes it, and returns the result metadata.
        
        :param user_query: Natural language query.
        :return: Execution results dictionary.
        """
        # 1. Reflect database schema
        schema = self.adapter.get_schema()
        
        # 2. Build the LLM prompt
        prompt = self.prompt_builder.build_prompt(user_query, schema)
        
        # 3. Call user's model completion function
        raw_sql = self.llm_call(prompt)
        
        # 4. Clean & sanitize SQL (run safety validations)
        try:
            sql = self.safety_validator.validate_and_sanitize(raw_sql)
        except PermissionError as pe:
            return {
                "success": False,
                "sql": raw_sql,
                "error": str(pe)
            }
            
        # 5. Run query on database
        result = self.adapter.execute_query(sql)
        
        # Merge prompt metadata for debuggability
        result["prompt"] = prompt
        return result
