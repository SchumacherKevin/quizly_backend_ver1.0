"""Tests for the CORS configuration used by the frontend."""

FRONTEND_ORIGIN = "http://127.0.0.1:5500"


def _preflight(client, origin):
    """Send a CORS preflight request from ``origin``."""
    return client.options(
        "/admin/login/",
        HTTP_ORIGIN=origin,
        HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
    )


def test_cors_preflight_allows_frontend_origin(client):
    """The frontend origin is allowed and may send credentials."""
    response = _preflight(client, FRONTEND_ORIGIN)

    assert response["Access-Control-Allow-Origin"] == FRONTEND_ORIGIN
    assert response["Access-Control-Allow-Credentials"] == "true"


def test_cors_rejects_unknown_origin(client):
    """Unknown origins do not get an allow origin header."""
    response = _preflight(client, "http://evil.example")

    assert "Access-Control-Allow-Origin" not in response
