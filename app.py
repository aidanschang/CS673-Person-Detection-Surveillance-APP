import os
import sqlite3

import torch  # noqa: F401

# for mac OS, it needs torch in order to use cv2 methods.
import cv2
import time

from typing import List
from datetime import datetime
from datetime import timedelta
from flask_mail import Mail, Message
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    Response,
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from user import user as user_blueprint
from user import decode_64
import user

from object_detection import ObjectDetection


def get_db_connection(database="database.db"):
    """Return connection to the database."""
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    return conn


def execute_query(sql, fetch_all: bool = True, database=None, commit=False):
    """This method is a generic handler for
    executing SQL on our database connection."""
    if database:
        conn = get_db_connection(database=database)
    else:
        conn = get_db_connection()

    if fetch_all:
        result = conn.execute(sql).fetchall()
    else:
        result = conn.execute(sql).fetchone()

    if commit:
        conn.commit()

    conn.close()
    return result


def insert_image_predictions_into_db(arr):
    """Insert numpy array into SQL DB for the history Tab.
    If a pdDataframe, use the .values method,"""
    file = execute_query(
        f""""Insert schema (Column1,column2,column3,column3
        VALUES({arr[0]},{arr[0]},{arr[0]},{arr[0]},{arr[0]})
        """,
        fetch_all=False,
    )
    if file is None:
        abort(404)
    return file


def get_file(file_id, database=None):
    """Return database row of data for a given file id."""
    file = execute_query(
        f"SELECT * FROM files WHERE id = {file_id}",
        fetch_all=False,
        database=database,
    )
    if file is None:
        abort(404)
    return file


class DetectionTrigger:
    """Observer to trigger notification/update of
    video stream frame on detection."""

    def update(self, frame, count):
        """Update database and notify user."""
        # check notification interval
        last_alert = get_last_alert_time()
        interval = get_alert_interval()
        next_alert_bound = last_alert + timedelta(minutes=interval)

        # uncomment to test
        # print(f"Next bound: {next_alert_bound}")
        # print(f"Current time: {datetime.now()}")
        if next_alert_bound < datetime.now():
            print("Lets go!")
            # create image from frame
            processed_filename = frame_to_image(frame)
            user_email = get_encoded_user_email()

            # write detection description
            detection_description = file_description(processed_filename)

            # insert detection results into table
            conn = get_db_connection()

            conn.execute(
                "INSERT INTO files (filename, user, detected, description)"
                " VALUES (?, ?, ?, ?)",
                (processed_filename, user_email, count, detection_description),
            )

            conn.commit()
            conn.close()

            # alert user
            send_email(
                recipients=[get_user_alert_address()],
                subject="FaFI Stream Detection Alert!",
                message=(
                    f"{detection_description} with {count} individuals"
                    " detected."
                ),
            )

            set_alert_time()


folder = "static/uploads/"
curfolder = ""
# user.current_user is current user email
UPLOAD_FOLDER = "static/uploads/"

app = Flask(__name__)
app.config[
    "SECRET_KEY"
] = "SOME_SECRET_KEY_VALUE"  # TODO: update with secret hash
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

mail_settings = {
    "MAIL_SERVER": "smtp.gmail.com",
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": "metcs673fafi@gmail.com",
    "MAIL_PASSWORD": "fdzlmtyogxbufwxt",
}

app.config.update(mail_settings)
mail = Mail(app)

# Login and out
app.register_blueprint(user_blueprint)

# Create a new object and execute.
detection = ObjectDetection()
trigger = DetectionTrigger()
detection.attach(trigger)


def get_user_email():
    """Get current user's email."""
    return decode_64(user.current_user)


def get_encoded_user_email():
    """Get encoded current user's email."""
    return user.current_user


def get_user_alert_address():
    """Get current user's email."""
    alert_email = execute_query(
        f"SELECT alert FROM users WHERE email = '{get_encoded_user_email()}'",
        fetch_all=False,
    )
    if alert_email[0] is None:
        return get_user_email()
    return alert_email[0]


def get_alert_interval():
    """Get current user's alert frame in minutes."""
    alert_interval = execute_query(
        "SELECT alert_interval FROM users WHERE email ="
        f" '{get_encoded_user_email()}'",
        fetch_all=False,
    )
    return alert_interval[0]


def get_last_alert_time():
    """Get current user's alert frame in minutes."""
    last_alert = execute_query(
        "SELECT last_alert as '[timestamp]' FROM users WHERE email ="
        f" '{get_encoded_user_email()}'",
        fetch_all=False,
    )
    print(f"Last Alert: {last_alert[0]}")
    return datetime.strptime(last_alert[0], "%Y-%m-%d %H:%M:%S")


def set_alert_time():
    """Get current user's alert frame in minutes."""
    execute_query(
        "UPDATE users "
        "SET last_alert = DATETIME('now', 'localtime') "
        f"WHERE email = '{get_encoded_user_email()}'",
        fetch_all=False,
        commit=True,
    )


def send_email(recipients: List[str], subject: str, message: str):
    """Send email using flask-mail."""
    with app.app_context():
        msg = Message(
            subject=subject,
            sender=app.config.get("MAIL_USERNAME"),
            recipients=recipients,
            body=message,
        )
        mail.send(msg)


def uploaded_filepath(filename):
    """Return filepath to uploaded file with input filename."""
    path = __file__[:-6] + os.path.join(app.config["UPLOAD_FOLDER"] + filename)
    if os.path.isfile(path):
        print("File exists")
    else:
        print("File does not exist")
        path = "Does not exist."

    return path


@app.route("/home")
def home():
    # check if user authorized
    if len(user.current_user) == 0:
        flash("Please Login")
        return render_template("login.html")
    else:
        """Route for home page."""
        count = detection.get_counts()

        return render_template("home.html", message=count)


@app.route("/stream")
def stream():
    # check if user authorized
    if len(user.current_user) == 0:
        flash("Please Login")
        return render_template("login.html")
    else:
        """Route for stream page."""
        count = detection.get_counts()

        return render_template("stream.html", message=count)


@app.route("/file_detection")
def file_detection():
    # check if user authorized
    if len(user.current_user) == 0:
        flash("Please Login")
        return render_template("login.html")
    else:
        """Route for file detection page."""
        return render_template("file_detection.html")


def file_description(filename):
    """Create file description based on standard file name."""
    parsed_name = filename.split("_")
    datetime_value = parsed_name[0]

    parsed_datetime = datetime_value.split("-")

    date = datetime.strptime(parsed_datetime[0], "%Y%m%d")
    date = date.strftime("%b %d, %Y")

    timestr = datetime.strptime(parsed_datetime[1], "%H%M%S")
    timestr = timestr.strftime("%I:%M:%S  %p")

    return f"Detection on {date} at {timestr}"


def _current_filename():
    """Generate standard file name based on current datetime."""
    timestr = time.strftime("%Y%m%d-%H%M%S")
    parsed_email = get_user_email().replace("@", "_")
    filename = timestr + "_" + parsed_email + ".jpg"
    sec_filename = secure_filename(filename)
    return sec_filename


def frame_to_image(frame):
    """Convert cv2 frame to image."""
    filename = _current_filename()
    upload_file_path = _upload_file_path(filename)
    cv2.imwrite(upload_file_path, frame)
    return filename


def _upload_file_path(filename):
    """Return file path to upload a file."""
    return os.path.join(app.config["UPLOAD_FOLDER"], filename)


def _save_intermittent_file(uploaded_file):
    """Save intermittent file to static path."""
    sec_filename = _current_filename()
    uploaded_file_path = _upload_file_path(sec_filename)
    uploaded_file.save(uploaded_file_path)
    return uploaded_file_path


def _upload_file(uploaded_file, detection):
    """Upload file handling functionality."""

    # apply model detection on uploaded file
    intermittent_file_path = _save_intermittent_file(uploaded_file)
    frame, counts = detection.score_plot_image(intermittent_file_path)
    processed_filename = frame_to_image(frame)

    user_email = get_encoded_user_email()

    # write detection description
    detection_description = file_description(processed_filename)

    # insert detection results into table
    conn = get_db_connection()

    conn.execute(
        "INSERT INTO files (filename, user, detected, description) VALUES (?,"
        " ?, ?, ?)",
        (processed_filename, user_email, counts, detection_description),
    )

    conn.commit()
    conn.close()

    # alert user
    send_email(
        recipients=[get_user_alert_address()],
        subject="FaFI image detection result!",
        message=(
            f"Submitted file: {uploaded_file.filename} has {counts} detected"
            " faces."
        ),
    )


@app.route("/uploader", methods=["GET", "POST"])
def upload_file():
    # check if user authorized
    if len(user.current_user) == 0:
        flash("Please Login")
        return render_template("login.html")
    else:
        """Route to uploader function where uploaded file is saved locally."""
        if request.method == "POST":
            if "file" not in request.files:
                flash("No file part")
                return redirect("home.html")

            _upload_file(request.files["file"], detection)
            return render_template("home.html")


@app.route("/history")
def history():
    # check if user authorized
    if len(user.current_user) == 0:
        flash("Please Login")
        return render_template("login.html")
    else:
        """Route for history page."""
        files = execute_query(
            f"SELECT * FROM files WHERE user = '{get_encoded_user_email()}';"
        )

        return render_template("history.html", files=files)


@app.route("/setting", methods=("GET", "POST"))
def setting():
    # check if user authorized
    if len(user.current_user) == 0:
        flash("Please Login")
        return render_template("login.html")
    else:
        """Route for Setting page and setting up notifier function."""
        if request.method == "POST":
            email = request.form["title"]
            interval = request.form["interval"]

            if not (email or interval):
                flash("Input is required!")

            if interval:
                if not (interval.isnumeric()) or int(interval) < 0:
                    flash("Interval must be a positive integer")
                else:
                    interval = int(interval)
                    conn = get_db_connection()

                    conn.execute(
                        "UPDATE users "
                        "SET alert_interval = 'int(interval)' "
                        f"WHERE email = '{get_encoded_user_email()}'"
                    )
                    flash("Interval updated successfully.")

            if email:
                if not email.__contains__("@"):
                    flash("Please enter valid email")
                elif not email.split("@")[1].__contains__("."):
                    flash("Please enter valid email")
                elif len(email.split("@")[0]) == 0:
                    flash("Please enter valid email")
                else:
                    # insert detection results into table
                    conn = get_db_connection()

                    conn.execute(
                        "UPDATE users "
                        f"SET alert = '{email}' "
                        f"WHERE email = '{get_encoded_user_email()}'"
                    )

                    conn.commit()
                    conn.close()

                    send_email(
                        recipients=[get_user_alert_address()],
                        subject="FaFi active",
                        message=(
                            "This email is registered for FaFi notifications."
                        ),
                    )
                    flash("Email successfully registered for notifications.")

        return render_template("setting.html")


@app.route("/<int:file_id>")
def file(file_id):
    # check if user authorized
    if len(user.current_user) == 0:
        flash("Please Login")
        return render_template("login.html")
    else:
        """Route to independent page to display each file."""
        file = get_file(file_id)
        filename = os.path.join(app.config["UPLOAD_FOLDER"], file["filename"])

        return render_template("file.html", file=file, filename=filename)


@app.route("/video_feed")
def video_feed():
    # check if user authorized
    if len(user.current_user) == 0:
        flash("Please Login")
        return render_template("login.html")
    else:
        detection_generator = detection()

        return Response(
            detection_generator,
            mimetype="multipart/x-mixed-replace; boundary=frame",
        )


if __name__ == "__main__":
    app.run(debug=True)
