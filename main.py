from fastapi import FastAPI, Request
from models import Base
from database import engine
from routers import auth, todos, admin, users
from fastapi.templating import Jinja2Templates

app = FastAPI()

Base.metadata.create_all(bind = engine)

templates = Jinja2Templates(directory="templates")

@app.get("/")
def test(request:Request):
    return templates.TemplateResponse("home.html",{"request":request})

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)