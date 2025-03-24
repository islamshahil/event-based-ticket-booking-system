import os
import json
import threading
from fastapi import FastAPI
from kafka import KafkaConsumer
import redis

app = FastAPI(title="Cache Service")

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Initialize Redis
r = redis.from_url(REDIS_URL)

def consume_messages():
    consumer = KafkaConsumer(
        "booking-topic",
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset="earliest",
        group_id="cache-service-group",
        value_deserializer=lambda m: json.loads(m.decode("utf-8"))
    )

    for msg in consumer:
        event = msg.value
        event_type = event.get("type")
        event_id = event.get("event_id")
        seat_ids = event.get("seat_ids", [])

        if not event_id:
            continue

        # Update booked seats count in Redis
        if event_type == "book":
            for _ in seat_ids:
                r.hincrby("booked_seats", event_id, 1)
        elif event_type == "cancel":
            for _ in seat_ids:
                r.hincrby("booked_seats", event_id, -1)

@app.on_event("startup")
def startup_event():
    # Start consumer in background
    t = threading.Thread(target=consume_messages, daemon=True)
    t.start()

@app.get("/seats/{event_id}")
def get_seat_availability(event_id: int):
    """
    Return the number of booked seats for a given event.
    """
    booked = r.hget("booked_seats", str(event_id))
    booked_count = int(booked) if booked else 0
    return {"event_id": event_id, "booked_seats": booked_count}
