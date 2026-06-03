from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class BelgeKaydi(Base):
    __tablename__ = "belgeler"

    id = Column(Integer, primary_key=True, index=True)
    dosya_adi = Column(String(255), nullable=False)
    tur = Column(String(50), nullable=False)
    parca_sayisi = Column(Integer, nullable=False)
    yukleme_tarihi = Column(DateTime, default=datetime.utcnow)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()