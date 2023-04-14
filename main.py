import os
import sqlite3
from dotenv import load_dotenv
from datetime import datetime

from fastapi import FastAPI
from fastapi_mqtt import FastMQTT, MQTTConfig

import routes

app = FastAPI()

app.include_router(routes.router)

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGO = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 2000

# TODO : Utiliser le token bin comme y faut
# https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/

mqtt_config = MQTTConfig(host="172.16.5.101",
                         port=1883)

mqtt = FastMQTT(config=mqtt_config)

mqtt.init_app(app)

con = sqlite3.connect("test.sqlite")
cur = con.cursor()


@mqtt.on_connect()
def connect(client, flags, rc, properties):
    mqtt.client.subscribe("/test") #subscribing mqtt topic
    print("Connected: ", client, flags, rc, properties)


@mqtt.subscribe("alexis/co2")
@mqtt.subscribe("alexis/tvoc")
@mqtt.subscribe("alexis/co")
async def message_to_topic(client, topic, payload, qos, properties):
    print("Received message to specific topic: ", topic, payload.decode(), qos, properties)
    cur.execute("insert into logs (message, topic, created_at) values (?, ?, ?)", [payload.decode(), topic, datetime.now()])
    con.commit()


@mqtt.on_disconnect()
def disconnect(client, packet, exc=None):
    print("Disconnected")



@mqtt.on_subscribe()
def subscribe(client, mid, qos, properties):
    print("subscribed", client, mid, qos, properties)


