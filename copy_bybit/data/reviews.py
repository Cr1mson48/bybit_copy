import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class Review(SqlAlchemyBase):
    __tablename__ = 'reviews'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    time = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.Date,
                                     default=datetime.date.today)
