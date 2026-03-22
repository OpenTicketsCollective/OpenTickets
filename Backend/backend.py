from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from Backend_authlib import login_user, new_session, validate_session, create_user
from Backend_dblib import execute_query

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.post("/admin/resetpassword")
def reset_password(data: UserID):

    return {
        "status": True,
        "message": "Password reset placeholder"
    }

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