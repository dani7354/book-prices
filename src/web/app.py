from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/details/{id}')
def details():
    return '<h1>Hello from Flask</h1>'


if __name__ == "__main__":
    app.run(debug=True)