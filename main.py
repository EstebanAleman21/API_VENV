from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import secrets
from cryptography.fernet import Fernet

app = FastAPI()

# Simulación de base de datos para tokens
token_db = {}
key = Fernet.generate_key()
cipher_suite = Fernet(key)

class Token(BaseModel):
    token: str

class Message(BaseModel):
    token: str
    message: str

def validate_token(token: str):
    if token_db.get(token):
        return True
    else:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/token/", response_model=Token)
def create_token():
    new_token = secrets.token_urlsafe(16)
    token_db[new_token] = True
    return {"token": new_token}

@app.get("/token/{token}")
def validate_token_endpoint(token: str):
    validate_token(token)
    return {"token": token, "valid": True}

@app.delete("/token/{token}")
def delete_token(token: str):
    if validate_token(token):
        del token_db[token]
        return {"token": token, "valid": False}

@app.post("/encrypt/")
def encrypt_message(message: Message):
    if validate_token(message.token):
        encrypted_message = cipher_suite.encrypt(message.message.encode())
        return {"token": message.token, "encrypted_message": encrypted_message.decode()}

@app.post("/decrypt/")
def decrypt_message(message: Message):
    if validate_token(message.token):
        decrypted_message = cipher_suite.decrypt(message.message.encode())
        return {"token": message.token, "decrypted_message": decrypted_message.decode()}
