from fastapi import FastAPI
from models import Base
from database import engine
from routes.event_routes import router as event_router
from routes.user_routes import router as user_router
from consumers.kafka_consumer import start_consumer_thread

app = FastAPI(title="Event Service")

@app.on_event("startup")
def on_startup():
    # Create tables if not exist (for demo only; use migrations in production)
    Base.metadata.create_all(bind=engine)
    # Start Kafka consumer in background
    start_consumer_thread()

# Include routers
app.include_router(event_router)
app.include_router(user_router)
