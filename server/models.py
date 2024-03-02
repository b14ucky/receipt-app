from sqlalchemy import Boolean, Column, Integer, String, Float, Date
from .database import Base


class Buyers(Base):
    __tablename__ = "buyers"

    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), index=True)
    last_name = Column(String(100), index=True)


class Sellers(Base):
    __tablename__ = "sellers"

    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), index=True)
    last_name = Column(String(100), index=True)


class Products(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), index=True)
    price_per_unit = Column(Float(2), index=True)


class PaymentMethods(Base):
    __tablename__ = "payment_methods"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), index=True)


class Invoices(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True)
    number = Column(String(100), index=True)
    buyer_id = Column(Integer, index=True)
    seller_id = Column(Integer, index=True)
    product_id = Column(Integer, index=True)
    payment_method_id = Column(Integer, index=True)
    quantity = Column(Integer, index=True)
    total_amount = Column(Float(2), index=True)
    date_of_issue = Column(Date, index=True)
    date_of_purchase = Column(Date, index=True)
    place_of_issue = Column(String(100), index=True)
