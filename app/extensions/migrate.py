# app/extensions/migrate.py
from flask_migrate import Migrate
from app.extensions.database import db

migrate = Migrate()