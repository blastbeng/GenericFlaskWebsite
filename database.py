import os
import sys
import logging
from io import BytesIO
from sqlalchemy import create_engine
from sqlalchemy import create_engine, insert, select, Table, Column, Integer, String, Float, BLOB, MetaData, ForeignKey

SQLITE          = 'sqlite'
USERS           = 'users'
PRODUCTS        = 'products'
LOCATIONS       = 'locations'
GLOBAL_DATA     = 'global_data'
IMAGES          = 'images'

class Database:
  DB_ENGINE = {
      SQLITE: 'sqlite:///config/{DB}'
  }

  # Main DB Connection Ref Obj
  db_engine = None
  def __init__(self, dbtype, username='', password='', dbname=''):
    dbtype = dbtype.lower()
    engine_url = self.DB_ENGINE[dbtype].format(DB=dbname)
    self.db_engine = create_engine(engine_url)

  metadata = MetaData()

  users = Table(USERS, metadata,
                Column('id', Integer, primary_key=True, autoincrement=True),
                Column('username', String, nullable=False),
                Column('password', String, nullable=False),
                Column('role', String, nullable=False)
                )

  global_data = Table(GLOBAL_DATA, metadata,
                Column('id', Integer, primary_key=True, autoincrement=True),
                Column('key', String, nullable=False),
                Column('value', String, nullable=False)
                )

  images = Table(IMAGES, metadata,
                Column('id', Integer, primary_key=True, autoincrement=True),
                Column('key', String, nullable=False),
                Column('value', BLOB, nullable=False)
                )

  locations = Table(LOCATIONS, metadata,
                Column('id', Integer, primary_key=True, autoincrement=True),
                Column('country', String, nullable=False),
                Column('region', String)
                )

  products = Table(PRODUCTS, metadata,
                Column('id', Integer, primary_key=True, autoincrement=True),
                Column('id_locations', None, ForeignKey('locations.id')),
                Column('name', String, nullable=False),
                Column('description', String),
                Column('type', Integer, nullable=False),
                Column('price', Float, nullable=False),
                Column('tms_insert', String, nullable=False)
                )

def create_db_tables(self):
  try:
    self.metadata.create_all(self.db_engine)
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)

def print_all_data(self, table='', query=''):
  query = query if query != '' else "SELECT * FROM '{}';".format(table)
  print(query)
  with self.db_engine.connect() as connection:
    try:
      result = connection.execute(query)
    except Exception as e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
    else:
      for row in result:
        print(row) # print(row[0], row[1], row[2])
        result.close()
  print("\n")


def insert_init_data(self):
  try:
    insert_init_data_images(self)
    insert_init_data_texts(self)
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)

def insert_init_data_images(self):
  directory = "config/init_data/images"
  for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    if os.path.isfile(f):
      if select_image(self, filename) is None:
        with open(f, "rb") as fh:
          stmt = insert(self.images).values(key=filename, value=fh.read()).prefix_with('OR IGNORE')
          compiled = stmt.compile()
          with self.db_engine.connect() as conn:
            result = conn.execute(stmt)
            conn.commit()

def insert_init_data_texts(self):
  for init_name, value in os.environ.items():
    if init_name.startswith("INIT_"):
      name = init_name.replace("INIT_", "").lower()
      if select_text(self, name) is None:
        stmt = insert(self.global_data).values(key=name, value=value).prefix_with('OR IGNORE')
        compiled = stmt.compile()
        with self.db_engine.connect() as conn:
          result = conn.execute(stmt)
          conn.commit()

def select_image(self, value: str):
  try:
    image = None
    stmt = select(self.images.c.value).where(self.images.c.key==value)
    compiled = stmt.compile()
    with self.db_engine.connect() as conn:
      cursor = conn.execute(stmt)
      records = cursor.fetchall()

      for row in records:
        data   =  row[0]
        image = BytesIO(data)
        cursor.close()
      
      return image
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)

def select_text(self, value: str):
  try:
    text = None
    stmt = select(self.global_data.c.value).where(self.global_data.c.key==value)
    compiled = stmt.compile()
    with self.db_engine.connect() as conn:
      cursor = conn.execute(stmt)
      records = cursor.fetchall()

      for row in records:
        text   =  row[0]
        cursor.close()
      
      return text
  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)