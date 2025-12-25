from flask import jsonify, request, abort, g
from flask_login import login_required
from . import api
from models import db, Item, User
from functools import wraps

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        user = User.query.filter_by(token=token.replace('Bearer ', '')).first()
        if not user:
            return jsonify({'message': 'Invalid token'}), 401
        g.user = user
        return f(*args, **kwargs)
    return decorated

@api.route('/items', methods=['GET'])
@login_required
def get_items():
    items = Item.query.all()
    return jsonify([{'id': item.id, 'name': item.name, 'description': item.description} for item in items])

@api.route('/items/<int:id>', methods=['GET'])
@login_required
def get_item(id):
    item = Item.query.get_or_404(id)
    return jsonify({'id': item.id, 'name': item.name, 'description': item.description})

@api.route('/items', methods=['POST'])
@login_required
def create_item():
    if not request.json or 'name' not in request.json:
        abort(400)
    item = Item(name=request.json['name'], description=request.json.get('description', ''))
    db.session.add(item)
    db.session.commit()
    return jsonify({'id': item.id}), 201

@api.route('/items/<int:id>', methods=['PUT'])
@login_required
def update_item(id):
    item = Item.query.get_or_404(id)
    if not request.json:
        abort(400)
    item.name = request.json.get('name', item.name)
    item.description = request.json.get('description', item.description)
    db.session.commit()
    return jsonify({'id': item.id})

@api.route('/items/<int:id>', methods=['DELETE'])
@login_required
def delete_item(id):
    item = Item.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({'result': True})

# Token auth versions
@api.route('/token/items', methods=['GET'])
@token_required
def get_items_token():
    items = Item.query.all()
    return jsonify([{'id': item.id, 'name': item.name, 'description': item.description} for item in items])

@api.route('/token/login', methods=['POST'])
def token_login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and user.verify_password(data['password']):
        token = user.generate_token()
        db.session.commit()
        return jsonify({'token': token})
    return jsonify({'message': 'Invalid credentials'}), 401