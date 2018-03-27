WSGI file

import sys
import logging

logging.basicConfig(stream=sys.stderr)
sys.path.append('/var/www/catalog')
sys.path.append('/var/www/catalog/catalog')

from catalog import app as application
application.secret_key='super_secret_key'
