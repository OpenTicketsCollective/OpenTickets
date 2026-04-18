# these are the backend API endpoints for the OpenTickets application alongside all the necessary imports and setup for the FastAPI.
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator
from Backend_authlib import login_user, new_session, validate_session, create_user, checkauthlevel, display_sessions, logout_session
import Backend_ticketlib
from Backend_dblib import execute_query

app = FastAPI()

# Custom exception handler to hide detailed validation errors (security: prevent info disclosure)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Invalid request data"}
    )
#This is the CORS middleware setup that allows the frontend application to communicate with the backend API without the program being blocked by CORS policy.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # Localhost
        "https://localhost",
        "https://127.0.0.1",
        "https://localhost:443",
        "https://127.0.0.1:443",
        # LAN IP
        "https://192.168.254.162",
        "https://192.168.254.162:443",
        # Legacy direct connections (if bypassing nginx)
        "https://localhost:5000",
        "https://127.0.0.1:5000",
        # HTTP fallback for development
        "http://localhost",
        "http://127.0.0.1",
        "http://localhost:5000",
        "http://127.0.0.1:5000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=3600,
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
    
    @field_validator('access_level')
    @classmethod
    def validate_access_level(cls, v):
        valid_levels = {'Admin', 'L1', 'L2', 'User'}
        if v not in valid_levels:
            raise ValueError(f"Invalid access_level. Must be one of: {', '.join(sorted(valid_levels))}")
        return v
class UserID(BaseModel):
    userId: int
class TicketCreate(BaseModel):
    title: str
    description: str
    priority_code: str
    token: str
    ip_address: str
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

# Dependencies (using authlib)
def get_current_user(request: Request):
    """Returns user_id if session is valid, otherwise raises 401"""
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing session token"
        )
    # Get client IP from X-Real-IP header (set by nginx) or fallback to request.client.host
    ip_address = request.headers.get("X-Real-IP", request.client.host)

    valid, user_id = validate_session(token, ip_address)
    if not valid or user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )
    return user_id


def require_admin(current_user: int = Depends(get_current_user)):
    """Requires Admin access - raises 403 if not admin"""
    authorized, _ = checkauthlevel(current_user, ["Admin"])
    if not authorized:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

# This is the function that creates a connection pool to the MySql database using the MySQLConnectionPool class from the mysql.connector library. It reads the database connection parameters from environment variables and handles errors that may occur during the connection process.
@app.post("/login")
def login(data: LoginData, request: Request):
    try:
        success, user_id = login_user(data.email, data.password)
        if not success:
            print(f"LOGIN FAILED for {data.email}")
            return {"status": False, "message": "Invalid email or password"}

        # Get client IP from X-Real-IP header (set by nginx) or fallback to request.client.host
        client_ip = request.headers.get("X-Real-IP", request.client.host)
        token = new_session(
            user_id,
            client_ip,
            request.headers.get("user-agent")
        )
        return {
            "status": True,
            "session_token": token,
            "user_id": user_id
        }
    except Exception as e:
        print(f"LOGIN ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {"status": False, "message": f"Error: {str(e)}"}
    
@app.post("/validate_session")
def validate_session_endpoint(data: TicketSession, request: Request):
    # Get client IP from X-Real-IP header (set by nginx) or fallback to request.client.host
    client_ip = request.headers.get("X-Real-IP", request.client.host)
    valid, user_id = validate_session(data.token, client_ip)
    if not valid or user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )
    return {"status": True,"user_id": user_id}

@app.post("/logout")
def logout(data: TicketSession):
    try:
        logout_session(data.token)
        print("[LOGOUT] Session invalidated successfully")
        return {"status": True, "message": "Logged out successfully"}
    except Exception as e:
        return {"status": False, "message": f"Error: {str(e)}"}

@app.post("/check-admin")
def check_admin(current_user: int = Depends(get_current_user)):
    """Check if current user has Admin access level"""
    try:
        is_admin, access_level = checkauthlevel(current_user, ["Admin"])
        return {"is_admin": is_admin, "access_level": access_level}
    except Exception as e:
        print("CHECK ADMIN ERROR:", e)
        raise HTTPException(status_code=500, detail="Internal server error")

#This is the function that allows admin members to view all users in the system by sending a request to the backend API that queries the database for all users and returns their information in a structured format.
@app.post("/admin/users")
def get_users(current_user: int = Depends(require_admin)):
    try:
        users = execute_query("""
            SELECT user_id, email, first_name, last_name, access_level
            FROM User
        """)
        return users or []
    except Exception as e:
        print("ADMIN USERS FETCH ERROR:", e)
        raise HTTPException(status_code=500, detail="Failed to fetch users")

#This is the function that allows admin members to create new users in the system by sending a request to the backend API with the necessary user information (email, password, access level, etc.) and the backend will handle the creation of the user in the database and return a success or failure message.
@app.post("/admin/createuser")
def admin_create_user(data: UserCreate, request: Request, current_user: int = Depends(require_admin)):
    try:
        # Get client IP from X-Real-IP header (set by nginx) or fallback to request.client.host
        client_ip = request.headers.get("X-Real-IP", request.client.host)
        success, msg = create_user(
            request.headers.get("Authorization"),
            client_ip,
            data.email,
            data.password,
            data.access_level,
            data.first_name,
            data.last_name,
            data.force_password_change
        )
        return {"status": success, "message": msg or "User created successfully"}
    except Exception as e:
        print("ADMIN CREATE USER ERROR:", e)
        raise HTTPException(status_code=500, detail="Server error creating user")


#This is the function that allows admin members to delete users from the system by sending a request to the backend API with the user ID of the user to be deleted and the backend will handle the deletion of the user from the database and return a success or failure message.
@app.post("/admin/deleteuser")
def delete_user(data: UserID, current_user: int = Depends(require_admin)):
    try:
        if data.userId == current_user:
            raise HTTPException(status_code=400, detail="Cannot delete your own account")

        execute_query("DELETE FROM User WHERE user_id = %s", (data.userId,))
        return {"status": True, "message": "User deleted successfully"}
    except Exception as e:
        print("DELETE USER ERROR:", e)
        raise HTTPException(status_code=500, detail="Failed to delete user")

#This is the function that allows admin members to reset a user's password by sending a request to the backend API with the user ID of the user whose password is to be reset and the backend will handle the password reset process (which may involve generating a new password, updating the database, and possibly sending an email to the user) and return a success or failure message.
@app.post("/admin/resetpassword")
def reset_password(data: UserID, current_user: int = Depends(require_admin)):

    return {
        "status": True,
        "message": "Password reset placeholder"
    }

#This is the function that allows admin members to view all active sessions in the system by sending a request to the backend API that queries the database for all active sessions and returns their information (such as session token, user ID, creation time, expiration time, etc.) in a structured format.
@app.post("/admin/sessions")
def get_sessions(request: Request, current_user: int = Depends(require_admin)):
    try:
        token = request.headers.get("Authorization")
        # Get client IP from X-Real-IP header (set by nginx) or fallback to request.client.host
        client_ip = request.headers.get("X-Real-IP", request.client.host)
        success, result = display_sessions(token, client_ip)
        
        if not success:
            # Check the error message to return appropriate HTTP status code
            if "Invalid session" in str(result):
                raise HTTPException(status_code=401, detail=result)
            elif "Insufficient permissions" in str(result):
                raise HTTPException(status_code=403, detail=result)
            else:
                raise HTTPException(status_code=400, detail=result)
        
        return result or []
    except HTTPException:
        raise
    except Exception as e:
        print("ADMIN SESSIONS FETCH ERROR:", e)
        raise HTTPException(status_code=500, detail="Failed to fetch sessions")
        
@app.post("/tickets/create")
def create_ticket(data: TicketCreate, request: Request):
    try:
        client_ip = request.headers.get("X-Real-IP", request.client.host)
        success, result = Backend_ticketlib.create_ticket(
            data.token,
            client_ip,
            data.title,
            data.description,
            data.priority_code
        )
        if success:
            return {"status": True, "ticket_uuid": result}
        return {"status": False, "message": result}
    except Exception as e:
        print("TICKET CREATION ERROR:", e)
        return{"status": False, "message": "Server Error"}


@app.post("/tickets/mytickets")
def get_my_tickets(data: TicketSession, request: Request):
    try:
        client_ip = request.headers.get("X-Real-IP", request.client.host)
        success, tickets = Backend_ticketlib.get_user_tickets(data.token, client_ip)
        if success:
            return tickets or []
        return []
    except Exception as e:
        print("TICKET FETCH ERROR:", e)
        return []
    
@app.post("/tickets/detail")
def get_ticket_detail(data: TicketDetailsRequest, request: Request):
    # Get client IP from X-Real-IP header (set by nginx) or fallback to request.client.host
    client_ip = request.headers.get("X-Real-IP", request.client.host)
    
    success, result = Backend_ticketlib.get_ticket_details(
        data.token,
        client_ip,
        data.ticket_uuid
    )
    
    if success:
        return {"success": True, "ticket": result["ticket"], "comments": result["comments"]}
    
    # Check the error message to return appropriate HTTP status code
    error_msg = str(result)
    if "Invalid session" in error_msg:
        raise HTTPException(status_code=401, detail=error_msg)
    elif "Insufficient permissions" in error_msg:
        raise HTTPException(status_code=403, detail=error_msg)
    elif "Ticket not found" in error_msg:
        raise HTTPException(status_code=404, detail=error_msg)
    else:
        raise HTTPException(status_code=400, detail=error_msg)
                
@app.post("/tickets/comment")
def add_comment(data: TicketComments, request: Request):
    # Get client IP from X-Real-IP header (set by nginx) or fallback to request.client.host
    client_ip = request.headers.get("X-Real-IP", request.client.host)
    try:
        success, msg = Backend_ticketlib.create_comment(
            data.token,
            client_ip,
            data.ticket_uuid,
            data.comment_text
        )
        if success:
            return {"success": True}
        return {"success": False, "message": msg}
    except HTTPException:
        raise
    except Exception as e:
        print("ADD COMMENT ERROR:", e)
        return {"success": False}
    
