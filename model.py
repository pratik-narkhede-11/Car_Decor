#model.py
import os
import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "car_decor.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

engine = create_engine(f'sqlite:///{DB_PATH}')
Session = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    role = Column(String(20), nullable=False, default='std')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class DecorItem(Base):
    __tablename__ = 'decor_items'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    price = Column(Float, nullable=False)

class CarRecord(Base):
    __tablename__ = 'car_records'
    id = Column(Integer, primary_key=True)
    car_number = Column(String(20), nullable=False)
    owner_name = Column(String(100))
    record_date = Column(DateTime, default=datetime.datetime.utcnow)
    total_cost = Column(Float, nullable=False, default=0.0)
    items_used = relationship("RecordItemLink", back_populates="car_record", cascade="all, delete-orphan")

class RecordItemLink(Base):
    __tablename__ = 'record_item_links'
    id = Column(Integer, primary_key=True)
    car_record_id = Column(Integer, ForeignKey('car_records.id'), nullable=False)
    decor_item_id = Column(Integer, ForeignKey('decor_items.id'), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    car_record = relationship("CarRecord", back_populates="items_used")
    decor_item = relationship("DecorItem")

def init_db():
    Base.metadata.create_all(engine)
    session = Session()
    if not session.query(User).filter_by(username='admin').first():
        default_admin = User(username='admin', role='admin')
        default_admin.set_password('admin123')
        session.add(default_admin)
        session.commit()
    session.close()