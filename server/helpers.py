from datetime import datetime, timezone
from flask import request
import pytz

def request_wants_json():
    best = request.accept_mimetypes \
        .best_match(['application/json', 'text/html'])
    return best == 'application/json' and \
        request.accept_mimetypes[best] > \
        request.accept_mimetypes['text/html']

def get_current_aware_date():
    zone = datetime.now(timezone.utc).astimezone().tzinfo
    date = datetime.now(tz=zone)
    return date
