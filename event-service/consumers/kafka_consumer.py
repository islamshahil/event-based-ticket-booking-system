import json
import threading
from kafka import KafkaConsumer
from sqlalchemy.orm import Session
from database import SessionLocal
from config import KAFKA_BOOTSTRAP_SERVERS
from services.booking_service import BookingService

def consume_messages():
    consumer = KafkaConsumer(
        "booking-topic",
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset="earliest",
        group_id="event-service-group",
        value_deserializer=lambda m: json.loads(m.decode("utf-8"))
    )

    for msg in consumer:
        event = msg.value
        event_type = event.get("type")
        user_id = event.get("user_id")
        event_id = event.get("event_id")
        seat_ids = event.get("seat_ids", [])

        db: Session = SessionLocal()
        try:
            if event_type == "book":
                BookingService.book_seats(db, user_id, event_id, seat_ids)
            elif event_type == "cancel":
                BookingService.cancel_bookings(db, event_id, seat_ids)
        finally:
            db.close()

def start_consumer_thread():
    t = threading.Thread(target=consume_messages, daemon=True)
    t.start()
