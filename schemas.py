from typing import List

from pydantic import BaseModel,EmailStr
from enum import Enum

class UserCreate(BaseModel):
    email: str
    username: str
    first_name: str
    last_name: str
    password: str

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email:EmailStr
    password: str


    class Config:
        orm_mode = True
class UserResponseAfterLogin(BaseModel):
    email: EmailStr
    username: str
    first_name: str
    last_name: str

    class Config:
        orm_mode = True

class NewsCategory(str, Enum):
    WORLD = "World"
    POLITICS = "Politics"
    BUSINESS = "Business"
    AI = "AI"                
    SPACE = "SPACE"  
    TECHNOLOGY = "Technology"
    SCIENCE = "Science"
    ENTERTAINMENT = "Entertainment"
    SPORTS = "Sports"
    HEALTH = "Health"
    ENVIRONMENT = "Environment"
    EDUCATION = "Education"
    LIFESTYLE = "Lifestyle"
    CRIME = "Crime"
    RELIGION = "Religion"
    CULTURE = "Culture"
    AUTOMOTIVE = "Automotive"
    REAL_ESTATE = "Real Estate"



class UserPreference(BaseModel):
    id:int
    user_email: str
    category:List[NewsCategory]


    class Config:
        orm_mode = True



class UserOut(BaseModel):
    id: int
    email: str
    username: str
    first_name: str
    last_name: str

    class Config:
        orm_mode = True

class PreferenceIn(BaseModel):
    category: List[NewsCategory]
