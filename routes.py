from fastapi import APIRouter, Depends

import hashlib
import os
import jwt
import sqlite3
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from datetime import datetime, timedelta

from models import message, user
from auth.bearer import JWTBearer

load_dotenv()

con = sqlite3.connect("test.sqlite")
cur = con.cursor()

SECRET_KEY = os.getenv("SECRET_KEY")

router = APIRouter()


@router.get("/", dependencies=[Depends(JWTBearer())])
async def root():
    return {"message": "Bienvenue à l'API de Qualité de l'Air"}


@router.get("/brokerIp", dependencies=[Depends(JWTBearer())])
async def broker_ip():
    return {"ip": "172.16.5.101"}


@router.post("/addToArchive", dependencies=[Depends(JWTBearer())])
async def add_to_archive(leMessage: message.Message):
    print(leMessage.data)
    print(leMessage)
    cur.execute("insert into logs (message, topic, created_at) values (?, ?, ?)", [leMessage.data, leMessage.data, datetime.now()])
    con.commit()
    return leMessage


@router.get("/getLogs", dependencies=[Depends(JWTBearer())])
async def get_logs():
    result = cur.execute('select * from logs')
    return result.fetchall()


@router.get("/getLatestCO2", dependencies=[Depends(JWTBearer())])
async def get_latest_co2():
    print("getLatestCO2")
    result = cur.execute("select message, created_at from logs "
                         "where topic = 'alexis/co2' "
                         "order by created_at desc "
                         "limit 1")
    column_names = [desc[0] for desc in cur.description]
    return zip(column_names, result.fetchone())


@router.get("/getLatestTVOC", dependencies=[Depends(JWTBearer())])
async def get_latest_tvoc():
    result = cur.execute("select message, created_at from logs "
                         "where topic = 'alexis/tvoc' "
                         "order by created_at desc "
                         "limit 1")
    column_names = [desc[0] for desc in cur.description]
    return zip(column_names, result.fetchone())


@router.get("/login")
async def login(utilisateur: user.User):
    # return jwt token
    try:
        username = utilisateur.username
        password = utilisateur.password
        
        # Hash password to compare with stored hash
        hashed_password = get_password_hash(password)

        # Query database for user credentials
        query = "SELECT username, password FROM users WHERE username = ?"
        result = cur.execute(query, [username]).fetchone()
        
        # Check if user exists and password matches
        if result and verify_password(password, result[1]):
            token = jwt.encode({
                'sub': username,
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(minutes=200)
            }, SECRET_KEY)
            return JSONResponse(status_code=200, content={"token": token})
        else:
            return JSONResponse(status_code=401, content={"message": "Wrong username or password"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_password_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password, hashed_password):
    print(plain_password)
    print(hashed_password)
    return get_password_hash(plain_password) == hashed_password


@router.post("/createUser")
async def create_user(utilisateur: user.User):
    try:
        username = utilisateur.username
        password = utilisateur.password
        hashed = get_password_hash(password)
        cur.execute("insert into users (username, password) values (?, ?)", [username, hashed])
        con.commit()
        # return that it worked
        return JSONResponse(status_code=200, content={"message": "User created"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
