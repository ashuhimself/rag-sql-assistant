import logging
import requests
from typing import List, Dict, Any, Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class OllamaClient:
    def __init__(self):
        self.base_url = settings.OLLAMA_URL
        self.model = settings.OLLAMA_MODEL
        self.session = requests.Session()

    def _make_request(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Make a request to Ollama API
        """
        try:
            url = f"{self.base_url}/api/generate"

            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "top_p": 0.9,
                    "num_predict": 500
                }
            }

            if system_prompt:
                payload["system"] = system_prompt

            response = self.session.post(url, json=payload, timeout=60)
            response.raise_for_status()

            result = response.json()
            return result.get('response', '').strip()

        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API request failed: {str(e)}")
            raise Exception(f"Failed to connect to Ollama: {str(e)}")
        except Exception as e:
            logger.error(f"Error in Ollama request: {str(e)}")
            raise

    def generate_sql(self, user_question: str, relevant_schemas: List[Dict[str, Any]]) -> str:
        """
        Generate SQL query based on user question and relevant schemas
        """
        system_prompt = """You are a SQL expert. Generate accurate, safe PostgreSQL queries based on the provided database schema and user questions.

Rules:
1. Only generate SELECT statements
2. Use proper PostgreSQL syntax
3. Include appropriate JOINs when needed
4. Use LIMIT to restrict results to reasonable numbers
5. Handle date/time comparisons properly
6. Use proper column names exactly as defined in schema
7. Return only the SQL query, no explanations"""

        # Format schema information
        schema_context = "\n\n".join([
            f"Table: {schema['table_name']}\n{schema['ddl_statement']}"
            for schema in relevant_schemas
        ])

        prompt = f"""Database Schema:
{schema_context}

User Question: {user_question}

Generate a PostgreSQL SELECT query to answer this question. Return only the SQL query:"""

        try:
            sql_query = self._make_request(prompt, system_prompt)

            # Clean up the response (remove markdown formatting if present)
            sql_query = sql_query.replace('```sql', '').replace('```', '').strip()

            # Basic validation
            if not sql_query.upper().startswith('SELECT'):
                logger.warning(f"Generated query doesn't start with SELECT: {sql_query}")

            return sql_query

        except Exception as e:
            logger.error(f"Error generating SQL: {str(e)}")
            raise Exception(f"Failed to generate SQL query: {str(e)}")

    def generate_response(self, user_question: str, sql_query: str, query_result: Dict[str, Any]) -> str:
        """
        Generate natural language response based on query results
        """
        system_prompt = """You are a helpful data analyst. Provide clear, concise answers to user questions based on SQL query results.

Rules:
1. Answer in natural language
2. Be specific with numbers and data
3. Keep responses under 200 words
4. If no results, explain why
5. Highlight key insights"""

        # Format the query result for the prompt
        if query_result.get('success', False):
            data = query_result.get('data', [])
            columns = query_result.get('columns', [])
            row_count = query_result.get('row_count', 0)

            if row_count == 0:
                result_text = "No results found."
            else:
                # Format first few rows for context
                result_text = f"Found {row_count} result(s).\n"
                if data and columns:
                    result_text += f"Columns: {', '.join(columns)}\n"
                    # Show first 3 rows as examples
                    for i, row in enumerate(data[:3]):
                        result_text += f"Row {i+1}: {dict(zip(columns, row))}\n"
                    if row_count > 3:
                        result_text += f"... and {row_count - 3} more rows"
        else:
            result_text = f"Query failed: {query_result.get('error', 'Unknown error')}"

        prompt = f"""User Question: {user_question}

SQL Query Used: {sql_query}

Query Results: {result_text}

Provide a helpful response to the user's question based on these results:"""

        try:
            response = self._make_request(prompt, system_prompt)
            return response

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"I found the data you requested, but encountered an error generating the response. The query returned {query_result.get('row_count', 0)} results."

    def generate_brief_response(self, user_question: str) -> str:
        """
        Generate brief response for non-database questions
        """
        system_prompt = """You are a database assistant. For non-database questions, provide very brief responses (under 50 words) and redirect to database-related topics."""

        prompt = f"""Question: {user_question}

This question doesn't seem to be about database queries. Provide a brief response and suggest asking about the banking database instead:"""

        try:
            response = self._make_request(prompt, system_prompt)
            # Ensure response is brief
            if len(response) > 200:
                response = response[:197] + "..."
            return response

        except Exception as e:
            logger.error(f"Error generating brief response: {str(e)}")
            return "I'm designed to help with database queries about banking data. Please ask about customers, accounts, transactions, loans, or other banking information."

    def test_connection(self) -> Dict[str, Any]:
        """
        Test connection to Ollama
        """
        try:
            response = self._make_request("Say 'Hello' if you can hear me.")
            return {
                'success': True,
                'message': 'Connected to Ollama successfully',
                'model': self.model,
                'response': response
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'model': self.model
            }