from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime,
    func,
    CheckConstraint
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    bookings = relationship("Booking", back_populates="user")

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    date = Column(DateTime, nullable=False)
    location = Column(String(255), nullable=False)
    total_seats = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    seats = relationship("Seat", back_populates="event")
    bookings = relationship("Booking", back_populates="event")

class Seat(Base):
    __tablename__ = "seats"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"))
    seat_number = Column(String(10), nullable=False)
    is_booked = Column(Boolean, default=False)
    booked_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))

    event = relationship("Event", back_populates="seats")

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"))
    seat_id = Column(Integer, ForeignKey("seats.id", ondelete="CASCADE"))
    status = Column(String(20), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint("status IN ('CONFIRMED', 'CANCELED')", name="check_status"),
    )

    user = relationship("User", back_populates="bookings")
    event = relationship("Event", back_populates="bookings")
