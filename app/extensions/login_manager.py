# app/extensions/login_manager.py
from flask_login import LoginManager

login_manager = LoginManager()
login_manager.login_view = 'auth_bp.login' # Aponta para o novo Blueprint

# Lógica do user_loader será definida no app_factory após a importação do modelo User