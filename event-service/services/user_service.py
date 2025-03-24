from sqlalchemy.orm import Session
from repositories.user_repository import UserRepository

class UserService:
    @staticmethod
    def create_user(db: Session, name: str, email: str):
        return UserRepository.create_user(db, name, email)

    @staticmethod
    def get_user(db: Session, user_id: int):
        return UserRepository.get_user_by_id(db, user_id)
