from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from backend.agent.state import AgentState
from backend.mcp_server.cloudant_client import CloudantClient
from backend.app.config import get_settings

class CloudantAgent:
    """
    Cloudant Agent for handling queries about machine status, tickets, and inventory.
    Integrates with IBM Cloudant to retrieve and update structured technical data.
    """

    def __init__(self):
        """Initialize the Cloudant agent."""
        self.name = "Cloudant Agent"
        settings = get_settings()

        # Initialize LLM for synthesis and intent analysis
        self.llm = ChatOpenAI(
            openai_api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            model=settings.openai_model,
            temperature=0.1 # Very low temperature for data accuracy
        )

        # Initialize the database client
        self.db_client = CloudantClient()

        # Specialized prompt for database interaction
        self.system_prompt = """You are the Database Specialist for Field Mind.
Your goal is to provide accurate information about machines, inventory, and service tickets.

RULES:
1. Use the provided database results to answer the user's question.
2. If you are updating a ticket, confirm the change clearly.
3. If the requested record (machine ID or ticket ID) is not found, state that clearly.
4. Present data in clean tables or bullet points for technical clarity.
5. Only report facts found in the database; do not guess machine status."""

    def process(self, state: AgentState) -> dict:
        """
        Process a query using Cloudant database.
        Flow: Intent Analysis -> DB Retrieval -> Synthesis.
        """
        messages = state["messages"]
        last_message = messages[-1]
        user_query = last_message.content if hasattr(last_message, "content") else last_message.get("content", "")

        try:
            # 1. Intent Analysis: Use LLM to determine which DB operation is needed
            # In a full implementation, we'd use Tool Calling. For now, we'll use a targeted prompt.
            analysis_prompt = f"""{self.system_prompt}

            Analyze the user query and determine the intent:
            - 'machine': if they want details/status of a machine
            - 'inventory': if they are asking about parts or stock
            - 'ticket': if they are asking about a service ticket
            - 'unknown': otherwise

            Query: {user_query}
            Intent:"""

            intent_response = self.llm.invoke(analysis_prompt).content.strip().lower()

            # 2. DB Retrieval based on intent
            db_context = ""
            if "machine" in intent_response:
                # Try to find a potential machine ID in the query
                # Simple heuristic: looking for alphanumeric codes
                import re
                ids = re.findall(r'([A-Z0-9\-]{4,})', user_query)
                if ids:
                    res = self.db_client.get_document("machines", ids[0])
                    db_context = f"Machine Data for {ids[0]}: {str(res)}"
                else:
                    db_context = "No specific machine ID found in query to search."

            elif "inventory" in intent_response:
                # Use the query as a search term for inventory
                selector = {"name": {"$regex": user_query, "$options": "i"}}
                res = self.db_client.query_documents("inventory", selector)
                db_context = f"Inventory Search Results: {str(res)}"

            elif "ticket" in intent_response:
                import re
                ids = re.findall(r'([A-Z0-9\-]{4,})', user_query)
                if ids:
                    res = self.db_client.get_document("tickets", ids[0])
                    db_context = f"Ticket Data for {ids[0]}: {str(res)}"
                else:
                    db_context = "No specific ticket ID found in query to search."
            else:
                db_context = "The request did not clearly map to a database operation."

            # 3. Synthesis: Generate the final answer
            final_prompt = f"""{self.system_prompt}

DATABASE RESULTS:
{db_context}

USER QUERY: {user_query}

FINAL RESPONSE:"""

            response = self.llm.invoke(final_prompt)

            return {
                "messages": [{"role": "assistant", "content": response.content}]
            }

        except Exception as e:
            return {
                "messages": [{"role": "assistant", "content": f"Cloudant Agent Error: {str(e)}"}]
            }
