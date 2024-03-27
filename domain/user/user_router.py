from datetime import timedelta, datetime


from fastapi import APIRouter, HTTPException
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from domain.user import user_crud, user_schema
from domain.user.user_crud import pwd_context

from .user_schema import ChangeEmailRequest  # 정확한 경로에 따라 import 경로를 조정하세요
from .user_schema import ChangePasswordRequest  # 정확한 경로에 따라 import 경로를 조정하세요

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
SECRET_KEY = "29ba911058da1ba60c86ce2445effadbd1469abcdfeb30583fd882c16f69d574"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/login")

router = APIRouter(
    prefix="/api/user",
)

#
# @router.post("/create", status_code=status.HTTP_204_NO_CONTENT)
# def user_create(_user_create: user_schema.UserCreate, db: Session = Depends(get_db)):
#     user_crud.create_user(db=db, user_create=_user_create)

@router.post("/create", status_code=status.HTTP_204_NO_CONTENT)
def user_create(_user_create: user_schema.UserCreate, db: Session = Depends(get_db)):
    user = user_crud.get_existing_user(db, user_create=_user_create)
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="이미 존재하는 사용자입니다.")
    user_crud.create_user(db=db, user_create=_user_create)


@router.post("/login", response_model=user_schema.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                           db: Session = Depends(get_db)):

    # check user and password
    user = user_crud.get_user(db, form_data.username)
    if not user or not pwd_context.verify(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # make access token
    data = {
        "sub": user.username,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    access_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username
    }

def get_current_user(token: str = Depends(oauth2_scheme),
                     db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    else:
        user = user_crud.get_user(db, username=username)
        if user is None:
            raise credentials_exception
        return user



@router.post("/change-email", status_code=status.HTTP_204_NO_CONTENT)
def change_email(request: ChangeEmailRequest, db: Session = Depends(get_db), current_user: user_schema.User = Depends(get_current_user)):
    if user_crud.change_user_email(db, current_user.username, request.new_email):
        return {"msg": "Email changed successfully"}
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Email change failed",
    )


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(request: ChangePasswordRequest, db: Session = Depends(get_db), current_user: user_schema.User = Depends(get_current_user)):
    user = user_crud.get_user(db, current_user.username)
    if not user or not pwd_context.verify(request.old_password, user.password):
        # 여기를 수정합니다. HTTP 401 대신 HTTP 400을 사용
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password",
        )
    if user_crud.change_user_password(db, user.username, request.new_password):
        return {"msg": "Password changed successfully"}
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Password change failed",
    )
