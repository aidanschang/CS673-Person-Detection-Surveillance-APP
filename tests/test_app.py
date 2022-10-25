from app import app
from app import get_file
from app import uploaded_filepath
import os


def test_uploaded_filepath():
    filename = "dog.jpg"
    fakename = "none"
    no_file = uploaded_filepath(fakename)
    exist_file = uploaded_filepath(filename)

    assert no_file == "Does not exist."
    assert exist_file == __file__[:-17] + os.path.join(
        app.config["UPLOAD_FOLDER"] + filename
    )


def test_get_file(
    setup_dog_data, dog_file_contents, dog_file_name, test_db_name
):
    """Test upload file functionality in app.py"""
    file = get_file(1, test_db_name)
    assert file[2] == dog_file_name  # index 2 is filename column
    assert file[3] == dog_file_contents  # index 3 is content column
