from flask import Flask, render_template, request, redirect, session
import sqlite3
import validators

app = Flask(__name__)
app.config['SECRET_KEY'] = "4v3r1s00p3rs3kr3tk3y"

acct = {
    "username": "admin",
    "password": "hunter2"
}

with sqlite3.connect("data.db") as conn:
    cur = conn.cursor()
    cur.execute('''create table if not exists videos (
                id integer primary key autoincrement,
                field text,
                url text,
                visible text
    )''')
    cur.execute('''create table if not exists meta (
                field text,
                message text
    )''')
    conn.commit()

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "GET" or "user" not in session:
        return redirect("/")

    field = request.form.get("field", "").strip()
    url = request.form.get("url", "").strip()
    visible = request.form.get("visible", "0")

    if not field or not url:
        return "cannot be empty"

    if not validators.url(url):
        return "incorrect url"

    with sqlite3.connect("data.db") as conn:
        cur = conn.cursor()
        cur.execute('insert into videos values (NULL, ?, ?, ?)', (field, url, visible))
        conn.commit()

    return redirect("/admin")

@app.route("/news", methods=["GET", "POST"])
def news():
    if request.method == "GET" or "user" not in session:
        return redirect("/")

    announce = request.form.get("news", "").strip()

    with sqlite3.connect("data.db") as conn:
        cur = conn.cursor()
        if cur.execute('select * from meta where field="news"').fetchone():
            cur.execute('update meta set message=? where field="news"', (announce,))
        else:
            cur.execute('insert into meta values ("news", ?)', (announce,))
        conn.commit()

    return redirect("/admin")

@app.route("/change", methods=["GET", "POST"])
def change():
    if request.method == "GET" or "user" not in session:
        return redirect("/")

    id = request.form.get("id", "")
    field = request.form.get("field", "").strip()
    url = request.form.get("url", "").strip()
    visible = request.form.get("visible", "0")
    submit = request.form.get("submit", "Change")

    if not id or not field or not url:
        return "cannot be empty"

    if not validators.url(url):
        return "incorrect url"

    if submit == "Delete":
        with sqlite3.connect("data.db") as conn:
            cur = conn.cursor()
            cur.execute('delete from videos where id=?', (id,))
            conn.commit()

    with sqlite3.connect("data.db") as conn:
        cur = conn.cursor()
        cur.execute('update videos set field=?, url=?, visible=? where id=?', (field, url, visible, id))
        conn.commit()

    return redirect("/admin")

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if username == acct['username'] and password == acct['password']:
            session['user'] = username
        return redirect("/admin")

    if "user" in session:
        with sqlite3.connect("data.db") as conn:
            cur = conn.cursor()
            res = cur.execute('select * from videos').fetchall()
            announce = cur.execute('select * from meta where field="news"').fetchone()
        if not announce:
            announce = ""
        else:
            announce = announce[1]
        data = []
        for r in res:
            data.append({
                "id": r[0],
                "field": r[1],
                "url": r[2],
                "visible": r[3]
            })
        return render_template("admin.html", data=data, announce=announce)

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

@app.route("/")
def index():
    with sqlite3.connect("data.db") as conn:
        cur = conn.cursor()
        res = cur.execute('select * from videos').fetchall()
        announce = cur.execute('select * from meta where field="news"').fetchone()
    data = []
    for r in res:
        data.append({
            "id": r[0],
            "field": r[1],
            "url": r[2],
            "visible": r[3]
        })
    if not announce:
        announce = ""
    else:
        announce = announce[1].split("\n")
    return render_template("index.html", data=data, announce=announce)

if __name__ == "__main__":
    app.run()