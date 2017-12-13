from datetime import datetime
from flask import Flask, json, redirect, render_template, request, url_for
from os.path import dirname, join, realpath
from pprint import pprint as pp

dir_path = dirname(realpath(__file__))
app = Flask(__name__)
app.config['APP_ROOT'] = dir_path + '/'
app.config['APP_IMAGES_PATH'] = 'static/images'
app.config['site_title'] = 'Who is watching'
app.config['site_description'] = 'A headline gatherer'
try:
    app.config.from_envvar('APP_ENVIRONMENTS')
except:
    pass

# import libraries after the app call
from image import get_image_listing
from helpers import request_wants_json

@app.route('/')
def hello():
    return redirect(url_for('headlines'))

@app.route('/headlines', strict_slashes=False, methods=['GET'])
def headlines():
    date_str = request.args.get('date', None)
    try:
        date = datetime.datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
    except:
        date = datetime.now()

    pubs = get_image_listing(date)

    if request_wants_json():
        return json.jsonify({ 'pubs' : pubs })
    else:
        return render_template('index.html', pubs=pubs)

