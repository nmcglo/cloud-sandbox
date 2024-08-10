from fastapi import FastAPI
import pika
import os

app = FastAPI()


RABBITMQ_SERVER = f"{os.environ['RABBITMQ_SERVICE_HOSTNAME']}"
connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_SERVER, credentials=pika.PlainCredentials('user', 'password')))
channel = connection.channel()

channel.queue_declare(queue='compute-work')

def callback(ch, method, properties, body):
    print(f" [x] Received {body.decode()}")

channel.basic_consume(queue='compute-work', on_message_callback=callback, auto_ack=True)

@app.on_event("startup")
async def startup_event():
    print(os.environ)

    import threading
    threading.Thread(target=channel.start_consuming).start()

@app.get("/")
async def read_root():
    return {"message": "compute dummy is running"}
