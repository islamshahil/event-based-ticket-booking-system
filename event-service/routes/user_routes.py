from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])

class UserCreateRequest(BaseModel):
    name: str
    email: str

@router.post("/")
def create_user(request: UserCreateRequest, db: Session = Depends(get_db)):
    user = UserService.create_user(db, request.name, request.email)
    return {"id": user.id, "name": user.name, "email": user.email}
