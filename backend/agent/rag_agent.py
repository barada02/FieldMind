from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from backend.agent.state import AgentState
from backend.rag.vector_store import get_chroma_manager
from backend.app.config import get_settings

class RagAgent:
    """
    RAG Agent for handling queries about SOPs, manuals, and how-to guides.
    Integrates Jina AI embeddings and ChromaDB for document retrieval.
    """

    def __init__(self):
        """Initialize the RAG agent."""
        self.name = "RAG Agent"
        settings = get_settings()

        # Initialize LLM for synthesis
        self.llm = ChatOpenAI(
            openai_api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            model=settings.openai_model,
            temperature=0.2 # Lower temperature for higher accuracy in RAG
        )

        self.vector_store = get_chroma_manager()

        # Specialized RAG prompt
        self.system_prompt = """You are the RAG Specialist for Field Mind.
Your goal is to provide accurate technical guidance based ONLY on the provided context from Standard Operating Procedures (SOPs) and manuals.

RULES:
1. Use the provided context to answer the user's question.
2. If the context contains the answer, cite the document ID if available.
3. If the answer is NOT in the context, clearly state: "I cannot find the answer in the official documentation." Do NOT make up an answer.
4. Be concise, technical, and actionable.
5. Format lists as bullet points for clarity."""

    def process(self, state: AgentState) -> dict:
        """
        Process a query using RAG capabilities.
        Full implementation: Retrieval -> Contextualization -> Synthesis.
        """
        messages = state["messages"]
        last_message = messages[-1]
        user_query = last_message.content if hasattr(last_message, "content") else last_message.get("content", "")

        # 1. Retrieval: Get relevant chunks from ChromaDB
        try:
            results = self.vector_store.query_documents(
                query=user_query,
                n_results=5
            )

            context_docs = results.get("documents", [])
            metadatas = results.get("metadatas", [])

            # Construct context string
            if not context_docs:
                context_text = "No relevant documentation found in the vector store."
            else:
                context_parts = []
                for i, doc in enumerate(context_docs):
                    meta = metadatas[i] if i < len(metadatas) else {}
                    source = meta.get("source", "Unknown Source")
                    context_parts.append(f"--- Source: {source} ---\n{doc}")
                context_text = "\n\n".join(context_parts)

            # 2. Synthesis: Feed context and query to LLM
            rag_prompt = f"""{self.system_prompt}

CONTEXT FROM DOCUMENTATION:
{context_text}

USER QUERY: {user_query}

SOP RESPONSE:"""

            # We use a simple invoke here as the Orchestrator handles the overall graph state
            response = self.llm.invoke(rag_prompt)

            return {
                "messages": [{"role": "assistant", "content": response.content}]
            }

        except Exception as e:
            return {
                "messages": [{"role": "assistant", "content": f"RAG Agent Error: {str(e)}"}]
            }
