from flask import Flask, render_template, request, redirect, flash, session, url_for

app = Flask(__name__)
app.secret_key = "qwroiqwkdnkas"


@app.route('/')
def home():
    return render_template('index.html')


if __name__ == '__main__':
    app.run()