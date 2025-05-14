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
from models import db, User, Favorito, Planet, People
from sqlalchemy import select
#from models import Person

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

@app.route("/users", methods=["GET"])
def get_all_users():
    stmt = select(User)
    users = db.session.execute(stmt).scalars().all()
    return jsonify([user.serialize() for user in users]), 200

@app.route("/people", methods=["GET"])
def get_people():
    stmt = select(People)
    people = db.session.execute(stmt).scalars().all()
    return jsonify([person.serialize() for person in people]), 200

@app.route("/people/<int:people_id>", methods=["GET"])
def get_one_person(people_id):
    stmt = select(People).where(People.id == people_id)
    person = db.session.execute(stmt).scalar_one_or_none()

    if not person:
        return jsonify({"message": "People not found"}), 404

    return jsonify(person.serialize()), 200

@app.route("/planets", methods=["GET"])
def get_planets():
    stmt = select(Planet)
    planets = db.session.execute(stmt).scalars().all()
    return jsonify([planet.serialize() for planet in planets]), 200

@app.route("/planets/<int:planet_id>", methods=["GET"])
def get_one_planet(planet_id):
    stmt = select(Planet).where(Planet.id == planet_id)
    planet = db.session.execute(stmt).scalar_one_or_none()

    if not planet:
        return jsonify({"message": "Planet not found"}), 404

    return jsonify(planet.serialize()), 200


@app.route("/users/favoritos", methods=["GET"])
def get_user_favoritos():
    data = request.get_json()
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"message": "user_id is required"}), 400

    stmt = select(Favorito).where(Favorito.user_id == user_id)
    favoritos = db.session.execute(stmt).scalars().all()
    return jsonify([f.serialize() for f in favoritos]), 200

@app.route("/favorito/planet/<int:planet_id>", methods=["POST"])
def agregar_planet_favorito(planet_id):
    data = request.get_json()
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"message": "user_id is required"}), 400

    stmt_planet = select(Planet).where(Planet.id == planet_id)
    planet = db.session.execute(stmt_planet).scalar_one_or_none()
    if not planet:
        return jsonify({"message": "Planet not found"}), 404

    favorito = Favorito(user_id=user_id, planet_id=planet_id)
    db.session.add(favorito)
    db.session.commit()
    return jsonify(favorito.serialize()), 201


@app.route("/favorito/people/<int:people_id>", methods=["POST"])
def agregar_people_favorito(people_id):
    data = request.get_json()
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"message": "user_id is required"}), 400

    stmt_people = select(People).where(People.id == people_id)
    people = db.session.execute(stmt_people).scalar_one_or_none()
    if not people:
        return jsonify({"message": "People not found"}), 404

    favorito = Favorito(user_id=user_id, people_id=people_id)
    db.session.add(favorito)
    db.session.commit()
    return jsonify(favorito.serialize()), 201

@app.route("/favorito/planet/<int:planet_id>", methods=["DELETE"])
def delete_planet_favorito(planet_id):
    data = request.get_json()
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"message": "user_id is required"}), 400

    stmt = select(Favorito).where(Favorito.user_id == user_id, Favorito.planet_id == planet_id)
    favorito = db.session.execute(stmt).scalar_one_or_none()

    if not favorito:
        return jsonify({"message": "Planet favorite not found"}), 404

    db.session.delete(favorito)
    db.session.commit()
    return jsonify({"msg": "Planet favorite deleted"}), 200

@app.route("/favorito/people/<int:people_id>", methods=["DELETE"])
def delete_people_favorito(people_id):
    data = request.get_json()
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"message": "user_id is required"}), 400

    stmt = select(Favorito).where(Favorito.user_id == user_id, Favorito.people_id == people_id)
    favorito = db.session.execute(stmt).scalar_one_or_none()

    if not favorito:
        return jsonify({"message": "People favorite not found"}), 404

    db.session.delete(favorito)
    db.session.commit()
    return jsonify({"message": "People favorite deleted"}), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
