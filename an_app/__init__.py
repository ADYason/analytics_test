import os
from elasticsearch import Elasticsearch
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
elastic_client = Elasticsearch(hosts=os.getenv('ELASTIC_HOST',
                               default='http://127.0.0.1:9200'), timeout=10)

from . import api_views, cli_commands
