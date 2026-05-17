from fastmcp import FastMCP
from backend.mcp_server.cloudant_client import CloudantClient
from backend.app.config import get_settings

# Initialize FastMCP server
mcp = FastMCP("FieldMind-Cloudant-Server")
settings = get_settings()
cloudant = CloudantClient()

@mcp.tool()
def get_machine_details(machine_id: str) -> str:
    """
    Retrieve detailed information about a specific machine.
    Use this when you have a machine ID and need its specs or status.
    """
    db = settings.cloudant_machines_db
    doc = cloudant.get_document(db, machine_id)
    if doc:
        return f"Machine Details for {machine_id}: {str(doc)}"
    return f"Machine with ID {machine_id} not found in {db}."

@mcp.tool()
def query_inventory(part_name: str) -> str:
    """
    Search for parts in the inventory.
    Use this to check if a part is in stock or to find its location.
    """
    db = settings.cloudant_inventory_db
    selector = {"name": {"$regex": part_name, "$options": "i"}}
    results = cloudant.query_documents(db, selector)

    if not results:
        return f"No parts matching '{part_name}' found in inventory."

    return f"Found {len(results)} matching items:\n" + "\n".join([str(r) for r in results])

@mcp.tool()
def check_ticket_status(ticket_id: str) -> str:
    """
    Retrieve the status and details of a specific service ticket.
    """
    db = settings.cloudant_tickets_db
    doc = cloudant.get_document(db, ticket_id)
    if doc:
        return f"Ticket {ticket_id} Status: {str(doc)}"
    return f"Ticket {ticket_id} not found."

@mcp.tool()
def update_ticket(ticket_id: str, status: str, notes: str) -> str:
    """
    Update a service ticket with a new status and technician notes.
    """
    db = settings.cloudant_tickets_db
    # Get existing doc to avoid overwriting other fields
    doc = cloudant.get_document(db, ticket_id)
    if not doc:
        return f"Cannot update ticket {ticket_id} because it does not exist."

    doc["status"] = status
    doc["notes"] = notes

    try:
        cloudant.upsert_document(db, ticket_id, doc)
        return f"Ticket {ticket_id} successfully updated to status: {status}."
    except Exception as e:
        return f"Failed to update ticket: {str(e)}"

if __name__ == "__main__":
    mcp.run()
