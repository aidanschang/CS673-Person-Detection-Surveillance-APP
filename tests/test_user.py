import werkzeug.routing.exceptions
from sqlite3 import Connection
from user import get_db_connection


def test_get_db_connection():
    conn = get_db_connection()
    assert type(conn) == Connection


def test_main_route(user_test_client):
    response = user_test_client.get("/")
    assert response.status_code == 200


def test_login_route(user_test_client):
    response = user_test_client.get("/login")
    assert response.status_code == 200


def test_signup_route(user_test_client):
    response = user_test_client.get("/signup")
    assert response.status_code == 200


def test_user_signup(user_test_client, test_email, test_password):
    url = "/signup"
    response = user_test_client.post(
        url, data=dict(email=test_email, password=test_password, name="test")
    )
    assert response.status_code == 302


def test_user_wrong_password_redirect(
    user_test_client, test_email, test_password
):
    url = "/login"
    response = user_test_client.post(
        url, data=dict(email=test_email, password="bad")
    )
    assert response.status_code == 302


def test_user_login(user_test_client, test_email, test_password):
    url = "/login"
    try:
        user_test_client.post(
            url, data=dict(email=test_email, password=test_password)
        )
    except werkzeug.routing.exceptions.BuildError as e:
        assert "Could not build url for endpoint 'home'" in str(e)


def test_logout(user_test_client):
    url = "/logout"
    response = user_test_client.get(url)
    assert response.status_code == 302
