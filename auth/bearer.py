from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os
from dotenv import load_dotenv
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta

app = FastAPI()

load_dotenv()


SECRET_KEY = os.getenv("SECRET_KEY")
bearer_token_scheme = HTTPBearer()


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        try:
            credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
            if credentials:
                if not credentials.scheme == "Bearer":
                    raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
                if not self.validate_jwt_token(credentials.credentials):
                    raise HTTPException(status_code=403, detail="Invalid token or expired token")
                return credentials.credentials
            else:
                raise HTTPException(status_code=403, detail="Invalid authorization code.")
        except InvalidTokenError:
            raise HTTPException(status_code=403, detail="Invalid token")

    def validate_jwt_token(self, token: str):
        # Decode the JWT token with the secret key
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

        print(decoded_token)

        # Check if the token has expired
        if datetime.utcfromtimestamp(decoded_token['exp']) < datetime.utcnow():
            raise HTTPException(status_code=401, detail='JWT token has expired')

        # Return the decoded token data
        return decoded_token
