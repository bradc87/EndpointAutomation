from flask import render_template
from eaMasterScheduler import app



@app.route('/')
def render_home():
    return render_template('main.html')