from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from repositories.event_repository import EventRepository

router = APIRouter(prefix="/events", tags=["events"])

@router.get("/")
def list_events(db: Session = Depends(get_db)):
    events = EventRepository.list_events(db)
    return [
        {
            "id": e.id,
            "name": e.name,
            "date": e.date,
            "location": e.location,
            "total_seats": e.total_seats
        } for e in events
    ]
