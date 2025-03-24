from sqlalchemy.orm import Session
from models import Event
from models import Seat

class EventRepository:
    @staticmethod
    def get_event_by_id(db: Session, event_id: int) -> Event:
        return db.query(Event).filter(Event.id == event_id).first()

    @staticmethod
    def list_events(db: Session):
        return db.query(Event).all()

class SeatRepository:
    @staticmethod
    def all_seats(db: Session):
        return db.query(Seat).all()
    
    @staticmethod
    def all_seats_event(db: Session, event_id):
        return db.query(Seat).filter(Seat.event_id == event_id).all()
    
    @staticmethod
    def get_seats_by_ids(db: Session, event_id: int, seat_id: int):
        return db.query(Seat).filter(Seat.event_id == event_id, Seat.id == seat_id).first()

    @staticmethod
    def update_seat(db: Session, seat: Seat):
        db.add(seat)
        db.commit()
        db.refresh(seat)
