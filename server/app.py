from flask import Flask, request, jsonify
from flask_migrate import Migrate
from models import db, Sweet, Vendor, VendorSweet
from sqlalchemy.orm import Session

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
    vendors = db.session.query(Vendor).all()
    return jsonify([vendor.serialize() for vendor in vendors])


@app.route('/vendors/<int:id>', methods=['GET'])
def get_vendor(id):
    vendor = db.session.get(Vendor, id)
    if vendor:
        vendor_data = vendor.serialize()
        vendor_data['vendor_sweets'] = [vs.serialize() for vs in vendor.vendor_sweets]
        return jsonify(vendor_data)
    else:
        return jsonify({"error": "Vendor not found"}), 404


@app.route('/sweets', methods=['GET'])
def get_sweets():
    sweets = db.session.query(Sweet).all()
    return jsonify([sweet.serialize() for sweet in sweets])


@app.route('/sweets/<int:id>', methods=['GET'])
def get_sweet(id):
    sweet = db.session.get(Sweet, id)
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

    if price is None or not isinstance(price, (int, float)) or price < 0:
        return jsonify({"errors": ["validation errors"]}), 400

    vendor = db.session.get(Vendor, vendor_id)
    sweet = db.session.get(Sweet, sweet_id)

    if not vendor or not sweet:
        return jsonify({"errors": ["Vendor or Sweet not found"]}), 404

    vendor_sweet = VendorSweet(price=price, vendor=vendor, sweet=sweet)
    db.session.add(vendor_sweet)
    db.session.commit()

    return jsonify(serialize_vendor_sweet(vendor_sweet)), 201


@app.route('/vendor_sweets/<int:id>', methods=['DELETE'])
def delete_vendor_sweet(id):
    vendor_sweet = db.session.get(VendorSweet, id)
    if vendor_sweet:
        db.session.delete(vendor_sweet)
        db.session.commit()
        return '', 204
    else:
        return jsonify({"error": "VendorSweet not found"}), 404


def serialize_vendor_sweet(vendor_sweet):
    return {
        'id': vendor_sweet.id,
        'price': vendor_sweet.price,
        'vendor_id': vendor_sweet.vendor_id,
        'sweet_id': vendor_sweet.sweet_id,
        'vendor': vendor_sweet.vendor.serialize(),
        'sweet': vendor_sweet.sweet.serialize(),
    }

if __name__ == '__main__':
    app.run(port=5555, debug=True)
