# app/__init__.py (VERSÃO FINAL CORRIGIDA PARA FLASK CONTEXTO)

from flask import Flask, redirect, url_for, current_app 
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager 
from app.config.config import Config, NAMING_CONVENTION 

# =================================================================
# 1. INSTANCIAÇÕES GLOBAIS (APENAS INSTÂNCIAS DE EXTENSÃO)
# =================================================================

db = SQLAlchemy()
migrate = Migrate() 

# Inicialização do Flask-Login
login_manager = LoginManager() 
login_manager.login_view = 'auth.login' 
login_manager.login_message = 'Por favor, faça login para acessar esta página.' 
login_manager.login_message_category = 'warning'

# =================================================================
# 2. BLOCO DE IMPORTAÇÃO DE MODELOS REMOVIDO PARA EVITAR CYCLES
# =================================================================
# Os modelos serão importados localmente ou no contexto da aplicação.


# =================================================================
# 3. FUNÇÃO CREATE_APP
# =================================================================

def create_app(config_class=Config):
    app = Flask(__name__)
    
    app.config.from_object(config_class)
    
    # -------------------------------------------------------------
    # 3.1. INICIALIZAÇÃO DE EXTENSÕES (db.init_app deve ser o primeiro)
    # -------------------------------------------------------------
    db.init_app(app)
    db.metadata.naming_convention = NAMING_CONVENTION 
    migrate.init_app(app, db, render_as_batch=True)
    login_manager.init_app(app)
    
    # -------------------------------------------------------------
    # 3.2. CARREGAMENTO DE MODELOS E COMANDOS CLI (DENTRO DO CONTEXTO)
    # -------------------------------------------------------------
    with app.app_context():
        # Importa todos os modelos. Isso é necessário para:
        # 1. Garantir que o Flask-Migrate os encontre
        # 2. Permitir que o user_loader e o CLI os usem.
        try:
            from app.models import user, service, booking, schedule
            from app.models.user import User, register_cli_commands # Importa User e a função CLI
        except ImportError as e:
            # Em caso de erro, avisa e permite que o resto da aplicação tente rodar.
            app.logger.error(f"Erro ao carregar modelos para Alembic/CLI: {e}")
            
        # REGISTRO DE COMANDOS CLI
        # Verifica se a função CLI foi importada antes de tentar usá-la.
        if 'register_cli_commands' in locals():
            register_cli_commands(app)
        else:
            app.logger.warning("Comandos CLI não registrados. Verifique a importação do user.py.")


    # -------------------------------------------------------------
    # 3.3. CONFIGURAÇÃO DO FLASK-LOGIN (LOADER)
    # -------------------------------------------------------------
    @login_manager.user_loader
    def load_user(user_id):
        # O modelo User JÁ FOI importado no contexto acima. 
        # Acesso direto deve funcionar agora, pois o DB já foi inicializado.
        try:
            # Não é necessário usar 'with current_app.app_context()' aqui, 
            # pois o Flask-Login garante o contexto na chamada do load_user.
            return User.query.get(int(user_id))
        except NameError:
             # Retorna None se User não foi definido (em caso de falha de importação grave)
             return None 
        except Exception:
             return None


    # -------------------------------------------------------------
    # 3.4. REGISTRO DOS BLUEPRINTS
    # -------------------------------------------------------------
    
    from app.blueprints.auth.routes import auth_bp
    from app.blueprints.client.routes import client_bp
    from app.blueprints.admin.routes import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(client_bp, url_prefix='/client') 
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # -------------------------------------------------------------
    # 3.5. ROTA RAIZ E OUTRAS UTILS
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