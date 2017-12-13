from datetime import datetime
from flask import Flask, request
from os.path import dirname, join, realpath
from pprint import pprint as pp

dir_path = dirname(realpath(__file__))
app = Flask(__name__)
app.config['APP_ROOT'] = dir_path + '/'
app.config['APP_IMAGES_PATH'] = 'static/images'
try:
    app.config.from_envvar('APP_ENVIRONMENTS')
except:
    pass

# import libraries after the app call

from image import get_image_listing_json


@app.route('/')
def hello():
    return redirect(url_for('headlines'))

@app.route('/headlines', strict_slashes=False, methods=['GET'])
def headlines():
    date = request.args.get('date', None)
    if not date:
        date = datetime.now()
    return get_image_listing_json(date)

