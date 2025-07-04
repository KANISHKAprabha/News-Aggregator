from sqlalchemy.orm import Session
from .models import User  # Assuming User model is in models.py in the same directory
from fastapi import Request, Depends, HTTPException, status
from .database import get_db
from .utils import JWT_SECRET_KEY, ALGORITHM
from jose import jwt, JWTError
from . import crud  # Assuming crud functions are defined in crud.py in the same directory


def get_user_by_email(email: str, db: Session = Depends(get_db)):
    return db.query(User).filter(User.email == email).first() 
def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get("access_token")
    
    if not token:
        raise HTTPException(status_code=401, detail="Access token missing")

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Token payload invalid")

        user = crud.get_user_by_email(db=db, email=email)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid or expired token")
