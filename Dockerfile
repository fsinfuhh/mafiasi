FROM docker.io/debian:bookworm-slim

# Install base system dependencies
RUN apt update
# https://stackoverflow.com/questions/58160597/docker-fails-with-sub-process-usr-bin-dpkg-returned-an-error-code-1
RUN mkdir -p /usr/share/man/man1 /app/config
ENV DEBIAN_FRONTEND=noninteractive
RUN apt upgrade -y &&\
    apt install -y --no-install-recommends uwsgi uwsgi-plugin-python3 python3 python3-setuptools python3-pip gcc gettext \
    libldap-common libldap2-dev libsasl2-2 libsasl2-dev libgpgme11 libgpgme-dev python3-dev libgraphviz-dev graphviz libmagic-dev libjpeg-dev libjs-mathjax \
    make nginx supervisor pipenv python-is-python3

# add Pipfile seperate from other sources to take advantage of build caching
ADD Pipfile /app/src/Pipfile
ADD Pipfile.lock /app/src/Pipfile.lock
WORKDIR /app/src
RUN pipenv install --system --deploy --ignore-pipfile --extra-pip-args="--break-system-packages"
RUN pip3 install sentry-sdk --break-system-packages

# add remaining sources
ADD . /app/src

# Put configs in appropriate locations
RUN cp docker/nginx.conf /etc/nginx/sites-enabled/default && \
    cp docker/uwsgi.ini /etc/uwsgi/mafiasi-dashboard.ini && \
    cp docker/supervisor.conf /etc/supervisor/conf.d/app.conf

RUN mkdir -p /app/static/mathjax
RUN cp -rT /usr/share/javascript/mathjax /app/static/mathjax

# remove build dependencies
RUN apt purge -y gcc make libldap2-dev libsasl2-dev libgpgme-dev python3-dev libgraphviz-dev libjs-mathjax
RUN apt -y autoremove
RUN apt-get -y clean


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
