#!/usr/bin/python

## These two lines are needed to run on EL6
__requires__ = ['SQLAlchemy >= 0.7', 'jinja2 >= 2.4']
import pkg_resources

from fedocal import APP
from fedocal.fedocallib import model

model.create_tables(APP.config['DB_URL'],
    APP.config['PATH_ALEMBIC_INI'], True)
