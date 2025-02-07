from fastapi import APIRouter, Depends, HTTPException, status, Path
from typing import Annotated
from sqlalchemy.orm import Session
from models import Todos
from database import sessionLocal
from pydantic import BaseModel, Field
from .auth import get_current_user


router = APIRouter(
    tags=["todos"]
    )

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session,Depends(get_db)]
user_dependency = Annotated[dict,Depends(get_current_user)]

class TodoRequest(BaseModel):
    title : str = Field(min_length=3, max_length=50)
    description : str = Field(min_length=3, max_length=50)
    priority : str = Field(max_length=1, min_length=1)
    completed : bool

@router.get("/todos", status_code=status.HTTP_200_OK)
async def get_all_todos(user: user_dependency ,db : db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user not authorized")
    todo_data = db.query(Todos).filter(Todos.owner_id == user.get("id")).all()
    if todo_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Data not found")
    return todo_data

@router.get("/todos/{u_id}", status_code=status.HTTP_200_OK)
async def get_todo_by_id(user: user_dependency ,db: db_dependency, u_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user not authorized")
    todo_data = db.query(Todos).filter(Todos.owner_id == user.get("id")).filter(Todos.id == u_id).first()
    if todo_data is None:
        raise HTTPException(status_code=404, detail="data not found")
    return todo_data

@router.post("/todos/create_todo", status_code=status.HTTP_201_CREATED)
async def create_new_todo(user:user_dependency, db: db_dependency, user_data:TodoRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user not authorized")
    todo_data = Todos(**user_data.model_dump(), owner_id = user.get("id"))
    db.add(todo_data)
    db.commit()
    
@router.put("/todos/{todo_id}")
async def update_existing_data(user:user_dependency, db: db_dependency, todo_id: int, user_data: TodoRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user not authorized")
    todo_data = Todos(**user_data.model_dump())
    temp_data = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).first()
    if temp_data is None:
        raise HTTPException(status_code=404, detail="Given id is not present")
    
    temp_data.description = todo_data.description
    temp_data.completed = todo_data.completed
    temp_data.title = todo_data.title
    temp_data.priority = todo_data.priority

    db.add(temp_data)
    db.commit()

@router.delete("/todos/{todo_id}")
async def update_existing_data(user: user_dependency, db: db_dependency, todo_id: int):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user not authorized")
    temp_data = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).first()
    if temp_data is None:
        raise HTTPException(status_code=404, detail="Given id is not present")
    db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).delete()
    db.commit()
