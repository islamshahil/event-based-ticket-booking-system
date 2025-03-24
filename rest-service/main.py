import os
import json
import uuid
import time
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from kafka import KafkaProducer, KafkaConsumer, TopicPartition
import requests

app = FastAPI(title="REST Service")

# Environment Variables
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
EVENT_SERVICE_URL = os.getenv("EVENT_SERVICE_URL", "http://localhost:8001")
# CACHE_SERVICE_URL = os.getenv("CACHE_SERVICE_URL", "http://localhost:8002")

# Kafka topic details
TOPIC = "booking-topic"
REQUEST_PARTITION = 0   # for booking requests
REPLY_PARTITION = 1     # for replies
TIMEOUT = 100            # seconds to wait for a reply

# Initialize Kafka Producer (uses JSON serialization)
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def send_request_and_wait(message: dict, timeout: int = TIMEOUT) -> dict:
    """
    Sends a message to the request partition of TOPIC and waits for a reply
    on the reply partition that matches the correlation_id.
    """
    # Ensure a unique correlation_id exists in the message.
    correlation_id = message.get("correlation_id", str(uuid.uuid4()))
    message["correlation_id"] = correlation_id

    # Send message to the request partition.
    producer.send(TOPIC, message, partition=REQUEST_PARTITION)
    producer.flush()

    # Create a Kafka consumer to listen to replies on the reply partition.
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset='earliest',
        group_id=None,  # No consumer group, so we read from the start of the partition.
        value_deserializer=lambda m: json.loads(m.decode("utf-8"))
    )
    tp = TopicPartition(TOPIC, REPLY_PARTITION)
    consumer.assign([tp])

    start_time = time.time()
    result = None

    # Poll until timeout is reached or a matching message is found.
    while time.time() - start_time < timeout:
        messages = consumer.poll(timeout_ms=1000)
        for _, msgs in messages.items():
            for msg in msgs:
                data = msg.value
                if data.get("correlation_id") == correlation_id:
                    result = data
                    break
            if result:
                break
        if result:
            break

    consumer.close()
    return result

# Pydantic model for booking requests
class BookingRequest(BaseModel):
    user_id: int
    event_id: int
    seat_ids: list[int]

@app.post("/bookings/book")
def create_booking(request: BookingRequest):
    message = {
        "type": "book",
        "user_id": request.user_id,
        "event_id": request.event_id,
        "seat_ids": request.seat_ids
    }
    result = send_request_and_wait(message)
    if result:
        return {"status": "Booking processed", "result": result}
    else:
        raise HTTPException(status_code=504, detail="Booking processing timed out")

@app.delete("/bookings/cancel/{booking_id}")
def cancel_booking(
    booking_id: int,
    event_id: int = Query(...),
    seat_id: list[int] = Query(None)
):
    message = {
        "type": "cancel",
        "booking_id": booking_id,
        "event_id": event_id,
        "seat_id": seat_id or []
    }
    result = send_request_and_wait(message)
    if result:
        return {"status": "Cancellation processed", "result": result}
    else:
        raise HTTPException(status_code=504, detail="Cancellation processing timed out")

@app.get("/bookings/user/{user_id}")
def get_user_bookings(user_id: int):
    try:
        resp = requests.get(f"{EVENT_SERVICE_URL}/bookings/user/{user_id}")
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/events")
def get_seat_availability(event_id: int):
    try:
        resp = requests.get(f"{EVENT_SERVICE_URL}/events")
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/events/seats/{event_id}")
def get_seat_availability(event_id: str):
    try:
        if event_id == "*":
            url = f"{EVENT_SERVICE_URL}/events/seats"
        else:
            int_event_id = int(event_id)
            url = f"{EVENT_SERVICE_URL}/events/seats/{int_event_id}"
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
