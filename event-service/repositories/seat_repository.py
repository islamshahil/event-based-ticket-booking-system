from sqlalchemy.orm import Session
from models import Seat

class SeatRepository:
    @staticmethod
    def get_seats_by_ids(db: Session, seat_ids: list[int]) -> list[Seat]:
        return db.query(Seat).filter(Seat.id.in_(seat_ids)).all()

    @staticmethod
    def update_seat(db: Session, seat: Seat):
        db.add(seat)
        db.commit()
        db.refresh(seat)
