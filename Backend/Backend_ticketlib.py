from Backend_dblib import execute_query, get_user_by_ID
from Backend_authlib import validate_session, new_session


def create_ticket(token, ip_address, title, description, ):
    valid, requestedby = validate_session(token, ip_address)
    if not valid:
        # session invalid; reject the operation
        return False, "Invalid session"
    # session is valid; proceed with creating the ticket
    text = execute_query("START TRANSACTION;INSERT INTO ActiveTickets (created_by, ticket_name, contains_flagged_url) VALUES (%s, %s, %s);SELECT LAST_INSERT_ID();COMMIT;", (requestedby, title, 0))
    return True, text[1][0]['LAST_INSERT_ID()']

print(create_ticket("z-GLO1B8C-XUgrdxMeVgeAr0ciQW0xHeCzvD1-iPPI_TDdCcq9K4FW3NiDdTrScAwjC7UnY1HIHEkaIGp9pDBQV31pcaj2WDK9RsD2vY5pGAGs76mwGWwoWHgm7oq8O1u6zOaINMBtQMv1tGbyhoRzcPHEerm0-tSzuxWyQ18Fc", "127.0.0.1", "testing", "description"))