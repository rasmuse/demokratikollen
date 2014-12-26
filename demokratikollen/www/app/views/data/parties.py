from flask import Blueprint, request, jsonify, render_template
# from demokratikollen.www.app.models import parties
from demokratikollen.www.app.models.parties import party_election, get_municipality_timeseries

from demokratikollen.www.app.helpers.db import db
from demokratikollen.core.db_structure import Party


import datetime
from demokratikollen.core.utils.mongodb import MongoDBDatastore

blueprint = Blueprint('elections', __name__, url_prefix='/data')

@blueprint.route('/elections/<int:year>/<string:abbr>.json')
def election(year,abbr):
    try:
        d = party_election(abbr,year)
    except KeyError as e:
        return render_template('404.html'), 404
    return jsonify(d)

@blueprint.route('/elections/timeseries/<string:abbr>/<string:municipality_id>.json')
def municipality_timeseries(abbr,municipality_id):
    # try:
    d = get_municipality_timeseries(abbr,municipality_id)
    # except KeyError as e:
    #     return render_template('404.html'), 404
    return jsonify(d)


@blueprint.route('/cosigning/timeseries.json', methods=['GET'])
def timeseries():
    
    ds = MongoDBDatastore()
    cosigning_data = ds.get_object("party_cosigning_timeseries")
    return jsonify(cosigning_data);

@blueprint.route('/cosigning/matrix/<string:partyA>.json', methods=['GET'])
def cosigning_matrix(partyA):

    ds = MongoDBDatastore()
    mongodb = ds.get_mongodb_database() 
    mongo_collection = mongodb.party_cosigning_matrix
    record= mongo_collection.find_one({"partyA": party_abbr})
    if record:
        del record['_id']
        return jsonify(record)
    else:
        return render_template('404.html'), 404


@blueprint.route('/covoting/party_bias_<string:partyA>_<string:partyB>.json', methods=['GET'])
def party_bias(partyA,partyB):

    s=db.session
    A_id = s.query(Party.id).filter(Party.abbr==partyA).one()[0]
    B_id = s.query(Party.id).filter(Party.abbr==partyB).one()[0]

    ds = MongoDBDatastore()
    mongodb = ds.get_mongodb_database()
    mongo_collection = mongodb.party_covoting

    record = mongo_collection.find_one({"partyA": A_id, "partyB": B_id})
    if record:
        del record['_id']
        return jsonify(record);
    else:
        return render_template('404.html'), 404