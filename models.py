from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
import enum

Base = declarative_base()

class NewsCategoryEnum(str, enum.Enum):
    WORLD = "World"
    AI = "AI"                 
    SPACE = "SPACE"  
    POLITICS = "Politics"
    BUSINESS = "Business"
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

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    password = Column(String, nullable=False)  # store hashed

    preferences = relationship("UserPreference", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, ForeignKey("users.email", ondelete="CASCADE"))
    category = Column(Enum(NewsCategoryEnum), nullable=False)

    user = relationship("User", back_populates="preferences")

    def __repr__(self):
        return f"<UserPreference(user_id={self.id}, category={self.category})>"
