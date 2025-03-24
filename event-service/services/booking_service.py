import os
import redis
from sqlalchemy.orm import Session
from repositories.booking_repository import BookingRepository
from repositories.seat_repository import SeatRepository

CACHE_SERVICE_URL = os.getenv("CACHE_SERVICE_URL", "http://localhost:8002")
redis_client = redis.from_url(CACHE_SERVICE_URL)


class BookingService:
    @staticmethod
    def book_seats(db: Session, user_id: int, event_id: int, seat_ids: list[int]):
        cache_key = f"event:{event_id}:seat:{seat_id}"
        try:
            booked_booking_ids = []
            for seat_id in seat_ids:
                seat_status = redis_client.get(cache_key)
                
                # If cache indicates the seat is already booked, record failure.
                if seat_status and seat_status.decode("utf-8") == "booked":
                    return {"status": f"{seat_id} is already booked"}

                # Mark the seat as booked in Redis.
                redis_client.set(cache_key, "booked")

                # Retrieve the seat from the database.
                seat = SeatRepository.get_seats_by_ids(db, event_id, seat_id)
                
                # Update the seat status in the DB.
                seat.is_booked = True
                seat.booked_by = user_id
                SeatRepository.update_seat(db, seat)

                # Create a booking record in the DB.
                booking = BookingRepository.create_booking(db, user_id, event_id, seat.id)
                booked_booking_ids.append(booking.id)
            
            return booked_booking_ids
        except Exception as e:
            redis_client.set(cache_key, "available")
            return {f"Booking Failed {str(e)}"}


    @staticmethod
    def cancel_bookings(db: Session, booking_id: int, event_id: int, seat_id: int):
        try:
            cache_key = f"seat:{seat.id}"
            redis_client.set(cache_key, "available")

            seat = SeatRepository.get_seats_by_ids(db, event_id, seat_id)
            seat.is_booked = False
            seat.booked_by = None
            SeatRepository.update_seat(db, seat)
            

            booking = BookingRepository.cancel_booking(db, booking_id)

            return {f"{booking} cancelled succesfully"}
        except Exception as e:
            return {f"Cancellation Failed {str(e)}"}
