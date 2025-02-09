from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from models import Users
from passlib.context import CryptContext
from database import sessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import timedelta, datetime, timezone
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated = 'auto')

SECRET_KEY = "e2198bac3559a3907e7f4d9296cf9aaba7cc19045ad9010aba2d335ec0ed64e8"
ALGORITHM = "HS256"

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/token")

class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str

class Token(BaseModel):
    access_token : str
    token_type : str

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session,Depends(get_db)]

templates = Jinja2Templates(directory="templates")
### pages ###
@router.get("/login-page")
async def login_page(request:Request):
    return templates.TemplateResponse("login.html",{"request":request})

@router.get("/register-page")
async def register_page(request:Request):
    return templates.TemplateResponse("register.html",{"request":request})

### end points ###
def authenticate_user(username: str, password : str, db):
    user = db.query(Users).filter(Users.username==username).first()
    if user is None:
        return False
    if not bcrypt_context.verify(password,user.hashed_password):
        return False
    return user

def create_access_token(db, user_name: str, user_id: int, role:str, expires_delta: timedelta):
    encode = {"sub":user_name, "id":user_id, "role":role}
    expires = datetime.now(timezone.utc)+expires_delta
    encode.update({"exp":expires})
    return jwt.encode(encode,SECRET_KEY,algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str,Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        userId: int = payload.get("id")
        userRole: str = payload.get("role")
        if username is None or userId is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user is not authorized")
        return {"username":username, "id":userId, "role":userRole}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user is not authorized")

@router.get("/get_users", status_code=status.HTTP_200_OK)
async def get_all_users(db: db_dependency):
    return db.query(Users).all()
    pass

@router.post("/create_user", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    create_user_model = Users(
        username = create_user_request.username,
        email = create_user_request.email,
        first_name = create_user_request.first_name,
        last_name = create_user_request.last_name,
        hashed_password = bcrypt_context.hash(create_user_request.password),
        role = create_user_request.role,
        is_active = True
    )
    db.add(create_user_model)
    db.commit()
    return {"message":"data inserted suscessfully"}

@router.post("/token", response_model=Token)
async def login_for_access_token(db : db_dependency, form_data : Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user is not authorized")
    token = create_access_token(db, user.username, user.id,user.role, timedelta(minutes=20) )
    return {"access_token":token, "token_type":"bearer"}
