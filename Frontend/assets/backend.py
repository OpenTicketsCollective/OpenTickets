from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# allows the admin page.html to communicate with the backend server which will be a middle man for communication with db
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


users = []
sessions = []

class UserCreate(BaseModel):
    email: str
    first_name: str
    last_name: str
    password: str
    access_level: str

class UserID(BaseModel):
    userId: int


@app.get("/admin/user")
def get_users():
    return users


@app.post("/admin/createuser")
def create_user(user: UserCreate):

    new_user = {
        "user_id": len(users) + 1,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": "staff",
        "access_level": user.access_level
    }

    users.append(new_user)

    return {"status": "user created", "user": new_user}


@app.post("/admin/deleteuser")
def delete_user(data: UserID):

    global users
    users = [u for u in users if u["user_id"] != data.userId]

    return {"status": "user deleted"}


@app.post("/admin/resetpassword")
def reset_password(data: UserID):

    return {"status": "password reset", "user": data.userId}


@app.get("/admin/sessions")
def get_sessions():
    return sessions