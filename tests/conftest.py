import sqlite3
import pytest
import base64

from flask import Flask
from user import user


@pytest.fixture
def test_db_name():
    return "test.db"


@pytest.fixture(scope="function")
def setup_db(test_db_name):
    """Set up our testing db and yield the connection for downstream use."""
    conn = sqlite3.connect(test_db_name, timeout=20)
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS files;")

    cur.execute(
        """
        CREATE TABLE files (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                       filename TEXT NOT NULL,
                       content TEXT NOT NULL,
                       detected BIT NOT NULL DEFAULT 0
        );
        """
    )
    yield conn


@pytest.fixture
def dog_file_name():
    return "dog.jpg"


@pytest.fixture
def dog_file_path(dog_file_name):
    return f"tests/test_files/{dog_file_name}"


@pytest.fixture(scope="function")
def dog_file_contents(dog_file_path):
    with open(dog_file_path, "rb") as f_in:
        file_contents = base64.b64encode(f_in.read()).decode("utf-8")
    return file_contents


@pytest.fixture(scope="function")
def setup_dog_data(setup_db, dog_file_name, dog_file_contents):
    """Read in dog file image and save into database."""
    cur = setup_db
    cur.execute(
        "INSERT INTO files (filename, content) VALUES (?, ?)",
        (dog_file_name, dog_file_contents),
    )

    setup_db.commit()
    cur.close()


@pytest.fixture(scope="session")
def user_test_client():
    app = Flask(__name__, template_folder="templates/")
    app.register_blueprint(user, url_prefix="/")
    app.testing = True
    app.secret_key = "test"
    return app.test_client()


@pytest.fixture
def test_email():
    return "test@email.com"


@pytest.fixture
def test_password():
    return "password"
