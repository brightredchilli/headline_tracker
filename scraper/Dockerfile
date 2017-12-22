FROM python:3.5.4-alpine


RUN apk --update \
add \
bash \
wget \
build-base \
jpeg-dev \
zlib-dev \
&& rm -rf /var/cache/apk/*


RUN addgroup deploy && \
adduser -D deploy -G deploy

RUN mkdir /app && mkdir /images
COPY Pipfile* /app/
COPY *.py /app/

RUN chown -R deploy:deploy /app* && \
chmod -R u+rwx /app && \
chown -R deploy:deploy /images* && \
chmod -R u+rwx /images

WORKDIR /app
RUN pip install pipenv==8.3

#USER deploy

RUN pipenv install --verbose


CMD ["pipenv", "run", "python", "who_is_watching.py"]




# ARG PUID
# ARG PGID
#
# RUN addgroup -g ${PGID} abc && \
#     adduser -D -u ${PUID} -G abc abc

