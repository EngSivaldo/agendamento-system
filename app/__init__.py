# app/__init__.py (VERSÃO FINAL OTIMIZADA E CORRIGIDA)

from flask import Flask, redirect, url_for, current_app 
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager 
from app.config.config import Config, NAMING_CONVENTION 
import datetime # Importado aqui para o context_processor

# =================================================================
# 1. INSTANCIAÇÕES GLOBAIS
# =================================================================

db = SQLAlchemy()
migrate = Migrate() 
login_manager = LoginManager() 
login_manager.login_view = 'auth.login' 
login_manager.login_message = 'Por favor, faça login para acessar esta página.' 
login_manager.login_message_category = 'warning'

# =================================================================
# 2. FUNÇÃO CREATE_APP
# =================================================================

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # -------------------------------------------------------------
    # 2.1. INICIALIZAÇÃO DE EXTENSÕES
    # -------------------------------------------------------------
    db.init_app(app)
    db.metadata.naming_convention = NAMING_CONVENTION 
    migrate.init_app(app, db, render_as_batch=True)
    login_manager.init_app(app)
    
    # -------------------------------------------------------------
    # 2.2. CARREGAMENTO DE MODELOS E CONFIGURAÇÃO DO FLASK-LOGIN
    # -------------------------------------------------------------
    # Garante que os modelos sejam carregados antes de qualquer uso relacionado a DB
    with app.app_context():
        # Importa todos os módulos de modelos para registro no SQLAlchemy/Migrate
        # e garante que o objeto User esteja acessível no load_user.
        try:
            # Importação Mestra:
            from app.models import user, service, booking, schedule
            
            # Importação Específica de User e CLI para uso local
            from app.models.user import User, register_cli_commands
            
        except ImportError as e:
            app.logger.error(f"Erro ao carregar modelos: {e}")
            return app # Retorna o app se a falha de importação for crítica
            
        # 🚨 CONFIGURAÇÃO DO FLASK-LOGIN (LOADER) 🚨
        # Definido DENTRO do contexto de create_app, mas AGORA a classe User é conhecida
        @login_manager.user_loader
        def load_user(user_id):
            # A classe User está acessível aqui devido à importação acima.
            # return db.session.get(User, int(user_id)) # Método mais moderno do SQLAlchemy 2.0
            return User.query.get(int(user_id)) 

        # REGISTRO DE COMANDOS CLI
        if 'register_cli_commands' in locals():
             register_cli_commands(app)


    # -------------------------------------------------------------
    # 2.3. REGISTRO DOS BLUEPRINTS
    # -------------------------------------------------------------
    
    # Imports de Blueprints
    from app.blueprints.auth.routes import auth_bp
    from app.blueprints.client.routes import client_bp
    from app.blueprints.admin.routes import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(client_bp, url_prefix='/client') 
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # -------------------------------------------------------------
    # 2.4. ROTAS RAIZ E PROCESSADORES DE CONTEXTO
    # -------------------------------------------------------------
    
    @app.route('/')
    @app.route('/home', endpoint='home_page') # Consolida rotas de raiz
    def index_redirect():
        # A rota 'auth.login' deve estar resolvida agora que o Blueprint foi registrado
        return redirect(url_for('auth.login'))
    
    
    @app.context_processor
    def inject_now():
        return {'now': datetime.datetime.now}
            
    return app