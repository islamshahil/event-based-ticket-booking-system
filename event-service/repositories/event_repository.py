from sqlalchemy.orm import Session
from models import Event

class EventRepository:
    @staticmethod
    def get_event_by_id(db: Session, event_id: int) -> Event:
        return db.query(Event).filter(Event.id == event_id).first()

    @staticmethod
    def list_events(db: Session):
        return db.query(Event).all()
