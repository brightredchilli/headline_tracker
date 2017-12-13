from app import app
from collections import namedtuple
from datetime import datetime
from itertools import groupby
from operator import itemgetter, attrgetter
from os import listdir
from os.path import dirname, isfile, join
from pprint import pprint as pp
import re

Image = namedtuple('Image', 'publication date path')

def get_image_listing(target_date):
    """
    Get the latest listing of images based on a date
    :param target_date: datetime object
    :return: json string containing the latest images
    """

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

    return pubs_dict


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



