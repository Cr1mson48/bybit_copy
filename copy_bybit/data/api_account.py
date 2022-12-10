import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class Api_account(SqlAlchemyBase):
    __tablename__ = 'api_account'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    id_acc = sqlalchemy.Column(sqlalchemy.Integer)
    api = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    secret = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    def __repr__(self):
        return "<Api_account %r>" % self.id