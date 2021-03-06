from datetime import datetime
from flask import Flask, json, redirect, render_template, request, url_for, send_from_directory
from os.path import dirname, join, realpath
from pprint import pprint as pp
from os import environ
from helpers import ReverseProxied

debug_mode = environ.get('FLASK_DEBUG', False)

if debug_mode:
    from livereload import Server, shell

dir_path = dirname(realpath(__file__))
app = Flask(__name__)
app.wsgi_app = ReverseProxied(app.wsgi_app)

app.config['APP_ROOT'] = dir_path + '/'
imagepath = environ.get('IMAGE_PATH', 'test-images')
app.config['APP_IMAGES_PATH'] = join(app.config['APP_ROOT'], imagepath)
app.config['TEMPLATES_AUTO_RELOAD'] = debug_mode
app.config['site_title'] = 'Who is watching'
app.config['site_description'] = 'A headline gatherer'

try:
    app.config.from_envvar('APP_ENVIRONMENTS')
except:
    pass

print("Resolved image path: {}".format(app.config['APP_IMAGES_PATH']))

# import libraries after the app call
from image import get_image_listing
from helpers import request_wants_json, get_current_aware_date

if debug_mode:
    @app.route('/images/<path:path>')
    def send_image(path):
        return send_from_directory(app.config['APP_IMAGES_PATH'], path)

@app.route('/')
def hello():
    return redirect(url_for('headlines'))

@app.route('/headlines', strict_slashes=False, methods=['GET'])
def headlines():
    date_str = request.args.get('date', None)
    current = get_current_aware_date()
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
        date = datetime(date.year, date.month, date.day, tzinfo=current.tzinfo)
    except:
        date = current

    pubs = get_image_listing(date)

    if request_wants_json():
        return json.jsonify({ 'pubs' : pubs })
    else:
        return render_template('index.html', pubs=pubs)

@app.template_filter('formattime')
def _jinja2_filter_datetime(date):
    format='%b %d, %Y at %I:%M %p %Z'
    return datetime.strftime(date, format)

if debug_mode:
    print("Starting livereload server:")
    app.debug = True
    server = Server(app.wsgi_app)
    server.watch('static/css/*.css')
    server.watch('static/js/*.js')
    server.watch('templates/*')
    server.watch('*.py')
    server.serve()

