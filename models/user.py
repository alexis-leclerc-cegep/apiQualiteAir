from pydantic import BaseModel
import hashlib


class User(BaseModel):
    username: str
    password: str

    def hashPassword(self):
        return hashlib.sha256(self.password.encode()).hexdigest()
