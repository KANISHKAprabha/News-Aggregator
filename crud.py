from sqlalchemy.orm import Session
from .models import User  # Assuming User model is in models.py in the same directory
from fastapi import Request, Depends, HTTPException, status
from .database import get_db
from .utils import JWT_SECRET_KEY, ALGORITHM
from jose import jwt, JWTError
from . import crud  # Assuming crud functions are defined in crud.py in the same directory


def get_user_by_email(email: str, db: Session = Depends(get_db)):
    
     try:
        if email is not None:
            email = email.strip()
        else:
             raise HTTPException(status_code=403, detail="type error ")
        user=db.query(User).filter(User.email == email).first() 
        return user
     except Exception as e :
         raise HTTPException(detail=str(e))
         
