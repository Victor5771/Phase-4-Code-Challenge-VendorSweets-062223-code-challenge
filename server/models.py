from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, ForeignKey
from sqlalchemy.orm import relationship, validates
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)


class Sweet(db.Model, SerializerMixin):
    __tablename__ = 'sweets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    vendor_sweets = relationship('VendorSweet', back_populates='sweet')
    
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name
        }
    

class Vendor(db.Model, SerializerMixin):
    __tablename__ = 'vendors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    vendor_sweets = relationship('VendorSweet', back_populates='vendor')
    
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name
        }
    

class VendorSweet(db.Model, SerializerMixin):
    __tablename__ = 'vendor_sweets'

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)
    sweet_id = db.Column(db.Integer, db.ForeignKey('sweets.id'), nullable=False)

    sweet = relationship('Sweet', back_populates='vendor_sweets')
    vendor = relationship('Vendor', back_populates='vendor_sweets')
    
    @validates('price')
    def validate_price(self, key, price):
        if price is None or price < 0:
            raise ValueError("Price must be a non-negative number")
        return price
