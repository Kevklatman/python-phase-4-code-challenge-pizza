#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
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

class RestaurantList(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return [restaurant.to_dict() for restaurant in restaurants]
    
class RestaurantByID(Resource):
    def get(self, id):
        restaurant = Restaurant.query.get(id)
        if restaurant:
            restaurant_data = restaurant.to_dict(rules=('restaurant_pizzas',))
            
            response_data = {
                "id": restaurant_data['id'],
                "name": restaurant_data['name'],
                "address": restaurant_data['address'],
                "restaurant_pizzas": []
            }
            
            for rp in restaurant_data['restaurant_pizzas']:
                pizza = Pizza.query.get(rp['pizza_id'])
                restaurant_pizza = {
                    "id": rp['id'],
                    "price": rp['price'],
                    "pizza_id": rp['pizza_id'],
                    "restaurant_id": rp['restaurant_id'],
                    "pizza": pizza.to_dict()
                }
                response_data['restaurant_pizzas'].append(restaurant_pizza)
            
            return response_data, 200
        else:
            return {"error": "Restaurant not found"}, 404
        
    def delete(self, id):
        restaurant = Restaurant.query.get(id)
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return '', 204  # 204 No Content
        else:
            return {"error": "Restaurant not found"}, 404
        
class PizzaList(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return [pizza.to_dict() for pizza in pizzas], 200
        


api.add_resource(RestaurantList, '/restaurants')
api.add_resource(RestaurantByID, '/restaurants/<int:id>')
api.add_resource(PizzaList, '/pizzas')



if __name__ == "__main__":
    app.run(port=5555, debug=True)
