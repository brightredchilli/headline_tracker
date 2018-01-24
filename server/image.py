from app import app
from collections import namedtuple
from datetime import datetime
from itertools import groupby
from helpers import get_current_aware_date
from operator import itemgetter, attrgetter
from os import listdir
from os.path import dirname, isfile, join
from pprint import pprint as pp
import pytz
import re

Image = namedtuple('Image', 'publication date path')


date_format_v2 = '%Y-%m-%d-%H_%M%Z_'
date_format_v1 = '%Y-%m-%d-%H_%M_'
date_format_v2_len = 20
date_format_v1_len = 17
date_regex = re.compile('\d\d\d\d-\d\d-\d\d-\d\d_\d\d(\w{3})?_')
tz_eastern = pytz.timezone('US/Eastern')
tz_utc = pytz.utc

def get_image_listing(target_date):
    """
    Get the latest listing of images based on a date
    :param target_date: datetime object
    :return: json string containing the latest images
    """

    images_path = app.config['APP_IMAGES_PATH']
    #images_path = join(app.config['APP_ROOT'], images_path)
    files = listdir(images_path)

    # get png files
    png_files = [ f for f in files if isimage(f)]
    print(target_date)

    imgs = [Image(parse_publication(f), parse_date(f), f) for f in png_files]
    imgs = [i for i in imgs if i.date <= target_date] # filter out later dates
    #imgs = [i for i in imgs if matches_date(i.date, target_date)] # get only target date's images

    pubs_dict = {}
    # must sort dictionary before using itertools.groupby
    imgs.sort(key=attrgetter('publication'))
    for key, valuesiter in groupby(imgs, key=attrgetter('publication')):

        # sort imgs by reverse chronological order
        valuesiter = sorted(valuesiter, key=attrgetter('date'), reverse=True)

        cropped = next((i for i in valuesiter if "cropped" in i.path), None)
        original = next((i for i in valuesiter if i.date == cropped.date and i.path != cropped.path), None)

        cropped_dict = {'path' : join("images", cropped.path), \
                        'date' : cropped.date} if cropped else None

        original_dict = {'path' : join("images", original.path), \
                         'date' : original.date} if original else None

        # get first cropped image

        pubs_dict[key] = {'cropped' : cropped_dict, \
                          'original' : original_dict, \
                          'url' : get_url(cropped.publication)}

    return pubs_dict


def get_url(vendor):
    """
    :param vendor: Canonical vendor name
    :return: Full vendor url
    """
    vendor_to_url = {
        'nytimes' : 'https://nytimes.com',
        'usatoday' : 'https://usatoday.com',
        'washingtonpost' : 'https://washingtonpost.com',
        'foxnews' : 'http://foxnews.com',
        'npr' : 'https://npr.org',
    }

    return vendor_to_url.get(vendor, 'Unknown url')


def parse_date(name, zone=None):
    """
    :param name: filename as a string
    :return: datetime object
    """
    date_part = get_date_part(name)
    if date_part:
        if len(date_part) == date_format_v2_len:
            date_format = date_format_v2
        elif len(date_part) == date_format_v1_len:
            date_format = date_format_v1
        else:
            print("no date found!")
            return None

    date_part = name[0:len(date_part)]
    date = datetime.strptime(date_part, date_format)

    if date_format == date_format_v1:
        zone = tz_eastern
    else:
        # quite bad, we only handle two formats for now
        # It's actually not easy to back out the date based on
        # shortcode mapping like 'EST' back to US/Eastern
        code = date_part[-4:-1]
        if code == 'EST':
            zone = tz_eastern
        else:
            zone = tz_utc

    date = zone.localize(date)
    return date

def get_date_part(name):
    match = date_regex.search(name)
    return match.group(0) if match else None


def parse_publication(name):
    """
    Given '2017-12-11-16_23_usatoday.png', returns usatoday
    :param name: filename as a string
    :return: the publication key
    """
    name = name[len(get_date_part(name)):]

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



