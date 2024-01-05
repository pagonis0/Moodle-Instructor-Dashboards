import os
import sys
import traceback
import logging
from functools import wraps
import json

import flask.json
from copy import deepcopy
from flask import Flask
from flask import request
from flask.json import jsonify
from flask_restful import Api, Resource, reqparse
from flask_httpauth import HTTPTokenAuth

from UsageGraph import UsageGraph

app = Flask(__name__)
api = Api(app)
app.config['BUNDLE_ERRORS'] = True
auth = HTTPTokenAuth(scheme='Bearer')

@auth.verify_token
def _authenticate(token):
    if token == 'test_token':
        return True
    else:
        return False


@auth.error_handler
def auth_error():
    return "Access Denied", 403

class PostGraph(Resource):
    @auth.login_required
    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument("courseid", location="json", type=int, required=True)
            #parser.add_argument("chapter", location="json")
            parser.add_argument("date_range", location="json", type=list)
            parser.add_argument("LN", location="json", type=list)
            #parser.add_argument("JSON", location="json", type=str)
            params = parser.parse_args()

            usage_graph = UsageGraph()
            json_result = usage_graph.usagegraph(
                courseid=params['courseid'],
                chapter=params.get('chapter'),
                date_range=params.get('date_range'),
                LN=params.get('LN'),
                #JSON=params.get('JSON')
            )

            return json.loads(json_result)
        except Exception as error:
            logging.error(f"Error processing request: {error}")
            logging.error(traceback.format_exc())  # Add this line for full traceback
            return {"error": f"Internal Server Error: {error}"}, 500

api.add_resource(PostGraph, "/graph")

if __name__ == '__main__':
    logging.basicConfig(filename="api.log", level=logging.INFO,
                        format="%(asctime)s [%(levelname)s]: %(message)s", datefmt="%d.%m.%Y | %H:%M:%S")
    logging.info("Starting flask_restful app...")
    app.run(debug=True, port=5005)
    logging.info("Ending flask_restful app")
