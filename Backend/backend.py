# these are the backend API endpoints for the OpenTickets application alongside all the necessary imports and setup for the FastAPI.
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from Backend_authlib import login_user, new_session, validate_session, create_user
from Backend_dblib import execute_query

app = FastAPI()
#This is the CORS middleware setup that allows the frontend application to communicate with the backend API without the program being blocked by CORS policy.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5000",
        "http://localhost:5000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)
#These are the Pydantic models that define the expected structure of the data for the login, user creation, and user ID endpoint.
class LoginData(BaseModel):
    email: str
    password: str
class UserCreate(BaseModel):
    email: str
    first_name: str
    last_name: str
    password: str
    access_level: str
    force_password_change: bool = False
class UserID(BaseModel):
    userId: int
class TicketCreate(BaseModel):
    title: str
    description: str
class TicketSession(BaseModel):
    token: str
    ip_address: str
class TicketDetailsRequest(BaseModel):
    ticket_uuid: str
    token: str
    ip_address: str
class TicketComments(BaseModel):
    ticket_uuid: str
    ip_address: str
    token: str
    comment_text: str

# This is the function that creates a connection pool to the MySql database using the MySQLConnectionPool class from the mysql.connector library. It reads the database connection parameters from environment variables and handles errors that may occur during the connection process.
@app.post("/login")
def login(data: LoginData, request: Request):
    try:
        success, user_id = login_user(data.email, data.password)
    except Exception as e:
        print("LOGIN ERROR:", e)
        return {"status": False, "message": "Login failed"}
    if not success:
        return {"status": False, "message": "Invalid credentials"}
    try:
        token = new_session(
            user_id,
            request.client.host,
            request.headers.get("user-agent")
        )
    except Exception as e:
        print("SESSION ERROR:", e)
        return {"status": False, "message": "Session creation failed"}
    return {
        "status": True,
        "session_token": token,
        "user_id": user_id
    }

#This is the function that allows admin members to view all users in the system by sending a request to the backend API that queries the database for all users and returns their information in a structured format.
@app.get("/admin/users")
def get_users():
    try:
        users = execute_query("""
            SELECT user_id, email, first_name, last_name, access_level
            FROM User
        """)
    except Exception as e:
        print("USER FETCH ERROR:", e)
        return []
    return users

#This is the function that allows admin members to create new users in the system by sending a request to the backend API with the necessary user information (email, password, access level, etc.) and the backend will handle the creation of the user in the database and return a success or failure message.
@app.post("/admin/createuser")
def admin_create_user(data: UserCreate, request: Request):
    try:
        token = request.headers.get("Authorization")
        if not token:
            return {"status": False, "message": "Missing session token"}
        success, msg = create_user(
            token,
            request.client.host,
            data.email,
            data.password,
            data.access_level,
            data.first_name,
            data.last_name,
            data.force_password_change
        )
        return {
            "status": success,
            "message": msg
        }
    except Exception as e:
        print("CREATE USER ERROR:", e)
        return {
            "status": False,
            "message": "Server error creating user"
        }

#This is the function that allows admin members to delete users from the system by sending a request to the backend API with the user ID of the user to be deleted and the backend will handle the deletion of the user from the database and return a success or failure message.
@app.post("/admin/deleteuser")
def delete_user(data: UserID):
    try:
        execute_query(
            "DELETE FROM User WHERE user_id = %s",
            (data.userId,)
        )
    except Exception as e:
        print("DELETE ERROR:", e)
        return {"status": False}

    return {"status": True}

#This is the function that allows admin members to reset a user's password by sending a request to the backend API with the user ID of the user whose password is to be reset and the backend will handle the password reset process (which may involve generating a new password, updating the database, and possibly sending an email to the user) and return a success or failure message.
@app.post("/admin/resetpassword")
def reset_password(data: UserID):

    return {
        "status": True,
        "message": "Password reset placeholder"
    }

#This is the function that allows admin members to view all active sessions in the system by sending a request to the backend API that queries the database for all active sessions and returns their information (such as session token, user ID, creation time, expiration time, etc.) in a structured format.
@app.get("/admin/sessions")
def get_sessions():
    try:
        sessions = execute_query("""
            SELECT session_token AS session_id,
                   user_id,
                   created_time,
                   expire_time
            FROM Sessions
        """)
    except Exception as e:
        print("SESSION FETCH ERROR:", e)
        return []
    return sessions

@app.post("/tickets/create")
def create_ticket(data: TicketCreate):
        user_id = None
        if data.token:
            valid, user_id = validate_session(data.token, data.ip_address)
            if not valid:
                user_id = None
        try:
            execute_query(
                """
                INSERT INTO Tickets (ticket_name, ticket_description, created_by)
                VALUES (%s, %s, %s)
                """,
                (data.title, data.description, user_id)
            )

            return {"status": True}
        except Exception as e:
            print("TICKET CREATION ERROR:", e)
            return {"status": False}

@app.post("/tickets/mytickets")
def get_my_tickets(data: TicketSession):
    try:
        valid, user_id= validate_session(data.token, data.ip_address)
        if not valid:
            return []
        
        tickets = execute_query(
            "SELECT ticket_uuid, ticket_name, ticket_description FROM Tickets WHERE created_by = %s ORDER BY created_time DESC",
            (user_id,)
        )
        return tickets
    except Exception as e:
        print("TICKET FETCH ERROR:", e)
        return []
@app.post("/tickets/detail")
def get_ticket_detail(data: TicketDetailsRequest):

    try:
        valid, user_id = validate_session(data.token, data.ip_address)

        if not valid:
            return {"success": False}

        ticket = execute_query(
            """
            SELECT ticket_uuid, ticket_name, ticket_description, status
            FROM Tickets
            WHERE ticket_uuid = %s
            """,
            (data.ticket_uuid,)
        )

        comments = execute_query(
            "SELECT comment_text, created_time FROM TicketComments WHERE ticket_uuid = %s ORDER BY created_time",
            (data.ticket_uuid,)
        )

        if not ticket:
            return {"success": False}

        return {
            "success": True,
            "ticket": ticket[0],
            "comments": comments
        }

    except Exception as e:
        print("TICKET DETAIL ERROR:", e)
        return {"success": False}
@app.post("/tickets/comment")
def add_comment(data: TicketComments):

    try:
        valid, user_id = validate_session(data.token, data.ip_address)

        if not valid:
            return {"success": False}

        execute_query(
            """
            INSERT INTO TicketComments (ticket_uuid, comment_text, created_by)
            VALUES (%s,%s,%s)
            """,
            (data.ticket_uuid, data.comment_text, user_id)
        )

        return {"success": True}

    except Exception as e:
        print("COMMENT ERROR:", e)
        return {"success": False}
