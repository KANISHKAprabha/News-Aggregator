# here the pending works
# Preference handeling
# Celery -email notification
# Redis-for caching and handle the RSS feeds gracefully 
# Docker - for containerization
# Deployment - Heroku or any other cloud service












from ast import List
from fastapi import FastAPI,HTTPException,Depends,Request,Form
from sqlalchemy.orm import Session
import feedparser
from . import schemas,hash,crud,utils,database,models,dependency,tasks

from .database import get_db
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from jose import jwt, JWTError
from datetime import timedelta

app = FastAPI()
app.mount("/static", StaticFiles(directory="news_aggregator/static"), name="static")
templates = Jinja2Templates(directory="news_aggregator/templates")



models.Base.metadata.create_all(bind=database.engine)

import os

print("Templates folder exists:", os.path.isdir("news_aggregator/templates"))


@app.get("/", response_class=HTMLResponse)
def home(request: Request,db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    user = None
    if token:
        try:
            payload = jwt.decode(token, utils.JWT_SECRET_KEY, algorithms=[utils.ALGORITHM])
            email = payload.get("sub")
            user = crud.get_user_by_email(email=email, db=db)
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
        except JWTError:
            user = None
            return RedirectResponse(url="/refresh", status_code=303)
    return templates.TemplateResponse("home.html", {"request": request})
   


@app.get("/me", response_model=schemas.UserOut)
def get_me(user: models.User = Depends(dependency.get_current_user)):
    return user


@app.get("/register", response_class=HTMLResponse)
def register_form(request: Request,db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    user = None
    if token:
        try:
            payload = jwt.decode(token, utils.JWT_SECRET_KEY, algorithms=[utils.ALGORITHM])
            email = payload.get("sub")
            user = crud.get_user_by_email(email=email, db=db)
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
        except JWTError:
            user = None
            return RedirectResponse(url="/refresh", status_code=303)
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request,db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    user = None
    if token:
        try:
            payload = jwt.decode(token, utils.JWT_SECRET_KEY, algorithms=[utils.ALGORITHM])
            email = payload.get("sub")
            user = crud.get_user_by_email(email=email, db=db)
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
        except JWTError:
            user = None
            return RedirectResponse(url="/refresh", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request})


print("reach the  post request")
@app.post("/save_preferences", response_model=dict)
async def save_preferences(
    data: schemas.PreferenceIn,
    db: Session = Depends(get_db),
    user: models.User = Depends(dependency.get_current_user)
):
    if not user:
        raise HTTPException(status_code=403, detail="Not authenticated")

    # db.query(models.UserPreference).filter(models.UserPreference.user_email == user.email).delete()

    for category in data.category:
        pref = models.UserPreference(user_email=user.email, category=category)
        db.add(pref)

    db.commit()
    return {"message": "Preferences saved successfully"}


@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request, db: Session = Depends(get_db), topic: str =  "Technology"):
    token = request.cookies.get("access_token")
    user = None
    if token:
        try:
            payload = jwt.decode(token, utils.JWT_SECRET_KEY, algorithms=[utils.ALGORITHM])
            email = payload.get("sub")
            user = crud.get_user_by_email(email=email, db=db)
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
        except JWTError:
            user = None
            return RedirectResponse(url="/refresh", status_code=303)
    user_preference =   db.query(models.UserPreference).filter(models.UserPreference.user_email == user.email).all()    
   
   



    preferred_topics =[pref.category.value for pref in user_preference] if user_preference else ["Technology"]
    task_res = tasks.fetch_articles.delay(preferred_topics)
    safe_entries=task_res.get(timeout=30) if task_res else ["Technology"]
    

    return templates.TemplateResponse("admin.html", {"request": request, "user": user, "feeds": safe_entries,"show":len(user_preference)})







from fastapi import Request, Response

@app.get("/refresh")
def refresh_access_token(request: Request, response: Response, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token")
    print(refresh_token)
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    try:
        payload = jwt.decode(refresh_token, utils.JWT_REFRESH_SECRET_KEY, algorithms=[utils.ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid or expired refresh token")

    user = crud.get_user_by_email(email=email, db=db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Issue new access token
    new_access_token = utils.create_access_token(subject=email)
    # print(new_access_token,"line 202")
    response.set_cookie("access_token", new_access_token, httponly=True)

    return templates.TemplateResponse("login.html",{"request":request})










@app.get("/")
def read_root():
    return "Welcome to the URL shortener API :)"

@app.post("/create_user")
def user_create(
    email: str = Form(...),
    username: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
   
    # user = db.get()
    user_data = models.User(
        email=email,
        username=username,
        first_name=first_name,
        last_name=last_name,
        password=hash.hash_password(password)
    )
    print("User object being created:", user_data)
    print("Type of password:", type(user_data.password))

    db.add(user_data)

    db.commit()
    db.refresh(user_data)
    tasks.send_email_background.delay(
        to_email=email,
        subject="Welcome!",
        body=f"Hi {first_name}, thanks for registering!"
    )

    return RedirectResponse(url="/login", status_code=303)

@app.post("/login")
def user_login(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    db_user = crud.get_user_by_email(email=email, db=db)
    if not db_user or not hash.verify_password(password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = utils.create_access_token(subject=db_user.email)
    refresh_token = utils.create_refresh_token(subject=db_user.email)
    response = RedirectResponse(url="/admin", status_code=303)
    response.set_cookie(key="access_token", value=access_token, httponly=True, secure=True)
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=True)
    return response

@app.get("/logout")
def user_logout(response: Response):
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    response = RedirectResponse(url="/login", status_code=303)
    return response