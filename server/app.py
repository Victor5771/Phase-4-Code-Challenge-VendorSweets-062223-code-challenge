#!/usr/bin/env python3

from models import db, Sweet, Vendor, VendorSweet
from flask_migrate import Migrate
from flask import Flask, request, jsonify
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return '<h1>Code challenge</h1>'


@app.route('/vendors', methods=['GET'])
def get_vendors():
    vendors = Vendor.query.all()
    return jsonify([vendor.serialize() for vendor in vendors])


@app.route('/vendors/<int:id>', methods=['GET'])
def get_vendor(id):
    vendor = Vendor.query.get(id)
    if vendor:
        return jsonify(vendor.serialize())
    else:
        return jsonify({"error": "Vendor not found"}), 404


@app.route('/sweets', methods=['GET'])
def get_sweets():
    sweets = Sweet.query.all()
    return jsonify([sweet.serialize() for sweet in sweets])


@app.route('/sweets/<int:id>', methods=['GET'])
def get_sweet(id):
    sweet = Sweet.query.get(id)
    if sweet:
        return jsonify(sweet.serialize())
    else:
        return jsonify({"error": "Sweet not found"}), 404


@app.route('/vendor_sweets', methods=['POST'])
def create_vendor_sweet():
    data = request.json
    vendor_id = data.get('vendor_id')
    sweet_id = data.get('sweet_id')
    price = data.get('price')

    if vendor_id is None or sweet_id is None or price is None:
        return jsonify({"errors": ["Vendor ID, Sweet ID, and Price are required fields"]}), 400

    vendor = Vendor.query.get(vendor_id)
    sweet = Sweet.query.get(sweet_id)

    if not vendor or not sweet:
        return jsonify({"errors": ["Vendor or Sweet not found"]}), 404

    vendor_sweet = VendorSweet(price=price, vendor=vendor, sweet=sweet)
    db.session.add(vendor_sweet)
    db.session.commit()

    return jsonify(vendor_sweet.serialize()), 201


@app.route('/vendor_sweets/<int:id>', methods=['DELETE'])
def delete_vendor_sweet(id):
    vendor_sweet = VendorSweet.query.get(id)
    if vendor_sweet:
        db.session.delete(vendor_sweet)
        db.session.commit()
        return jsonify({})
    else:
        return jsonify({"error": "VendorSweet not found"}), 404


if __name__ == '__main__':
    app.run(port=5555, debug=True)

