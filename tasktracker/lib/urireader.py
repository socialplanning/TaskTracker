"""
Read settings from the config or build.ini
"""

from ConfigParser import ConfigParser
import os

def get_instance(app_conf):
    if app_conf.get('openplans_instance'):
        return app_conf['openplans_instance']
    if app_conf.get('openplans_build_ini'):
        conf = read_config(app_conf)
        return conf.get('applications', 'opencore uri')

def get_login_uri(app_conf):
    ## FIXME: this doesn't show up in build.ini at all
    if app_conf.get('login_uri'):
        return app_conf['login_uri']
    else:
        ## FIXME: should came_from be here somewhere?
        return '/login'
    
def get_homepage_uri(app_conf):
    if app_conf.get('homepage_uri'):
        return app_conf['homepage_uri']
    else:
        return '/'

def get_profile_uri(app_conf):
    if app_conf.get('profile_uri'):
        return app_conf['profile_uri']
    else:
        return '/people/%s/profile'

def read_config(app_conf):
    fn = app_conf.get('openplans_build_ini')
    if not fn:
        raise ValueError(
            "No openplans_build_ini setting was given")
    if not os.path.exists(fn):
        raise OSError(
            "The build.ini file %s doesn't exist" % fn)
    parser = ConfigParser()
    parser.read([fn])
    return parser
