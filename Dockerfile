FROM alpine:3.16

# Install base system dependencies
RUN apk add build-base uwsgi python3-dev py3-pip openldap-dev gettext mathjax2 nginx supervisor gpgme-dev graphviz-dev py3-wheel
RUN pip install pipenv

# add Pipfile seperate from other sources to take advantage of build caching
ADD Pipfile /app/src/Pipfile
ADD Pipfile.lock /app/src/Pipfile.lock
WORKDIR /app/src
ENV PIPENV_VENV_IN_PROJECT=1
RUN pipenv install --deploy --ignore-pipfile

# add remaining sources
ADD . /app/src

# Put configs in appropriate locations
RUN cp docker/nginx.conf /etc/nginx/http.d/default.conf && \
    cp docker/uwsgi.ini /etc/uwsgi/mafiasi-dashboard.ini && \
    cp docker/supervisor.conf /etc/supervisord.conf

RUN mkdir -p /app/static/
RUN cp -rT /usr/share/mathjax2 /app/static/mathjax

# Configure Image Metadata
ENTRYPOINT ["/app/src/docker/entrypoint.sh"]
CMD supervisord -n -c /etc/supervisor/supervisord.conf -u root
ENV LANG=en_US.UTF-8
ENV HOME=/app
ENV MAFIASI_MEDIA_ROOT=/app/media
ENV MAFIASI_STATIC_ROOT=/app/static/django

# user uploaded content (like gprot) get put here
VOLUME /app/media
# pks keyring
VOLUME /app/.gnupg
# http
EXPOSE 8000
