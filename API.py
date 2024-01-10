import traceback
import logging
import json
from flask import Flask
from flask_restful import Api, Resource, reqparse
from flask_httpauth import HTTPTokenAuth
from UsageGraph import UsageGraph

app = Flask(__name__)
api = Api(app)
app.config['BUNDLE_ERRORS'] = True
auth = HTTPTokenAuth(scheme='Bearer')

@auth.verify_token
def _authenticate(token):
    """
    Token authentication method.
    If token provided not matched returns False
    :param token:
    :return: Boolean value if token is right or wrong
    """
    if token == 'test_token':
        return True
    else:
        return False


@auth.error_handler
def auth_error():
    """
    Error handler methon.
    If error raised return access denied
    :return: 403 Error: Access Denied
    """
    return "Access Denied", 403

class PostGraph(Resource):
    """
    The usage of this class provide the JSON onject to build a
    graph in moodle via an API call. If the class's method is called via
    an API some parameters must be give.
    Bearer Token: To authenticate the user
    Body: A JSON obejct with requested parameters.
    An example object could look like:
    {
      "courseid": 32,
      "date_range": ["21.12.2023", "02.12.2024"],
      "LN": ["*"]
    }
    The service was build by Panos Pagonis. For questions email
    panos.pagonis@thi.de.
    The main methods are:
    post()
    """
    @auth.login_required
    def post(self):
        """
        Method that posts the requested from user parameters in
        UsageGraph method in order to produce the graph/JSON object.
        :return: JSON objects which includes the graph
        """
        try:
            parser = reqparse.RequestParser()
            parser.add_argument("courseid", location="json", type=int, required=True)
            #parser.add_argument("chapter", location="json")
            parser.add_argument("date_range", location="json", type=list)
            parser.add_argument("LN", location="json", type=list)
            params = parser.parse_args()

            usage_graph = UsageGraph()
            json_result = usage_graph.usagegraph(
                courseid=params['courseid'],
                chapter=params.get('chapter'),
                date_range=params.get('date_range'),
                LN=params.get('LN')
            )

            return json.loads(json_result)
        except Exception as error:
            logging.error(f"Error processing request: {error}")
            logging.error(traceback.format_exc())
            return {"error": f"Internal Server Error: {error}"}, 500

api.add_resource(PostGraph, "/graph")

if __name__ == '__main__':
    logging.basicConfig(filename="api.log", level=logging.INFO,
                        format="%(asctime)s [%(levelname)s]: %(message)s", datefmt="%d.%m.%Y | %H:%M:%S")
    logging.info("Starting flask_restful app...")
    app.run(debug=True, port=5005)
    logging.info("Ending flask_restful app")
