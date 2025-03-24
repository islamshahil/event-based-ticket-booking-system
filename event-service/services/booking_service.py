from sqlalchemy.orm import Session
from repositories.booking_repository import BookingRepository
from repositories.seat_repository import SeatRepository

class BookingService:
    @staticmethod
    def book_seats(db: Session, user_id: int, event_id: int, seat_ids: list[int]):
        """
        Book multiple seats for a user and an event.
        """
        seats = SeatRepository.get_seats_by_ids(db, seat_ids)
        booked_booking_ids = []

        for seat in seats:
            if not seat.is_booked:
                # Mark seat as booked
                seat.is_booked = True
                seat.booked_by = user_id
                SeatRepository.update_seat(db, seat)

                # Create booking record
                booking = BookingRepository.create_booking(db, user_id, event_id, seat.id)
                booked_booking_ids.append(booking.id)
            else:
                # Seat already booked, skip or handle error
                pass
        return booked_booking_ids

    @staticmethod
    def cancel_bookings(db: Session, event_id: int, seat_ids: list[int]):
        """
        Cancel the bookings for given seat IDs (and mark seats as not booked).
        """
        seats = SeatRepository.get_seats_by_ids(db, seat_ids)
        for seat in seats:
            seat.is_booked = False
            seat.booked_by = None
            SeatRepository.update_seat(db, seat)
        return True
