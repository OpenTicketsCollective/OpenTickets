from Backend_dblib import execute_query
from Backend_authlib import validate_session


def create_ticket(token, ip_address, title, description):
	valid, requestedby = validate_session(token, ip_address)
	if not valid:
		# session invalid; reject the operation
		return False, "Invalid session"

	if not isinstance(title, str) or not isinstance(description, str):
		raise TypeError("title and description must both be strings")

	uuid_row = execute_query("SELECT UUID() AS ticket_uuid")
	if not uuid_row:
		return False, "Failed to generate ticket UUID"
	ticket_uuid = uuid_row[0]["ticket_uuid"]

	# session is valid; proceed with creating the ticket
	execute_query("INSERT INTO ActiveTickets (ticket_number, created_by, ticket_name, contains_flagged_url, ticket_description) VALUES (UUID_TO_BIN(%s), %s, %s, %s, %s)", (ticket_uuid, requestedby, title, 0, description))
	return True, ticket_uuid


