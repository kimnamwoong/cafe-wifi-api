from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        dictionary = {}
        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self,column.name)

        return dictionary

    def __repr__(self):
        return f'<title: {self.name}>'


@app.route("/")
def home():
    return render_template("index.html")
    

## HTTP GET - Read Record
@app.route('/random',methods=["GET"])
def get_random_cafe():
    cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(cafes)

    return jsonify(cafe=random_cafe.to_dict())


@app.route('/all')
def get_all_cafe():
    # db 상 모든 데이터 select (return => list)
    cafes = db.session.query(Cafe).all()
    return jsonify(cafe=[cafe.to_dict() for cafe in cafes])


@app.route('/search',methods=["GET"])
def search_cafe():
    search_location = request.args.get('loc')
    cafe = Cafe.query.filter_by(location=search_location).first()
    if cafe:
        return jsonify(cafe=cafe.to_dict())
    else:
        return jsonify(error={"Not Found":"Sorry, we don't have a cafe at that location"})


## HTTP POST - Create Record
@app.route('/add',methods=["GET","POST"])
def add_cafe():
    new_cafe = Cafe(
        name=request.args.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price= request.form.get("price")
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success":"Successfully added the new cafe"})


## HTTP PUT/PATCH - Update Record
@app.route('/update-price/<int:cafe_id>',methods=["GET","PATCH"])
def update_price(cafe_id):
    new_price = request.args.get('new-price')
    update_cafe = Cafe.query.filter_by(id=cafe_id).first()
    if update_cafe:
        update_cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"success":"Successfully updated the price"}),200
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database"}),404
## HTTP DELETE - Delete Record
@app.route('/report-closed/<int:cafe_id>',methods=["GET","DELETE"])
def delete_cafe(cafe_id):
    api_key = request.args.get('api-key')
    if api_key == "TopSecretAPIKey":
        delete_cafe = db.session.query(Cafe).get(cafe_id)
        if delete_cafe:
            db.session.delete(delete_cafe)
            db.session.commit()
            return jsonify(response={"Delete":"Delete cafe"}),200
        else:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database"}),404
    else:
        return jsonify({"error": "Sorry, that's not allowed. Make sure you have the correct api_key"}),403


if __name__ == '__main__':
    app.run(debug=True)
