from fastapi import Request, HTTPException, status, Depends
from jose import jwt, JWTError
from datetime import datetime
from .utils import JWT_SECRET_KEY, ALGORITHM
from . import crud, schemas, models, database
from sqlalchemy.orm import Session

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_token_from_cookie(request: Request) -> str:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return token

def get_current_user(
    token: str = Depends(get_token_from_cookie),
    db: Session = Depends(get_db)
) -> schemas.UserOut:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        exp = payload.get("exp")
        if datetime.fromtimestamp(exp) < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=403, detail="Could not validate credentials")

    user = crud.get_user_by_email(email=email, db=db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
