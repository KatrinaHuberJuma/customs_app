# coding: utf-8
from sqlalchemy import DECIMAL, DateTime  # API Logic Server GenAI assist
from sqlalchemy import Boolean, Column, DECIMAL, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

########################################################################################################################
# Classes describing database for SqlAlchemy ORM, initially created by schema introspection.
#
# Alter this file per your database maintenance policy
#    See https://apilogicserver.github.io/Docs/Project-Rebuild/#rebuilding
#
# Created:  February 17, 2026 20:48:03
# Database: sqlite:////Users/val/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test/ApiLogicServer/basic_demo_customs3/database/db.sqlite
# Dialect:  sqlite
#
# mypy: ignore-errors
########################################################################################################################
 
from database.system.SAFRSBaseX import SAFRSBaseX, TestBase
from flask_login import UserMixin
import safrs, flask_sqlalchemy, os
from safrs import jsonapi_attr
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.sql.sqltypes import NullType
from typing import List

db = SQLAlchemy() 
Base = declarative_base()  # type: flask_sqlalchemy.model.DefaultMeta
metadata = Base.metadata

#NullType = db.String  # datatype fixup
#TIMESTAMP= db.TIMESTAMP

from sqlalchemy.dialects.sqlite import *

if os.getenv('APILOGICPROJECT_NO_FLASK') is None or os.getenv('APILOGICPROJECT_NO_FLASK') == 'None':
    Base = SAFRSBaseX   # enables rules to be used outside of Flask, e.g., test data loading
else:
    Base = TestBase     # ensure proper types, so rules work for data loading
    print('*** Models.py Using TestBase ***')



class Customer(Base):  # type: ignore
    __tablename__ = 'customer'
    _s_collection_name = 'Customer'  # type: ignore

    id = Column(Integer, primary_key=True)
    name = Column(String)
    balance : DECIMAL = Column(DECIMAL)
    credit_limit : DECIMAL = Column(DECIMAL)
    email = Column(String)
    email_opt_out = Column(Boolean)

    # parent relationships (access parent)

    # child relationships (access children)
    OrderList : Mapped[List["Order"]] = relationship(back_populates="customer")



class Product(Base):  # type: ignore
    __tablename__ = 'product'
    _s_collection_name = 'Product'  # type: ignore

    id = Column(Integer, primary_key=True)
    name = Column(String)
    count_suppliers = Column(Integer)
    unit_price : DECIMAL = Column(DECIMAL)

    # parent relationships (access parent)

    # child relationships (access children)
    ProductSupplierList : Mapped[List["ProductSupplier"]] = relationship(back_populates="product")
    ItemList : Mapped[List["Item"]] = relationship(back_populates="product")



class Supplier(Base):  # type: ignore
    __tablename__ = 'supplier'
    _s_collection_name = 'Supplier'  # type: ignore

    id = Column(Integer, primary_key=True)
    name = Column(String)
    contact_name = Column(String)
    phone = Column(String)
    email = Column(String)
    region = Column(String)

    # parent relationships (access parent)

    # child relationships (access children)
    ProductSupplierList : Mapped[List["ProductSupplier"]] = relationship(back_populates="supplier")



class Order(Base):  # type: ignore
    __tablename__ = 'order'
    _s_collection_name = 'Order'  # type: ignore

    id = Column(Integer, primary_key=True)
    notes = Column(String)
    customer_id = Column(ForeignKey('customer.id'), nullable=False)
    CreatedOn = Column(Date)
    date_shipped = Column(Date)
    amount_total : DECIMAL = Column(DECIMAL)

    # parent relationships (access parent)
    customer : Mapped["Customer"] = relationship(back_populates=("OrderList"))

    # child relationships (access children)
    ItemList : Mapped[List["Item"]] = relationship(back_populates="order")



class ProductSupplier(Base):  # type: ignore
    __tablename__ = 'product_supplier'
    _s_collection_name = 'ProductSupplier'  # type: ignore

    id = Column(Integer, primary_key=True)
    product_id = Column(ForeignKey('product.id'))
    supplier_id = Column(ForeignKey('supplier.id'))
    supplier_part_number = Column(String)
    unit_cost : DECIMAL = Column(DECIMAL)
    lead_time_days = Column(Integer)

    # parent relationships (access parent)
    product : Mapped["Product"] = relationship(back_populates=("ProductSupplierList"))
    supplier : Mapped["Supplier"] = relationship(back_populates=("ProductSupplierList"))

    # child relationships (access children)



class Item(Base):  # type: ignore
    __tablename__ = 'item'
    _s_collection_name = 'Item'  # type: ignore

    id = Column(Integer, primary_key=True)
    order_id = Column(ForeignKey('order.id'))
    product_id = Column(ForeignKey('product.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    amount : DECIMAL = Column(DECIMAL)
    unit_price : DECIMAL = Column(DECIMAL)

    # parent relationships (access parent)
    order : Mapped["Order"] = relationship(back_populates=("ItemList"))
    product : Mapped["Product"] = relationship(back_populates=("ItemList"))

    # child relationships (access children)



# ==============================================================================
# CBSA Steel Derivative Goods Surtax System
# PC Number: 2025-0917, Program Code: 25267A
# Effective Date: 2025-12-26
# ==============================================================================

class ProvinceTaxRate(Base):  # type: ignore
    """Provincial Sales Tax (PST) and Harmonized Sales Tax (HST) rates by province"""
    __tablename__ = 'province_tax_rate'
    _s_collection_name = 'ProvinceTaxRate'  # type: ignore

    id = Column(Integer, primary_key=True)
    province_code = Column(String(2), nullable=False, unique=True)  # ON, BC, QC, etc.
    province_name = Column(String(100), nullable=False)
    tax_type = Column(String(10), nullable=False)  # PST, HST, GST
    tax_rate : DECIMAL = Column(DECIMAL(5, 4), nullable=False)  # 0.13 for 13%
    effective_date = Column(Date, nullable=False)

    # child relationships (access children)
    SurtaxOrderList : Mapped[List["SurtaxOrder"]] = relationship(back_populates="province_tax_rate")


class CountryOrigin(Base):  # type: ignore
    """Countries of origin for steel derivative goods with surtax applicability"""
    __tablename__ = 'country_origin'
    _s_collection_name = 'CountryOrigin'  # type: ignore

    id = Column(Integer, primary_key=True)
    country_code = Column(String(2), nullable=False, unique=True)  # DE, US, JP, CN
    country_name = Column(String(100), nullable=False)
    surtax_applicable = Column(Boolean, nullable=False, default=True)
    surtax_rate : DECIMAL = Column(DECIMAL(5, 4), nullable=False, default=0.25)  # 25%

    # child relationships (access children)
    SurtaxOrderList : Mapped[List["SurtaxOrder"]] = relationship(back_populates="country_origin")


class HSCodeRate(Base):  # type: ignore
    """HS Code classification with duty and surtax rates for steel derivative goods"""
    __tablename__ = 'hs_code_rate'
    _s_collection_name = 'HSCodeRate'  # type: ignore

    id = Column(Integer, primary_key=True)
    hs_code = Column(String(10), nullable=False, unique=True)
    description = Column(String(500), nullable=False)
    base_duty_rate : DECIMAL = Column(DECIMAL(5, 4), nullable=False)  # Base customs duty
    surtax_rate : DECIMAL = Column(DECIMAL(5, 4), nullable=False, default=0.25)  # Steel surtax 25%
    effective_date = Column(Date, nullable=False)

    # child relationships (access children)
    SurtaxLineItemList : Mapped[List["SurtaxLineItem"]] = relationship(back_populates="hs_code_rate")


class SurtaxOrder(Base):  # type: ignore
    """Main customs entry for steel derivative goods subject to surtax"""
    __tablename__ = 'surtax_order'
    _s_collection_name = 'SurtaxOrder'  # type: ignore

    id = Column(Integer, primary_key=True)
    order_number = Column(String(50), nullable=False, unique=True)
    entry_date = Column(Date, nullable=False)
    ship_date = Column(Date, nullable=False)
    country_origin_id = Column(ForeignKey('country_origin.id'), nullable=False)
    province_code_id = Column(ForeignKey('province_tax_rate.id'), nullable=False)
    
    # Calculated totals (derived by business logic)
    total_customs_value : DECIMAL = Column(DECIMAL(15, 2), default=0)
    total_duty : DECIMAL = Column(DECIMAL(15, 2), default=0)
    total_surtax : DECIMAL = Column(DECIMAL(15, 2), default=0)
    total_pst_hst : DECIMAL = Column(DECIMAL(15, 2), default=0)
    total_amount_due : DECIMAL = Column(DECIMAL(15, 2), default=0)
    
    surtax_applicable = Column(Boolean, default=False)  # True if ship_date >= 2025-12-26
    importer_name = Column(String(200))
    broker_name = Column(String(200))

    # parent relationships (access parent)
    country_origin : Mapped["CountryOrigin"] = relationship(back_populates="SurtaxOrderList")
    province_tax_rate : Mapped["ProvinceTaxRate"] = relationship(back_populates="SurtaxOrderList")

    # child relationships (access children)
    SurtaxLineItemList : Mapped[List["SurtaxLineItem"]] = relationship(back_populates="surtax_order", cascade="all, delete-orphan")


class SurtaxLineItem(Base):  # type: ignore
    """Individual goods on customs entry with duty and surtax calculations"""
    __tablename__ = 'surtax_line_item'
    _s_collection_name = 'SurtaxLineItem'  # type: ignore

    id = Column(Integer, primary_key=True)
    surtax_order_id = Column(ForeignKey('surtax_order.id'), nullable=False)
    hs_code_id = Column(ForeignKey('hs_code_rate.id'), nullable=False)
    line_number = Column(Integer, nullable=False)
    description = Column(String(500))
    quantity : DECIMAL = Column(DECIMAL(15, 3), nullable=False)
    unit_of_measure = Column(String(20), default='KG')
    unit_price : DECIMAL = Column(DECIMAL(15, 2), nullable=False)
    
    # Calculated fields (derived by business logic)
    customs_value : DECIMAL = Column(DECIMAL(15, 2), default=0)  # quantity * unit_price
    duty_rate : DECIMAL = Column(DECIMAL(5, 4), default=0)
    duty_amount : DECIMAL = Column(DECIMAL(15, 2), default=0)
    surtax_rate : DECIMAL = Column(DECIMAL(5, 4), default=0)
    surtax_amount : DECIMAL = Column(DECIMAL(15, 2), default=0)
    pst_hst_rate : DECIMAL = Column(DECIMAL(5, 4), default=0)
    pst_hst_amount : DECIMAL = Column(DECIMAL(15, 2), default=0)
    total_amount : DECIMAL = Column(DECIMAL(15, 2), default=0)

    # parent relationships (access parent)
    surtax_order : Mapped["SurtaxOrder"] = relationship(back_populates="SurtaxLineItemList")
    hs_code_rate : Mapped["HSCodeRate"] = relationship(back_populates="SurtaxLineItemList")

    # child relationships (access children)
