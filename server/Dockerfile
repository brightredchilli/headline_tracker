# start from base
FROM brightredchilli/uwsgi-nginx-flask:python3.5
MAINTAINER Ying Quan Tan <ying.quan.tan@gmail.com>

COPY Pipfile* /app/
RUN pipenv install --verbose --sequential
# copy our application code

COPY uwsgi.ini *.py /app/

COPY build/nginx.conf /etc/nginx/conf.d/nginx.conf

COPY static /app/static

COPY templates /app/templates

WORKDIR /app
# fetch app specific deps
ENV UWSGI_INI /app/uwsgi.ini

RUN echo "virtualenv = $(pipenv --venv)" >> uwsgi.ini

ENTRYPOINT []

CMD ["/usr/bin/supervisord"]



