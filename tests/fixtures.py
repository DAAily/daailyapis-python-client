import http.client as http_client

import flask
import pytest
from pytest_localserver.http import WSGIServer

# .invalid will never resolve, see https://tools.ietf.org/html/rfc2606
NXDOMAIN = "test.invalid"


class RequestResponseTests:
    @pytest.fixture(scope="module")
    def server(self):
        """Provides a test HTTP server.

        The test server is automatically created before
        a test and destroyed at the end. The server is serving a test
        application that can be used to verify requests.
        """
        app = flask.Flask(__name__)
        app.debug = True

        @app.route("/basic")
        def index():
            header_value = flask.request.headers.get("x-test-header", "value")
            headers = {"X-Test-Header": header_value}
            return "Basic Content", http_client.OK, headers

        @app.route("/make-auth-request", methods=["POST"])
        def make_auth_request():
            header_value = flask.request.headers.get("Authorization", "Bearer")
            headers = {"Authorization": header_value}
            return "Authorized Content", http_client.OK, headers

        @app.route("/products")
        def get_lucy_data():
            header_value = flask.request.headers.get("Authorization", "Bearer")
            headers = {"Authorization": header_value}
            return "Lucy Products", http_client.OK, headers

        server = WSGIServer(application=app.wsgi_app)
        server.start()
        yield server
        server.stop()
