# app/app_factory.py

from flask import Flask
from app.config.config import DevelopmentConfig
import os 
import datetime # 🌟 NOVO: Importe o módulo datetime para o rodapé do base.html

def create_app(config_class=DevelopmentConfig):
    # 1. Inicialização do App e Configuração
    app = Flask(__name__, instance_relative_config=True) 
    app.config.from_object(config_class)

    # 2. Inicialização de Extensões (CRÍTICO)
    from app.extensions.database import db
    from app.extensions.migrate import migrate
    from app.extensions.login_manager import login_manager
    
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # 3. Configuração do Flask-Login e Comandos CLI (Dentro do Contexto)
    with app.app_context():
        from app.models.user import User, register_cli_commands
        from app.extensions.database import db

        # 🔐 Loader correto e compatível com SQLAlchemy 2.x
        @login_manager.user_loader
        def load_user(user_id):
            return db.session.get(User, int(user_id))

        register_cli_commands(app)


    # 🌟 4. INJEÇÃO DE CONTEXTO GLOBAL (Para o Rodapé) 🌟
    # Adiciona a função 'now()' ao contexto do Jinja para usar em templates (ex: rodapé)
    @app.context_processor
    def inject_global_variables():
        return {
            'now': datetime.datetime.now
        }

    # 5. Registro de Blueprints (CRÍTICO)
    # Garante que as rotas sejam carregadas a partir dos subdiretórios 'routes.py'
    from app.blueprints.auth.routes import auth_bp
    from app.blueprints.client.routes import client_bp
    from app.blueprints.admin.routes import admin_bp
    
    # 🛑 NOTA IMPORTANTE: Mantive os nomes de endpoint curtos (auth, client, admin)
    # se o nome do Blueprint dentro do routes.py estiver correto.
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(client_bp, url_prefix='/')
    app.register_blueprint(admin_bp, url_prefix='/admin') 

    return app