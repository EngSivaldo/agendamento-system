from datetime import datetime
from app import db
from app.models.base import BaseMixin

class Booking(db.Model, BaseMixin):
    __tablename__ = 'agendamento'

    # =====================================================
    # CAMPOS
    # =====================================================
    id = db.Column(db.Integer, primary_key=True)

    # Data e hora do agendamento
    data_agendamento = db.Column('data', db.DateTime, nullable=False)

    status = db.Column(
        db.String(50),
        default='Pendente',
        nullable=False
    )

    # 🔥 SOFT DELETE
    deleted_at = db.Column(db.DateTime, nullable=True)

    # 🔥 AUDITORIA
    deleted_by = db.Column(
        db.Integer,
        db.ForeignKey('usuario.id'),
        nullable=True
    )
    deleted_reason = db.Column(db.String(255), nullable=True)

    # 🔗 CHAVES ESTRANGEIRAS
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('usuario.id'),
        nullable=False
    )

    service_id = db.Column(
        db.Integer,
        db.ForeignKey('servico.id'),
        nullable=False
    )

    schedule_id = db.Column(
        db.Integer,
        db.ForeignKey('schedule.id'),
        nullable=False
    )

    # =====================================================
    # RELACIONAMENTOS (🔥 TODOS AQUI DENTRO 🔥)
    # =====================================================

    # Dono do agendamento
    user = db.relationship(
        'User',
        foreign_keys=[user_id],
        back_populates='agendamentos'
    )

    # Usuário que realizou o delete (auditoria)
    deleted_by_user = db.relationship(
        'User',
        foreign_keys=[deleted_by],
        viewonly=True
    )

    # Serviço agendado
    servico = db.relationship(
        'Service',
        back_populates='agendamentos'
    )

    # Slot de agenda
    schedule_slot = db.relationship(
        'Schedule',
        back_populates='agendamentos'
    )

    # =====================================================
    # REGRAS DE NEGÓCIO
    # =====================================================

    def can_be_deleted(self, user):
        """
        Define se o agendamento pode ser excluído.
        Retorna (bool, mensagem).
        """

        if self.deleted_at is not None:
            return False, "Este agendamento já foi removido."

        if self.user_id != user.id and not user.is_admin:
            return False, "Você não tem permissão para excluir este agendamento."

        if self.status != 'Pendente':
            return False, "Somente agendamentos pendentes podem ser excluídos."

        if self.data_agendamento <= datetime.now():
            return False, "Não é possível excluir um agendamento já ocorrido."

        return True, None

    # =====================================================
    # AÇÕES
    # =====================================================

    def confirm(self):
        self.status = 'Confirmado'
        self.save()

    def cancel(self):
        self.status = 'Cancelado'
        self.save()

    def soft_delete(self, user_id, reason=None):
        self.deleted_at = datetime.utcnow()
        self.deleted_by = user_id
        self.deleted_reason = reason
        self.save()

    # =====================================================
    # REPRESENTAÇÃO
    # =====================================================

    def __repr__(self):
        return f'<Booking {self.id} - {self.data_agendamento} ({self.status})>'
