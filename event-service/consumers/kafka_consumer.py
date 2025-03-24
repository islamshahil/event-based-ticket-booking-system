import json
import threading
from kafka import KafkaConsumer, KafkaProducer
from sqlalchemy.orm import Session
from database import SessionLocal
from config import KAFKA_BOOTSTRAP_SERVERS
from services.booking_service import BookingService

TOPIC = "booking-topic"

def consume_messages():
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset="earliest",
        group_id="event-service-group",
        value_deserializer=lambda m: json.loads(m.decode("utf-8"))
    )

    # Producer for sending replies to partition 1.
    producer_reply = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )

    for msg in consumer:
        event = msg.value
        correlation_id = event.get("correlation_id")
        event_type = event.get("type")
        user_id = event.get("user_id")
        booking_id = event.get("booking_id")
        event_id = event.get("event_id")
        seat_ids = event.get("seat_ids", [])
        seat_id = event.get("seat_id", [])

        db: Session = SessionLocal()
        try:
            if event_type == "book":
                result = BookingService.book_seats(db, user_id, event_id, seat_ids)
            elif event_type == "cancel":
                result = BookingService.cancel_bookings(db, booking_id, event_id, seat_id)
            elif event_type == "get_user_bookings":
                result = BookingService.get_user_bookings(db, booking_id, event_id, seat_id)
            reply = {
                "correlation_id": correlation_id,
                "result": result
            }
            producer_reply.send(TOPIC, reply, partition=1)
            producer_reply.flush()
        finally:
            db.close()

def start_consumer_thread():
    t = threading.Thread(target=consume_messages, daemon=True)
    t.start()
