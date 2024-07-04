#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


@app.route('/restaurants', methods= ['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    restaurant_data = [restaurant.to_dict() for restaurant in restaurants]
    return jsonify(restaurant_data), 200

@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant(id):
    restaurant = db.session.get(Restaurant, id)
    if restaurant:
        restaurant_data = restaurant.to_dict()
        restaurant_data['restaurant_pizzas'] = [
            {
                "id": rp.id,
                "pizza_id": rp.pizza_id,
                "price": rp.price,
                'restaurant_id': rp.restaurant_id,
                "pizza": rp.pizza.to_dict()
            } for rp in restaurant.restaurant_pizzas
        ]
        return jsonify(restaurant_data), 200
    else:
        return jsonify({"error": "Restaurant not found"}), 404
    
@app.route('/restaurants/<int:id>', methods= ['DELETE'])
def delete_restaurant(id):
    restaurant = db.session.get(Restaurant, id)
    if restaurant:
        db.session.delete(restaurant)
        db.session.commit()
        return make_response('', 204)
    else:
        return jsonify({"error": "Restaurant not found"}), 404
    

    
@app.route('/pizzas', methods= ['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    pizza_data = [pizza.to_dict() for pizza in pizzas]
    return jsonify(pizza_data), 200

class RestaurantPizzasResource(Resource):
    def post(self):
        try:
            data = request.get_json()
            price = int(data.get('price'))
            restaurant_pizza = RestaurantPizza(
                pizza_id=data.get('pizza_id'),
                restaurant_id=data.get('restaurant_id'),
                price=price,
            )
            db.session.add(restaurant_pizza)
            db.session.commit()
            response_dict = restaurant_pizza.to_dict()
            return make_response(response_dict, 201)
        except ValueError as e:
            return {"errors": ["validation errors"]}, 400
        except Exception as e:
            return {"errors": ["validation errors"]}, 400

api.add_resource(RestaurantPizzasResource, "/restaurant_pizzas")



if __name__ == "__main__":
    app.run(port=5555, debug=True)

