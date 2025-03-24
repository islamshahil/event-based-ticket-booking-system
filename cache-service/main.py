import os
import json
import threading
import requests
from fastapi import FastAPI
from kafka import KafkaConsumer
import redis

app = FastAPI(title="Cache Service")

# Environment variables
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
EVENT_SERVICE_URL = os.getenv("EVENT_SERVICE_URL", "http://event-service:8001")

# Initialize Redis client
r = redis.from_url(REDIS_URL)

def initialize_cache():
    try:
        print("Flushing Redis database...")
        r.flushdb()
        
        url = f"{EVENT_SERVICE_URL}/seats"
        print(f"Fetching seat data from {url}...")
        response = requests.get(url)
        response.raise_for_status()
        seats_data = response.json()
        
        for event in seats_data:
            event_id = event.get("event_id")
            booked_seats = event.get("booked_seats", [])
            for seat_id in booked_seats:
                cache_key = f"event:{event_id}:seat:{seat_id}"
                r.set(cache_key, "booked")
                print(f"Set cache key {cache_key} to 'booked'")
    except Exception as e:
        print(f"Error initializing cache: {e}")

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
        
        if event_type == "book":
            for seat_id in seat_ids:
                cache_key = f"event:{event_id}:seat:{seat_id}"
                r.set(cache_key, "booked")
                print(f"Booked seat updated: {cache_key} set to 'booked'")
        elif event_type == "cancel":
            for seat_id in seat_ids:
                cache_key = f"event:{event_id}:seat:{seat_id}"
                r.delete(cache_key)
                print(f"Cancellation processed: {cache_key} deleted")

@app.on_event("startup")
def startup_event():
    initialize_cache()
    t = threading.Thread(target=consume_messages, daemon=True)
    t.start()
