from datetime import datetime
import sqlite3

from flask import Flask, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret-key"
DATABASE = "database.db"



def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn



def valid_date_range(start_date: str, end_date: str) -> bool:
    """Return True when both ISO dates are valid and start <= end."""
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return False
    return start <= end


@app.route("/")
def home():
    return redirect(url_for("submit_request"))


@app.route("/request", methods=["GET", "POST"])
def submit_request():
    if request.method == "POST":
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]
        leave_type = request.form["leave_type"]

        if not valid_date_range(start_date, end_date):
            flash("Please provide a valid date range.")
            return redirect(url_for("submit_request"))

        with get_db() as conn:
            conn.execute(
                "INSERT INTO leave_requests (start_date, end_date, leave_type, status) VALUES (?, ?, ?, ?)",
                (start_date, end_date, leave_type, "Pending"),
            )
            conn.commit()

        flash("Leave request submitted successfully.")
        return redirect(url_for("submit_request"))

    return render_template("submit_request.html")


@app.route("/manager", methods=["GET", "POST"])
def manager_review():
    with get_db() as conn:
        if request.method == "POST":
            status = "Approved" if request.form["action"] == "approve" else "Rejected"
            conn.execute(
                "UPDATE leave_requests SET status = ? WHERE id = ?",
                (status, request.form["id"]),
            )
            conn.commit()

        requests = conn.execute("SELECT * FROM leave_requests ORDER BY id DESC").fetchall()

    return render_template("manager_review.html", requests=requests)


if __name__ == "__main__":
    app.run(debug=True)
