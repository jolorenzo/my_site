FROM python:2.7

RUN apt-get update && apt-get install -y \
		apache2 \
		nano \
		wget \
		python-dev \
		libapache2-mod-wsgi \
		gcc \
		libjansson4 \
		libhiredis0.10 \
		gettext \
		libz-dev \
		libjpeg-dev \
		libfreetype6-dev \
		cron \
	&& wget --quiet --output-document=/tmp/libcjose.deb https://github.com/pingidentity/mod_auth_openidc/releases/download/v2.0.0/libcjose_0.4.1-1_amd64.deb \
	&& wget --quiet --output-document=/tmp/oidc.deb https://github.com/pingidentity/mod_auth_openidc/releases/download/v2.0.0/libapache2-mod-auth-openidc_2.0.0-1_amd64.deb \
	&& dpkg -i /tmp/libcjose.deb /tmp/oidc.deb \
	&& rm -f /tmp/oidc.deb /tmp/libcjose.deb \
	&& rm -rf /var/lib/apt/lists/*

RUN a2enmod \
		auth_openidc \
		ssl \
		wsgi \
		authz_groupfile \
		rewrite \
		expires \
		proxy_http

ENV PYTHONUNBUFFERED 1

RUN mkdir /code
RUN mkdir /data
RUN mkdir /ifb
WORKDIR /code

ADD requirements.txt /code/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY ./script/docker-entrypoint.sh /
RUN chmod a+x /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]

# Make port 80 available to the world outside this container
EXPOSE 80


