from collections import namedtuple
from datetime import datetime
from flask import Flask, json, redirect, url_for, request
from itertools import groupby
from operator import itemgetter, attrgetter
from os import listdir
from os.path import dirname, isfile, join, realpath
from pprint import pprint as pp
import re

dir_path = dirname(realpath(__file__))
print(dir_path)

debug_images_path = dir_path + '/images'

app = Flask(__name__)
app.config['APP_ROOT'] = dir_path + '/'
app.config['APP_IMAGES_PATH'] = 'static/images'

try:
    app.config.from_envvar('APP_ENVIRONMENTS')
except:
    pass


@app.route('/')
def hello():
    return redirect(url_for('headlines'))

@app.route('/user/<int:id> ', strict_slashes=False)
@app.route('/headlines', strict_slashes=False, methods=['GET'])
def headlines():
    date = request.args.get('date', None)
    if not date:
        date = datetime.now()
    return get_image_listing(date)

def get_image_listing(target_date, time=None):
    images_path = app.config['APP_IMAGES_PATH']
    mypath = join(app.config['APP_ROOT'], images_path)
    files = listdir(mypath)

    # get png files
    png_files = [ f for f in files if isimage(f)]

    imgs = [Image(parse_publication(f), parse_date(f), f) for f in png_files]
    imgs = [i for i in imgs if matches_date(i.date, target_date)] # get only target date's images

    pubs_dict = {}
    # must sort dictionary before using itertools.groupby
    imgs.sort(key=attrgetter('publication'))
    for key, valuesiter in groupby(imgs, key=attrgetter('publication')):

        # sort imgs by reverse chronological order
        valuesiter = sorted(valuesiter, key=attrgetter('date'), reverse=True)

        cropped = next((i for i in valuesiter if "cropped" in i.path), None)
        original = next((i for i in valuesiter if i.date == cropped.date and i.path != cropped.path), None)

        cropped_dict = { 'path' : join('/', images_path, cropped.path), \
                        'date' : cropped.date }
        original_dict = { 'path' : join('/', images_path, original.path), \
                         'date' : original.date }

        # get first cropped image

        pubs_dict[key] = { 'cropped' : cropped_dict, \
                          'original' : original_dict }

    full_paths = [ join("/", images_path, png) for png in png_files ]

    return json.jsonify(pubs=pubs_dict)

Image = namedtuple('Image', 'publication date path')

def parse_date(name):
    """
    :param name: filename as a string
    :return: datetime object
    """
    # reference filename 2017-12-11-16_23_usatoday.png
    date_format = '%Y-%m-%d-%H_%M_'
    date_format_len = 17 # len("2017-12-11-16_23_")

    date_part = name[0:date_format_len]

    date = datetime.strptime(date_part, date_format)
    return date

def parse_publication(name):
    """
    Given '2017-12-11-16_23_usatoday.png', returns usatoday
    :param name: filename as a string
    :return: the publication key
    """
    date_format_len = len("2017-12-11-16_23")
    date_format_len = 17 # len("2017-12-11-16_23_")

    name = re.sub(r'[0-9_\-]*(.*)', r'\1', name)
    publication = re.sub(r'(_cropped\.png|\.png)', r'', name)
    return publication

def isimage(f): return re.search('.*\.png$', f)

def matches_date(date, target_date):
    """
    Return true if year, month, and day are the same
    :param date: datetime object
    """
    return date.year == target_date.year and \
           date.month == target_date.month and \
           date.day == target_date.day



