from flask import Flask
from config import Config
from flask_bootstrap import Bootstrap
import psycopg2

app = Flask(__name__)
app.config.from_object(Config)
conn = psycopg2.connect(dbname='deiel9rufiolas', user='fufkwaqdskamvj', password='bdf6227a465b0e2af4b590e09c0b657ef5c03c75ca76499d4f0066f7fd30207b', host='ec2-54-228-246-214.eu-west-1.compute.amazonaws.com')
bootstrap = Bootstrap(app)

from app import routes