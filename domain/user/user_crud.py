from passlib.context import CryptContext
from sqlalchemy.orm import Session
from domain.user.user_schema import UserCreate
from models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_user(db: Session, user_create: UserCreate):
    db_user = User(username=user_create.username,
                   password=pwd_context.hash(user_create.password1),
                   email=user_create.email)
    db.add(db_user)
    db.commit()

def get_existing_user(db: Session, user_create: UserCreate):
    return db.query(User).filter(
        (User.username == user_create.username) |
        (User.email == user_create.email)
    ).first()

def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def change_user_email(db: Session, username: str, new_email: str) -> bool:
    db_user = db.query(User).filter(User.username == username).first()
    if db_user:
        db_user.email = new_email
        db.commit()
        return True
    return False


def change_user_password(db: Session, username: str, new_password: str) -> bool:
    db_user = db.query(User).filter(User.username == username).first()
    if db_user:
        db_user.password = pwd_context.hash(new_password)  # 새 비밀번호로 해시하고 업데이트
        db.commit()
        return True  # 변경 성공
    return False  # 사용자를 찾지 못한 경우, 변경 실패


