class PromptBuilder:
    def __init__(self, custom_instructions: str = None, dialect: str = "SQL"):
        """
        Initialize PromptBuilder.
        
        :param custom_instructions: Custom instructions/guidelines for the model.
        :param dialect: The SQL dialect of the target database (e.g. SQLite, PostgreSQL, Transact-SQL).
        """
        self.custom_instructions = custom_instructions
        self.dialect = dialect

    def build_prompt(self, user_query: str, schema: str) -> str:
        """
        Builds the prompt string to send to the LLM.
        
        :param user_query: The user's natural language question.
        :param schema: Reflected database schema string.
        :return: Completed prompt string.
        """
        instructions = self.custom_instructions
        if not instructions:
            instructions = (
                "1. Return ONLY the raw SQL query. Do not include markdown formatting (such as ```sql), code blocks, or explanations.\n"
                "2. The query must be read-only (SELECT statements only).\n"
                "3. Limit the results to a maximum of 100 rows unless specified otherwise."
            )
        
        return f"""You are an expert SQL translator. Your task is to convert the natural language query into a valid {self.dialect} query.

Database Schema:
{schema}

Instructions:
{instructions}

Natural Language Query:
"{user_query}"

{self.dialect} Query:"""
