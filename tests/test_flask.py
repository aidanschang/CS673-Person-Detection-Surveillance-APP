import json
from app import app  # Flask instance of the Application


def test_main_route():
    response = app.test_client().get("/")
    assert response.status_code == 200


def test_home_route():
    response = app.test_client().get("/home")
    assert response.status_code == 200


def test_file_detection_route():
    response = app.test_client().get("/file_detection")
    assert response.status_code == 200


def test_history_route():
    response = app.test_client().get("/history")
    assert response.status_code == 200


def test_notification_route():
    response = app.test_client().get("/setting")
    assert response.status_code == 200


def test_file_id():
    response = app.test_client().get("/0")
    assert response.status_code == 200


def test_video_feed():
    response = app.test_client().get("/video_feed")
    assert response.status_code == 200


def test_upload_file(dog_file_path):
    client = app.test_client()

    mimetype = "application/json"
    headers = {"Content-Type": mimetype, "Accept": mimetype}
    data = {"file": dog_file_path}
    url = "/uploader"

    response = client.post(url, data=json.dumps(data), headers=headers)

    assert response.status_code == 200
