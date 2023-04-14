from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta

app = FastAPI()

# Define a JWT secret key (should be stored securely)
JWT_SECRET = 'my_secret_key'

# Define a bearer token scheme for FastAPI
bearer_token_scheme = HTTPBearer()

# Define a function to validate and decode JWT tokens

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials : HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            if not self.validate_jwt_token(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid token or expired token")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")
        # Get the token from the request

        # Validate and decode the token
        decoded_token = self.validate_jwt_token(token)

        # Add the decoded token data to the request state
        request.state.user = decoded_token['sub']

        return True
    def validate_jwt_token(self, token: str):
        try:
            # Decode the JWT token with the secret key
            decoded_token = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])

            # Check if the token has expired
            if decoded_token['exp'] < datetime.utcnow():
                raise HTTPException(status_code=401, detail='JWT token has expired')

            # Return the decoded token data
            return decoded_token
        except InvalidTokenError:
            raise HTTPException(status_code=401, detail='Invalid JWT token')


    async def authenticate_request(request: Request, token: HTTPAuthorizationCredentials = Depends(bearer_token_scheme)):
        # Validate and decode the JWT token
        decoded_token = validate_jwt_token(token.credentials)

        # Add the decoded token data to the request state
        request.state.user = decoded_token['sub']
