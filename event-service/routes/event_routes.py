from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from collections import defaultdict
from database import get_db
from repositories.event_repository import EventRepository, SeatRepository

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

@router.get("/seats/{event_id}")
def get_seat_availability(event_id: int, db: Session = Depends(get_db)):
    seats = SeatRepository.all_seats_event(db, event_id)
    booked_seats = [seat.id for seat in seats if seat.is_booked]
    available_seats = [seat.id for seat in seats if not seat.is_booked]
    return {"event_id": event_id, "booked_seats": booked_seats, "available_seats": available_seats}

@router.get("/seats")
def get_all_seat(db: Session = Depends(get_db)):
    try:
        seats = SeatRepository.all_seats(db)
        events = defaultdict(lambda: {"booked_seats": [], "available_seats": []})
        for seat in seats:
            if seat.is_booked:
                events[seat.event_id]["booked_seats"].append(seat.id)
            else:
                events[seat.event_id]["available_seats"].append(seat.id)

        result = []
        for event_id, data in events.items():
            result.append({
                "event_id": event_id,
                "booked_seats": data["booked_seats"],
                "available_seats": data["available_seats"]
            })
        return result
    except Exception as e:
        return str(e)
