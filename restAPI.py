from flask import Flask, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restful import reqparse

"""
restAPI.py
========================================================
Program that creates and maintains a databse on a server
"""

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///databse.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)


class VisitModel(db.Model):
    """The record class in the db database

    This class is a look of our visit database

    :param visit_id: id of a visit, primary_key
    :type visit_id: int
    :param visit_date: date of a visit
    :type visit_date: int
    :param patient_id: id of a patient
    :type patient_id: str
    :param patient_name: name of a patient
    :type patient_name: str
    :param doctor_name: name of a doctor
    :type doctor_name: str
    """
    visit_id = db.Column(db.Integer, primary_key=True)
    visit_date = db.Column(db.Integer)
    patient_id = db.Column(db.String(500))
    patient_name = db.Column(db.String(500))
    doctor_name = db.Column(db.String(500))


class MyAppSchema(ma.Schema):
    """The class that provides object serialization

    This class is a schema that finds certain keywords and completes objects from given data
    """
    class Meta:
        fields = ('visit_id', 'visit_date', 'patient_id', 'patient_name', 'doctor_name')


my_app_schema = MyAppSchema(many=True)


visit_put_args = reqparse.RequestParser()
visit_put_args.add_argument("visit_id", type=int)
visit_put_args.add_argument("visit_date", type=int)
visit_put_args.add_argument("patient_id", type=str)
visit_put_args.add_argument("patient_name", type=str)
visit_put_args.add_argument("doctor_name", type=str)


@app.route('/visit/<parameter>', methods=["GET"])
def get_visit(parameter):
    """GET type method

    Function that returns choosen range of visits from database

    :param parameter: Specifies the choice of option according to which we want to select elements from the database
    :type parameter: str
    :returns: result, which may be one or list of VisitModel objects when the action is succesful or
    flask.Response object containing the error message in json format with error code
    :rtype: list/flask.Request object
    """
    if parameter == "doctor":
        req = visit_put_args.parse_args()
        entries = VisitModel.query.filter_by(doctor_name=req["doctor_name"]).all()
        if not entries:
            return make_response(jsonify({"error": "This doctor has no appointments..."}), 405)
        result = my_app_schema.dump(entries)
        return jsonify(result)

    if parameter == "patient":
        req = visit_put_args.parse_args()
        entries = VisitModel.query.filter_by(patient_id=req["patient_id"]).all()
        if not entries:
            return make_response(jsonify({"error": "This patient has no appointments..."}), 405)
        result = my_app_schema.dump(entries)
        return jsonify(result)

    if parameter == "selected":
        req = visit_put_args.parse_args()
        entries = VisitModel.query.filter_by(visit_date=req["visit_date"], patient_id=req["patient_id"],
                                             patient_name=req["patient_name"], doctor_name=req["doctor_name"]).all()
        if not entries:
            return make_response(jsonify({"error": "Such visit doesn't exist..."}), 405)
        result = my_app_schema.dump(entries)
        return jsonify(result)

    if parameter == "date":
        req = visit_put_args.parse_args()

        if req['visit_date'] < 100000000 or req['visit_date'] > 199999999:
            return make_response(jsonify({"error": "Invalid date format..."}), 409)

        date_day = req['visit_date'] - (req['visit_date'] % 100)
        entries = db.session.query(VisitModel).filter(VisitModel.visit_date >= date_day,
                                                      VisitModel.visit_date <= (date_day + 100)).all()
        if not entries:
            return make_response(jsonify({"error": "Such visit doesn't exist..."}), 405)
        result = my_app_schema.dump(entries)
        return jsonify(result)

    if parameter == "id":
        req = visit_put_args.parse_args()
        entries = VisitModel.query.filter_by(visit_id=req["visit_id"]).all()
        if not entries:
            return make_response(jsonify({"error": f"There is no appointment with ID:{req['visit_id']}..."}), 405)
        result = my_app_schema.dump(entries)
        return jsonify(result)

    if parameter == "all":
        entries = VisitModel.query.all()
        result = my_app_schema.dump(entries)
        return jsonify(result)

    return make_response(jsonify({"error": "Invalid specifier..."}), 409)


@app.route('/visit', methods=["POST"])
def post_visit():
    """POST type method 

    Function that creates a new VisitModel object in the database from data in json format given by the user

    :returns: result being a flask.Response object containing either message or error in json format with appropriate code
    :rtype: flask.Request object
    """
    req = visit_put_args.parse_args()

    result = VisitModel.query.filter_by(visit_id=req["visit_id"]).first()
    if result:
        return make_response(jsonify({"error": f"Visit ID {req['visit_id']} is already taken..."}), 409)

    result = VisitModel.query.filter_by(visit_date=req["visit_date"], patient_id=req["patient_id"],
                                        patient_name=req["patient_name"], doctor_name=req["doctor_name"]).first()
    if result:
        return make_response(jsonify({"error": "You've already made such appointment..."}), 409)

    result = VisitModel.query.filter_by(visit_date=req["visit_date"], doctor_name=req["doctor_name"]).first()
    if result:
        return make_response(jsonify({"error": "The given date is taken..."}), 409)

    visit_id = req["visit_id"]
    visit_date = req["visit_date"]
    patient_id = req["patient_id"]
    patient_name = req["patient_name"]
    doctor_name = req["doctor_name"]
    new_entry = VisitModel(visit_id=visit_id, visit_date=visit_date, patient_id=patient_id,
                           patient_name=patient_name, doctor_name=doctor_name)

    db.session.add(new_entry)
    db.session.commit()

    result = VisitModel.query.filter_by(visit_date=req["visit_date"], doctor_name=req["doctor_name"]).all()
    if len(result) > 1:  # This fragment ensures the control of cases of simultaneous arrival of identical requests
        db.session.delete(new_entry)
        db.session.commit()
        return make_response(jsonify({'error': 'Someone just took this date...'}), 409)

    return make_response(jsonify({'message': 'New visit created'}), 201)


@app.route('/visit/<visit_id>', methods=["PUT"])
def update_visit(visit_id):
    """PUT type method

    Function that used here to change already existing records in the database

    :param visit_id: PrimalKey of an object that we want to change
    :type visit_id: int
    :returns: result being a flask.Response object containing either message or error in json format with appropriate code
    :rtype: flask.Request object
    """
    req = visit_put_args.parse_args()
    entry = VisitModel.query.get(visit_id)
    if not entry:
        return make_response(jsonify({"error": "Such visit doesn't exist, cannot update..."}), 405)

    result = VisitModel.query.filter_by(visit_id=req["visit_id"]).first()
    if result and result != entry:
        return make_response(jsonify({"error": f"Visit ID {req['visit_id']} is already taken..."}), 409)

    if entry.visit_date != req["visit_date"] and entry.doctor_name != req["doctor_name"]:
        result = VisitModel.query.filter_by(visit_date=req["visit_date"], doctor_name=req["doctor_name"]).first()
        if result:
            return make_response(jsonify({"error": "The given date is taken, cannot update..."}), 409)

    entry.visit_id = req["visit_id"]
    entry.patient_id = req["patient_id"]
    entry.patient_name = req["patient_name"]
    entry.doctor_name = req["doctor_name"]
    entry.visit_date = req["visit_date"]
    db.session.add(entry)
    db.session.commit()
    return make_response(jsonify({'message': 'Visit updated'}), 202)


@app.route('/visit/<visit_id>', methods=["DELETE"])
def delete_visit(visit_id):
    """DELETE type method

    Function deleting choosen object form the database

    :param visit_id: PrimalKey of an object that we want to delete
    :type visit_id: int
    :returns: result being a flask.Response object containing either message or error in json format with appropriate code
    :rtype: flask.Request object
    """
    entry = VisitModel.query.get(visit_id)
    if not entry:
        return make_response(jsonify({"error": "Such visit doesn't exist"}), 405)
    db.session.delete(entry)
    db.session.commit()
    return make_response(jsonify({'message': 'Visit deleted'}), 209)


@app.route('/visit', methods=["DELETE"])
def delete_all():
    """DELETE type method 

    Function deleting all objects form the database

    :returns: result being a flask.Response object containing message in json format with appropriate code confirming the success
    :rtype: flask.Request object
    """
    db.session.query(VisitModel).delete()
    db.session.commit()
    return make_response(jsonify({'message': 'You deleted the database'}), 200)


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
