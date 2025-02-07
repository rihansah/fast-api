from fastapi import APIRouter, Depends, HTTPException, status, Path
from typing import Annotated
from sqlalchemy.orm import Session
from models import Todos, Users
from database import sessionLocal
from pydantic import BaseModel, Field
from .auth import get_current_user
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from passlib.context import CryptContext

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated = 'auto')
def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session,Depends(get_db)]
user_dependency = Annotated[dict,Depends(get_current_user)]

@router.get("/get_user",status_code=status.HTTP_200_OK)
async def get_user(db:db_dependency, user:user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user_data = db.query(Users).filter(Users.username == user.get("username")).first()
    return user_data

@router.put("/change_pass/{user_name}",status_code=status.HTTP_200_OK)
async def change_passsword(db: db_dependency, user: user_dependency, user_name:str, old_pass:str, new_pass:str):
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user found")
    user = db.query(Users).filter(Users.username==user_name).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User name is incorrect.")
    if not bcrypt_context.verify(old_pass,user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Old pass is incorrect.")
    hashed_pass = bcrypt_context.hash(new_pass)
    user.hashed_password=hashed_pass
    db.add(user)
    db.commit()
    pass