# -*- coding: utf-8 -*-

"""
For uniformity with normal Python behavior, by default web2py does not
reload modules when changes are made. Yet this can be changed. To turn on
the auto-reload feature for modules, use the track_changes function as follows
(typically in a model file, before any imports):
"""
from gluon.custom_import import track_changes
track_changes(True)
"""
From now on, every time a module is imported, the importer will check if
the Python source file (.py) has changed. If it has changed, the module will
be reloaded.
"""

from gluon.tools import Service
service = Service()
