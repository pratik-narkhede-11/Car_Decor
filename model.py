# model.py

import os
import datetime
from sqlalchemy import (
    create_engine, 
    Column, 
    Integer, 
    String, 
    Float, 
    ForeignKey, 
    DateTime
)
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from werkzeug.security import generate_password_hash, check_password_hash

# --- 1. Configuration ---
# Store the database in a persistent location in the user's home directory.
# This is the single most important change to ensure data is not lost when
# the application is packaged and run as an executable (.exe).
APP_NAME = "CarDecorApp"
home_dir = os.path.expanduser("~")
app_data_dir = os.path.join(home_dir, APP_NAME)
DB_PATH = os.path.join(app_data_dir, "car_decor.db")

# --- 2. Database Setup ---
# Ensure the directory for the database exists before we try to use it.
os.makedirs(app_data_dir, exist_ok=True)

# The Engine is the starting point for any SQLAlchemy application.
engine = create_engine(f'sqlite:///{DB_PATH}')

# The Session is our window into the database. We create a Session factory
# that will be used to create new session objects in our controller.
Session = sessionmaker(bind=engine)

# A base class that our models will inherit from.
Base = declarative_base()

# --- 3. Model Definitions ---

class User(Base):
    """Represents a user of the application (either 'admin' or 'std')."""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    role = Column(String(20), nullable=False, default='std')

    def set_password(self, password):
        """Hashes and sets the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Checks if a provided password matches the stored hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User(username='{self.username}', role='{self.role}')>"

class DecorItem(Base):
    """Represents a single inventory item for car decoration."""
    __tablename__ = 'decor_items'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    price = Column(Float, nullable=False)

    def __repr__(self):
        return f"<DecorItem(name='{self.name}', price={self.price})>"

class CarRecord(Base):
    """Represents a single job or record for a specific car."""
    __tablename__ = 'car_records'

    id = Column(Integer, primary_key=True)
    car_number = Column(String(20), nullable=False)
    owner_name = Column(String(100))
    record_date = Column(DateTime, default=datetime.datetime.now) # Use local time
    total_cost = Column(Float, nullable=False, default=0.0)
    
    items_used = relationship(
        "RecordItemLink", 
        back_populates="car_record", 
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<CarRecord(car_number='{self.car_number}')>"

class RecordItemLink(Base):
    """Association table linking CarRecords and DecorItems with a quantity."""
    __tablename__ = 'record_item_links'

    id = Column(Integer, primary_key=True)
    car_record_id = Column(Integer, ForeignKey('car_records.id'), nullable=False)
    decor_item_id = Column(Integer, ForeignKey('decor_items.id'), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    
    car_record = relationship("CarRecord", back_populates="items_used")
    decor_item = relationship("DecorItem")

# --- 4. Database Initialization Function ---

def init_db():
    """
    Creates all database tables and ensures the default admin user exists.
    This function is designed to be called safely on every application startup.
    """
    Base.metadata.create_all(engine)
    session = Session()
    try:
        # Check if the 'root' user already exists.
        # BUG FIX: The original code checked for 'admin' but created 'root'.
        root_user_exists = session.query(User).filter_by(username='root').first()
        
        if not root_user_exists:
            print("Default admin user 'root' not found, creating it...")
            default_admin = User(username='root', role='admin')
            default_admin.set_password('root') # Default password is 'root'
            session.add(default_admin)
            session.commit()
            print("Default admin user created.")
    finally:
        # Always close the session to free up resources.
        session.close()