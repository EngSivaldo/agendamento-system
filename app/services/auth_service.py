from app.models.user import User
from app.extensions.database import db

def create_user(email: str, password_hash: str) -> User:
    """
    Cria um novo usuário no sistema.
    Regra de negócio: não é responsabilidade da rota nem do model.
    """
    user = User(
        email=email,
        password_hash=password_hash
    )

    db.session.add(user)
    db.session.commit()

    return user
