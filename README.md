This is the complete source for ZenTogether.com.

Python Dependencies:
Note that some libraries are not required, but involved in planned future development.

Django
PIL
django-allauth
django-ses
django-smtp-ssl
httplib2
oauth2
psycopg2 # for postgreSQL


Set up
====
To run ZenTogether locally, you'll need to:

Install PostgreSQL
-----
Get the binary package here:
http://www.postgresql.org/download/

Install psycopg2
----
get the archive from:
http://pypi.python.org/pypi/psycopg2

Install Django
---
$ pip install Django

To verify: at the Python prompt
>>> import django
>>> print django.get_version()
1.4

Install required modules:
----
django-allauth
	http://pypi.python.org/pypi/django-allauth/
django-uni-form
	https://github.com/pydanny/django-uni-form
django-email-confirmation
	https://github.com/jtauber/django-email-confirmation

Install GeoIP:
----
1) Get the GEOIP C library:
http://www.maxmind.com/download/geoip/api/c/
$ ./configure
$ make
$ make check
$ make install

2) Get the GEOIP Python API:
http://www.maxmind.com/download/geoip/api/python/

3) Get the GeoIP datasets:
http://www.maxmind.com/download/geoip/database/
You'll need GeoIP.dat.gz and GeoLiteCity.dat.gz
Unzip these into your geoip path
Change GEOIP_PATH in settings.py

Almost there:
---
Create database tables:
$ python manage.py syncdb

Load initial data fixtures:
$ python manage.py loaddata zen_fixtures.json

Run:
$ python manage.py runserver

