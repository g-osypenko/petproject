from sqlalchemy import Column, Integer, String, Numeric, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from pgvector.sqlalchemy import Vector

from app.database.core import Base

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    products = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"))
    name = Column(String(255), nullable=False)
    price = Column(Numeric(12, 2), nullable=False)
    stock_quantity = Column(Integer, default=0)
    rating = Column(Numeric(3, 2), default=0.0)
    description = Column(Text)
    specifications = Column(JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    category = relationship("Category", back_populates="products")
    embedding = Column(Vector(768))

class MigrationLog(Base):
    __tablename__ = "migration_log"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), unique=True, nullable=False)
    applied_at = Column(DateTime, default=datetime.utcnow)