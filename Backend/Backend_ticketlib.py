from Backend_dblib import execute_query
from Backend_authlib import validate_session, Checkauthlevel


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


def _can_access_ticket(requestedby, ticket_uuid):
	ticket_creator_row = execute_query("SELECT created_by FROM ActiveTickets WHERE ticket_number = UUID_TO_BIN(%s)", (ticket_uuid,))
	if not ticket_creator_row:
		return False, "Ticket not found"
	ticket_creator_id = ticket_creator_row[0]["created_by"]
	if requestedby == ticket_creator_id:
		return True, None
	authorized, _ = Checkauthlevel(requestedby, ["Admin", "L1", "L2"])
	if not authorized:
		return False, "Insufficient permissions"
	return True, None

def create_comment(token, ip_address, ticket_uuid, comment_text):
	valid, requestedby = validate_session(token, ip_address)
	if not valid:
		# session invalid; reject the operation
		return False, "Invalid session"

	has_access, access_error = _can_access_ticket(requestedby, ticket_uuid)
	if not has_access:
		return False, access_error

	if not isinstance(comment_text, str):
		raise TypeError("comment_text must be a string")

	# session is valid; proceed with creating the comment
	execute_query("INSERT INTO TicketComments (comment_number, ticket_number, created_by, comment_description, contains_flagged_url) VALUES (UUID_TO_BIN(UUID()), UUID_TO_BIN(%s), %s, %s, %s)", (ticket_uuid, requestedby, comment_text, 0))
	return True, "Comment created successfully"

def get_ticket_details(token, ip_address, ticket_uuid):
	valid, requestedby = validate_session(token, ip_address)
	if not valid:
		# session invalid; reject the operation
		return False, "Invalid session"

	has_access, access_error = _can_access_ticket(requestedby, ticket_uuid)
	if not has_access:
		return False, access_error

	# session is valid; proceed with fetching the ticket details
	ticket_details = execute_query("SELECT BIN_TO_UUID(ticket_number) AS ticket_uuid, created_by, ticket_name, contains_flagged_url, ticket_description, status_code, priority_code, create_time FROM ActiveTickets WHERE ticket_number = UUID_TO_BIN(%s)", (ticket_uuid,))
	if not ticket_details:
		return False, "Ticket not found"
	
	# Fetch all comments for this ticket
	comments = execute_query("SELECT BIN_TO_UUID(comment_number) AS comment_uuid, created_by, comment_description, create_time FROM TicketComments WHERE ticket_number = UUID_TO_BIN(%s) ORDER BY create_time ASC", (ticket_uuid,))
	
	return True, {
		"ticket": ticket_details[0],
		"comments": comments if comments else []
	}

def get_user_tickets(token, ip_address):
	valid, user_id = validate_session(token, ip_address)
	if not valid:
		# session invalid; reject the operation
		return False, "Invalid session"

	# Fetch all tickets created by this user
	tickets = execute_query("SELECT BIN_TO_UUID(ticket_number) AS ticket_uuid, created_by, ticket_name, ticket_description, status_code, priority_code, create_time FROM ActiveTickets WHERE created_by = %s ORDER BY create_time DESC", (user_id,))
	
	return True, tickets if tickets else []
