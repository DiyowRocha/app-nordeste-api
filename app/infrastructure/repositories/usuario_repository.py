from datetime import datetime

from sqlalchemy.orm import Session

from app.infrastructure.models.usuario import UsuarioModel


class UsuarioRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def buscar_por_email(self, email: str) -> UsuarioModel | None:
        return self._db.query(UsuarioModel).filter(UsuarioModel.email == email).first()

    def buscar_por_id(self, usuario_id: int) -> UsuarioModel | None:
        return self._db.query(UsuarioModel).filter(UsuarioModel.id == usuario_id).first()

    def criar(self, model: UsuarioModel) -> UsuarioModel:
        self._db.add(model)
        self._db.flush()
        self._db.refresh(model)
        return model

    def atualizar(self, model: UsuarioModel) -> UsuarioModel:
        self._db.flush()
        self._db.refresh(model)
        return model

    def anonimizar(self, usuario_id: int) -> None:
        """Anonimiza dados pessoais do usuário (direito ao esquecimento LGPD)."""
        model = self.buscar_por_id(usuario_id)
        if model:
            model.nome = f"ANONIMIZADO_{usuario_id}"
            model.email = f"anonimizado_{usuario_id}@excluido.com"
            model.senha_hash = ""
            model.ativo = False
            self._db.flush()
