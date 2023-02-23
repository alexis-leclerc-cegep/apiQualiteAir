from fastapi import FastAPI
import sqlite3
from datetime import datetime
from fastapi_mqtt import FastMQTT, MQTTConfig

app = FastAPI()

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


@app.get("/")
async def root():
    return {"message": "Hello World"}



@app.get("/getLogs")
async def get_logs():
    result = cur.execute('select * from logs')
    return result.fetchall()


@app.get("/getLatestCO2")
async def get_latest_co2():
    print("getLatestCO2")
    result = cur.execute("select message, created_at from logs "
                         "where topic = 'alexis/co2' "
                         "order by created_at desc "
                         "limit 1")
    column_names = [desc[0] for desc in cur.description]
    return zip(column_names, result.fetchone())


@app.get("/getLatestTVOC")
async def get_latest_tvoc():
    result = cur.execute("select message, created_at from logs "
                         "where topic = 'alexis/tvoc' "
                         "order by created_at desc "
                         "limit 1")
    column_names = [desc[0] for desc in cur.description]
    return zip(column_names, result.fetchone())
