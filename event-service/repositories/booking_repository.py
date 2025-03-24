from sqlalchemy.orm import Session
from models import Booking

class BookingRepository:
    @staticmethod
    def create_booking(db: Session, user_id: int, event_id: int, seat_id: int) -> Booking:
        booking = Booking(
            user_id=user_id,
            event_id=event_id,
            seat_id=seat_id,
            status="CONFIRMED"
        )
        db.add(booking)
        db.commit()
        db.refresh(booking)
        return booking

    @staticmethod
    def get_bookings_by_user(db: Session, user_id: int):
        return db.query(Booking).filter(Booking.user_id == user_id).all()

    @staticmethod
    def cancel_booking(db: Session, booking_id: int):
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if booking:
            booking.status = "CANCELED"
            db.commit()
            db.refresh(booking)
        return booking
