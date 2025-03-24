import os
import json
import uuid
from fastapi import FastAPI, Query
from pydantic import BaseModel
from kafka import KafkaProducer
import requests

app = FastAPI(title="REST Service")

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
EVENT_SERVICE_URL = os.getenv("EVENT_SERVICE_URL", "http://localhost:8001")
CACHE_SERVICE_URL = os.getenv("CACHE_SERVICE_URL", "http://localhost:8002")

# Kafka producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

class BookingRequest(BaseModel):
    user_id: int
    event_id: int
    seat_ids: list[int]  # One or more seat IDs to book

@app.post("/bookings")
def create_booking(request: BookingRequest):
    """
    Publish a 'book' event to Kafka with the booking details.
    """
    event_data = {
        "type": "book",
        "booking_id": str(uuid.uuid4()),
        "user_id": request.user_id,
        "event_id": request.event_id,
        "seat_ids": request.seat_ids
    }
    producer.send("booking-topic", event_data)
    producer.flush()
    return {"status": "Booking event published", "booking_id": event_data["booking_id"]}

@app.delete("/bookings/{booking_id}")
def cancel_booking(booking_id: str, event_id: int = Query(...), seat_ids: list[int] = Query(None)):
    """
    Publish a 'cancel' event to Kafka with the booking details.
    """
    event_data = {
        "type": "cancel",
        "booking_id": booking_id,
        "event_id": event_id,
        "seat_ids": seat_ids or []
    }
    producer.send("booking-topic", event_data)
    producer.flush()
    return {"status": "Cancellation event published", "booking_id": booking_id}

@app.get("/bookings/user/{user_id}")
def get_user_bookings(user_id: int):
    """
    Query the event-service for all bookings of a user.
    """
    try:
        resp = requests.get(f"{EVENT_SERVICE_URL}/bookings/user/{user_id}")
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

@app.get("/seats/{event_id}")
def get_seat_availability(event_id: int):
    """
    Query the cache-service for seat availability for a specific event.
    """
    try:
        resp = requests.get(f"{CACHE_SERVICE_URL}/seats/{event_id}")
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}
