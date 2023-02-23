

import os
import logging
import requests
import random
import sys
import shutil
import database
import utils
from datetime import datetime
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import Flask, request, send_file, Response, jsonify, render_template, make_response, after_this_request, g
from flask_restx import Api, Resource, reqparse
from flask_caching import Cache
from pathlib import Path
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=int(os.environ.get("LOG_LEVEL")),
        datefmt='%Y-%m-%d %H:%M:%S')
log = logging.getLogger('werkzeug')
log.setLevel(int(os.environ.get("LOG_LEVEL")))

dbms = database.Database(database.SQLITE, dbname='database.sqlite3')

app = Flask(__name__)
class Config:    
    CACHE_TYPE = os.environ['CACHE_TYPE']
    CACHE_REDIS_HOST = os.environ['CACHE_REDIS_HOST']
    CACHE_REDIS_PORT = os.environ['CACHE_REDIS_PORT']
    CACHE_REDIS_DB = os.environ['CACHE_REDIS_DB']
    CACHE_REDIS_URL = os.environ['CACHE_REDIS_URL']
    CACHE_DEFAULT_TIMEOUT = os.environ['CACHE_DEFAULT_TIMEOUT']

INIT_SITENAME = os.environ['INIT_SITENAME']

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/second"],
    storage_uri="memory://",
)

app.config.from_object(Config())
cache = Cache(app)
api = Api(app)

nsutils = api.namespace('utils', INIT_SITENAME + ' Utils APIs')

@nsutils.route('/healthcheck')
class Healthcheck(Resource):
  def get (self):
    return "OK"


nsengine = api.namespace('engine', INIT_SITENAME + ' Engine APIs')

@nsengine.route('/get_image/<string:text>')
class GetImageClass(Resource):
  @cache.cached(timeout=7200, query_string=True)
  def get (self, text: str):
    try:
      data = database.select_image(dbms, text)
      if data is not None:
        return send_file(data, attachment_filename=text, mimetype=utils.guess_mymetype(text))
      else:
        @after_this_request
        def clear_cache(response):
          cache.delete_memoized(GetImageClass.get, self, str, str, str)
          return make_response("Failed to retrieve image!", 500)
    except Exception as e:
      g.request_error = str(e)
      @after_this_request
      def clear_cache(response):
        cache.delete_memoized(GetImageClass.get, self, str, str, str)
        return make_response(g.get('request_error'), 500)

@app.route('/index')
def index():
  return render_template('index.html', sitename=database.select_text(dbms, "sitename"),
                                       slogan=database.select_text(dbms, "slogan"),
                                       about_us=database.select_text(dbms, "about_us"),
                                       about_name=database.select_text(dbms, "about_name"),
                                       about_description=database.select_text(dbms, "about_description"),
                                       our_menu=database.select_text(dbms, "our_menu"),
                                       our_menu_name=database.select_text(dbms, "our_menu_name"))
  
cache.init_app(app)
limiter.init_app(app)

database.create_db_tables(dbms)
database.insert_init_data(dbms)

if __name__ == '__main__':
  app.run()
