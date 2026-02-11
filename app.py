from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
DATABASE = "database.db"

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def home():
    return redirect(url_for("submit_request"))
                    
@app.route("/request", methods=["GET", "POST"])
def submit_request():
    if request.method == "POST":
        conn = get_db()
        conn.execute(
            "INSERT INTO leave_requests (start_date, end_date, leave_type, status) VALUES (?, ?, ?, ?)",
            (
                request.form["start_date"],
                request.form["end_date"],
                request.form["leave_type"],
                "Pending"
            )
        )
        conn.commit()
        conn.close()
        return redirect(url_for("submit_request"))
    
    return render_template("submit_request.html")

@app.route("/manager", methods=["GET", "POST"])
def manager_review():
    conn = get_db()
    
    if request.method == "POST":
        status = "Approved" if request.form["action"] == "approve" else "Rejected"
        conn.execute(
            "UPDATE leave_requests SET status = ? WHERE id = ?",
            (status, request.form["id"])
        )
        conn.commit()
        
    requests = conn.execute("SELECT * FROM leave_requests").fetchall()
    conn.close()
    
    return render_template("manager_review.html", requests=requests)
    
if __name__ == "__main__":
    app.run(debug=True)