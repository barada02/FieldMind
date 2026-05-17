from typing import Any, Dict, List, Optional
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_cloud_sdk_core.api_exception import ApiException
from ibmcloudant.cloudant_v1 import CloudantV1
from backend.app.config import get_settings

class CloudantClient:
    """
    Client for IBM Cloudant to provide database operations for the MCP server.
    """
    def __init__(self):
        settings = get_settings()

        # Use IAM Authenticator if API key is provided
        if settings.cloudant_api_key:
            self.authenticator = IAMAuthenticator(settings.cloudant_api_key)
        else:
            # Fallback to username/password if provided
            self.authenticator = IAMAuthenticator(
                username=settings.cloudant_username,
                password=settings.cloudant_password
            )

        self.client = CloudantV1(authenticator=self.authenticator)
        self.client.set_service_url(settings.cloudant_url)

    def create_database_if_not_exists(self, db_name: str) -> None:
        """Ensure the specified database exists in Cloudant."""
        try:
            self.client.create_db(db=db_name).get_result()
            print(f"Successfully created database: {db_name}")
        except ApiException as e:
            if e.code == 412: # Conflict: Database already exists
                pass
            else:
                print(f"Warning: Could not create database {db_name}: {e}")

    def get_document(self, db_name: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific document by its ID."""
        try:
            return self.client.get_document(db=db_name, doc_id=doc_id).get_result()
        except ApiException as e:
            print(f"Error getting document {doc_id} from {db_name}: {e}")
            return None

    def query_documents(self, db_name: str, selector: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for documents using a selector query."""
        try:
            # Use the post_find method for flexible queries
            response = self.client.post_find(
                db=db_name,
                selector=selector
            ).get_result()

            return response.get("docs", [])
        except Exception as e:
            print(f"Error querying documents in {db_name}: {e}")
            return []

    def upsert_document(self, db_name: str, doc_id: str, document: Dict[str, Any]) -> Dict[str, Any]:
        """Insert or update a document."""
        try:
            return self.client.put_document(db=db_name, doc_id=doc_id, document=document).get_result()
        except ApiException as e:
            print(f"Error upserting document {doc_id} in {db_name}: {e}")
            raise e

    def list_documents(self, db_name: str, limit: int = 20) -> List[Dict[str, Any]]:
        """List documents in a database."""
        try:
            return self.client.get_all_documents(db=db_name).get_result()
        except ApiException as e:
            print(f"Error listing documents in {db_name}: {e}")
            return []
