import getpass
import bcrypt
import re

#This program will make the user create a password check it to meet the minimum requirements
#Then it will hash the password and print the hash to the user. The user can then use this hash to verify their password in the future.
def is_valid_password(password: str):
    if len(password) < 10:
        print("Password must be at least 10 characters long.")
        return False

    if not re.search(r"[A-Z]", password):
        print("Password must contain at least one uppercase letter.")
        return False

    if not re.search(r"[a-z]", password):
        print("Password must contain at least one lowercase letter.")
        return False

    if not re.search(r"\d", password):
        print("Password must contain at least one number.")
        return False

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        print("Password must contain at least one special character.")
        return False

    return True

#The retry prompt incase the password does not meet the requirements.
while True:
    password_input = getpass.getpass("Enter a password: ")

    if is_valid_password(password_input):
        print("Password accepted all the requirements met.")
        break
    else:
        print("Please try again.\n")

def hash_password(password: str):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode ('utf-8'), salt)

    print(f"Your hashed password is: {hashed_password.decode('utf-8')}")
    return hashed_password

hash_value = hash_password(password_input)
def verify_password(stored_hash, password: str):
    return bcrypt.checkpw(password.encode('utf-8'), stored_hash)

stored_hash = hash_value
password: str = getpass.getpass("Re-enter your password to verify: ")

if verify_password(stored_hash, password):
    print("Password verified successfully.")
else:
    print("Password verification failed.")