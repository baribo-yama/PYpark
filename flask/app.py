from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/carousel1")
def carousel1():
    return render_template("carousel1.html")

@app.route("/carousel2")
def carousel2():
    return render_template("carousel2.html")

@app.route("/carousel3")
def carousel3():
    return render_template("carousel3.html")

@app.route("/carousel4")
def carousel4():
    return render_template("carousel4.html")

@app.route("/carousel5")
def carousel5():
    return render_template("carousel5.html")

@app.route("/carousel6")
def carousel6():
    return render_template("carousel6.html")

@app.route("/carousel7")
def carousel7():
    return render_template("carousel7.html")

@app.route("/carousel8")
def carousel8():
    return render_template("carousel8.html")

if __name__ == "__main__":
    app.run(debug=True)
