import os
import sys
import json
from pathlib import Path
from typing import List

# Add project root to sys.path to allow imports from backend
root = Path(__file__).resolve().parents[1]
sys.path.append(str(root))

from backend.mcp_server.cloudant_client import CloudantClient
from backend.app.config import get_settings

def ingest_json_to_cloudant(file_path: Path, db_name: str, id_field: str):
    """
    Ingest data from a JSON file into a specific Cloudant database.
    """
    print(f"Starting ingestion for: {file_path} into database: {db_name}")

    if not file_path.exists():
        print(f"Error: File {file_path} not found.")
        return

    try:
        # Initialize the client FIRST
        client = CloudantClient()

        # Create database if it doesn't exist before ingesting
        client.create_database_if_not_exists(db_name)

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if not isinstance(data, list):
            print(f"Error: Expected a list of documents in {file_path}")
            return

        client = CloudantClient()
        count = 0

        for entry in data:
            # Extract ID for the document
            doc_id = entry.get(id_field)
            if not doc_id:
                print(f"Skipping entry missing {id_field}: {entry}")
                continue

            client.upsert_document(db_name, str(doc_id), entry)
            count += 1

        print(f"Successfully ingested {count} documents into {db_name}.")

    except Exception as e:
        print(f"An error occurred during ingestion of {file_path}: {e}")
        import traceback
        traceback.print_exc()

def main():
    settings = get_settings()

    # Mapping of files to databases and their respective unique ID fields
    ingestion_map = [
        {
            "file": Path("data/cloudant/machineRegistry.json"),
            "db": settings.cloudant_machines_db,
            "id_field": "machine_id"
        },
        {
            "file": Path("data/cloudant/partcatalogspermachine.json"),
            "db": settings.cloudant_inventory_db,
            "id_field": "part_id"
        },
        # Tickets JSON not found in current directory, but adding placeholder for future
        {
            "file": Path("data/cloudant/tickets.json"),
            "db": settings.cloudant_tickets_db,
            "id_field": "ticket_id"
        }
    ]

    for item in ingestion_map:
        ingest_json_to_cloudant(item["file"], item["db"], item["id_field"])

if __name__ == "__main__":
    main()
