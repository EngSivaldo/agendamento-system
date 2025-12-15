# app/config/config.py

import os
from dotenv import load_dotenv

load_dotenv()

# Convenção de nomenclatura para SQLAlchemy/Alembic
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

class Config:
    """Configuração base da aplicação."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'default_fallback_key_nao_usar_em_producao'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///instance/database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    if not os.path.exists('instance'):
        os.makedirs('instance')

class DevelopmentConfig(Config):
    """Configuração para ambiente de desenvolvimento."""
    DEBUG = True
    SQLALCHEMY_ECHO = True # Adicionado para debug

class TestingConfig(Config):
    """Configuração para ambiente de testes."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'