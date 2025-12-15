# app/__init__.py (VERSÃO CORRIGIDA E COMPLETA)

from flask import Flask, redirect, url_for, current_app 
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager 
from app.config.config import Config, NAMING_CONVENTION 

# =================================================================
# 1. INSTANCIAÇÕES GLOBAIS
# =================================================================

db = SQLAlchemy()
migrate = Migrate() 

# Inicialização do Flask-Login
login_manager = LoginManager() 
login_manager.login_view = 'auth.login' 
login_manager.login_message = 'Por favor, faça login para acessar esta página.' 
login_manager.login_message_category = 'warning'

# =================================================================
# 2. IMPORTAÇÃO DOS MODELOS (GLOBAL para Alembic)
# =================================================================
# A importação é mantida aqui para que o Alembic os encontre.
try:
    # Estas importações devem ser mantidas
    from app.models.user import User # Necessária para o load_user E para o CLI
    from app.models.user import register_cli_commands # Importa a função CLI
    from app.models.service import Service
    from app.models.booking import Booking
    from app.models.schedule import Schedule
except ImportError as e:
    print(f"AVISO CRÍTICO: Verifique o caminho dos seus modelos: {e}") 

# =================================================================
# 3. FUNÇÃO CREATE_APP
# =================================================================

def create_app(config_class=Config):
    app = Flask(__name__)
    
    app.config.from_object(config_class)
    
    # Inicializa as extensões
    db.init_app(app)
    db.metadata.naming_convention = NAMING_CONVENTION 
    migrate.init_app(app, db, render_as_batch=True)
    login_manager.init_app(app)
    
    # -------------------------------------------------------------
    # REGISTRO DE COMANDOS CLI (NOVO)
    # -------------------------------------------------------------
    register_cli_commands(app) # <--- REGISTRA O COMANDO 'create-admin'
    
    # -------------------------------------------------------------
    # CONFIGURAÇÃO DO FLASK-LOGIN (LOADER)
    # -------------------------------------------------------------
    @login_manager.user_loader
    def load_user(user_id):
        try:
            with current_app.app_context(): 
                # Usa o modelo User importado globalmente
                return User.query.get(int(user_id))
        except RuntimeError:
            return None 

    # -------------------------------------------------------------
    # REGISTRO DOS BLUEPRINTS
    # -------------------------------------------------------------
    
    from app.blueprints.auth.routes import auth_bp
    from app.blueprints.client.routes import client_bp
    from app.blueprints.admin.routes import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(client_bp, url_prefix='/client') 
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # -------------------------------------------------------------
    # ROTA RAIZ E OUTRAS UTILS
    # -------------------------------------------------------------
    @app.route('/')
    def index_redirect():
        return redirect(url_for('auth.login'))
    
    @app.route('/home', endpoint='home_page')
    def home_page():
        return redirect(url_for('auth.login'))
        
    import datetime
    @app.context_processor
    def inject_now():
        return {'now': datetime.datetime.now}
            
    return app