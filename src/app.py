"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planet, Favorite

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# Como todavia no hay login, usamos siempre este usuario como el usuario actual
CURRENT_USER_ID = 1


# Lista de todas las personas
@app.route('/people', methods=['GET'])
def get_people():
    people = People.query.all()
    return jsonify([person.serialize() for person in people]), 200


# Una sola persona por su id
@app.route('/people/<int:people_id>', methods=['GET'])
def get_one_person(people_id):
    person = People.query.get(people_id)
    if person is None:
        return jsonify({"msg": "Persona no encontrada"}), 404
    return jsonify(person.serialize()), 200


# Lista de todos los planetas
@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    return jsonify([planet.serialize() for planet in planets]), 200


# Un solo planeta por su id
@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_one_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"msg": "Planeta no encontrado"}), 404
    return jsonify(planet.serialize()), 200


# Lista de todos los usuarios
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200


# Favoritos del usuario actual
@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    favorites = Favorite.query.filter_by(user_id=CURRENT_USER_ID).all()
    return jsonify([favorite.serialize() for favorite in favorites]), 200


# Agregar un planeta favorito
@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"msg": "Planeta no encontrado"}), 404

    new_favorite = Favorite(user_id=CURRENT_USER_ID, planet_id=planet_id)
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify({"msg": "Planeta agregado a favoritos"}), 201


# Agregar una persona favorita
@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    person = People.query.get(people_id)
    if person is None:
        return jsonify({"msg": "Persona no encontrada"}), 404

    new_favorite = Favorite(user_id=CURRENT_USER_ID, people_id=people_id)
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify({"msg": "Persona agregada a favoritos"}), 201


# Borrar un planeta favorito
@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    favorite = Favorite.query.filter_by(
        user_id=CURRENT_USER_ID, planet_id=planet_id).first()
    if favorite is None:
        return jsonify({"msg": "Favorito no encontrado"}), 404

    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"msg": "Planeta borrado de favoritos"}), 200


# Borrar una persona favorita
@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    favorite = Favorite.query.filter_by(
        user_id=CURRENT_USER_ID, people_id=people_id).first()
    if favorite is None:
        return jsonify({"msg": "Favorito no encontrado"}), 404

    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"msg": "Persona borrada de favoritos"}), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
