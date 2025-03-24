from sqlalchemy.orm import Session
from models import Seat

class SeatRepository:
    @staticmethod
    def get_seats_by_ids(db: Session, event_id: int, seat_id: int):
        return db.query(Seat).filter(Seat.event_id == event_id, Seat.id == seat_id).first()

    @staticmethod
    def update_seat(db: Session, seat: Seat):
        db.add(seat)
        db.commit()
        db.refresh(seat)
