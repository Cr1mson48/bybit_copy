import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class Orders(SqlAlchemyBase):
    __tablename__ = 'orders'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    id_users = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    order_id = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    profit = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    symbol = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    qty = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    price_input = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    price_mark = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    #liquid = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    side = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    status = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.Date,
                                     default=datetime.date.today)
