from flask_login import LoginManager

login_manager = LoginManager()

# 🔐 endpoint correto do blueprint de autenticação
login_manager.login_view = 'auth.login'
