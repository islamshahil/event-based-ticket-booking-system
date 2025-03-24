from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from repositories.booking_repository import BookingRepository

router = APIRouter(prefix="/bookings", tags=["bookings"])

@router.get("/user/{user_id}")
def get_bookings_by_user(user_id: int, db: Session = Depends(get_db)):
    bookings = BookingRepository.get_bookings_by_user(db, user_id)
    return [
        {
            "id": b.id,
            "event_id": b.event_id,
            "seat_id": b.seat_id,
            "status": b.status
        } for b in bookings
    ]
