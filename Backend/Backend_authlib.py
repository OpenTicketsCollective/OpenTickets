from Backend_dblib import execute_query
from argon2 import PasswordHasher as ph
import base64
import hashlib
import time
import datetime
from os import urandom






def login_user(email, password):
    authuser= execute_query("Select user_id from User where email = %s", (email,))
    hashed = execute_query("SELECT password FROM User WHERE user_id = %s", (authuser,))
    if ph.verify(hashed, password):
        return True, authuser
    return False, None

def new_session(user_id, ip_address, user_agent):
    if not isinstance(user_id, int):
        raise TypeError(f"user_id must be int, got {type(user_id).__name__}")
    if not isinstance(ip_address, str):
        raise TypeError(f"ip_address must be str, got {type(ip_address).__name__}")
    if not isinstance(user_agent, str):
        raise TypeError(f"user_agent must be str, got {type(user_agent).__name__}")
    # Generate a random session token
    raw = urandom(128)
    token = base64.urlsafe_b64encode(raw).rstrip(b"=").decode()
    # Store the session in the database
    current_time = time.strftime('%Y-%m-%d %H:%M:%S')
    session_length = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time() + 14400))
    execute_query("INSERT INTO Sessions (session_id, user_id, session_token, created_time, expire_time, ip_address, user_agent_header)  VALUES (UUID(), %s, %s, %s, %s, %s, %s)", (user_id, token, current_time, session_length, ip_address, user_agent))
    return token

def validate_session(token, ip_address):
    if not isinstance(token, str):
        raise TypeError(f"token must be str, got {type(token).__name__}")
    if not isinstance(ip_address, str):
        raise TypeError(f"ip_address must be str, got {type(ip_address).__name__}")
    # Check if the session token exists and is valid
    session = execute_query("SELECT user_id, expire_time FROM Sessions WHERE session_token = %s AND ip_address = %s", (token, ip_address))
    if session:
        user_id, expire_time = session[0]['user_id'], session[0]['expire_time']
        if isinstance(expire_time, str):
            expire_time = datetime.datetime.strptime(expire_time, '%Y-%m-%d %H:%M:%S')
        if datetime.datetime.now() < expire_time:
            execute_query("UPDATE User SET last_login = %s WHERE user_id = %s", (time.strftime('%Y-%m-%d %H:%M:%S'), user_id))
            return True, user_id
    return False, None

def logout_session(token):
    execute_query("Update Sessions SET expire_time = %s WHERE session_token = %s", (time.strftime('%Y-%m-%d %H:%M:%S'), token))


def Checkauthlevel(user_id, permitted_access_levels):
    if not isinstance(user_id, int):
        raise TypeError(f"user_id must be int, got {type(user_id).__name__}")
    if isinstance(permitted_access_levels, str):
        permitted_access_levels = [permitted_access_levels]
    if not isinstance(permitted_access_levels, (list, tuple, set)):
        raise TypeError(f"permitted_access_levels must be list, tuple, or set, got {type(permitted_access_levels).__name__}")

    user_access_level = execute_query("SELECT access_level FROM User WHERE user_id = %s", (user_id,))
    if not user_access_level:
        return False, None

    access_level = user_access_level[0]['access_level']
    return access_level in permitted_access_levels, access_level


def create_user(token, ip_address, email, password, access_level, first_name, last_name, force_password_change):
    valid, requestedby = validate_session(token, ip_address)
    if not valid:
        # session invalid; reject the operation
        return False, "Invalid session"

    authorized, _ = Checkauthlevel(requestedby, ["Admin"])
    if not authorized:
        # user doesn't have permissions to create accounts; reject the operation
        return False, "Insufficient permissions"
    
    if execute_query("SELECT user_id FROM User WHERE email = %s", (email.lower(),)):
        # email already in use; reject the operation
        return False, "Email already in use"
    
    hashed_password = ph().hash(password)
    execute_query("INSERT INTO User (email, password, access_level, first_name, last_name, force_password_change) VALUES (%s, %s, %s, %s, %s, %s)",(email.lower(), hashed_password, access_level, first_name, last_name, force_password_change))
    return True, None

