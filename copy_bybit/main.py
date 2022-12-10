import csv
from pybit import usdt_perpetual
from data import db_session
from data.reviews import Review
from data.users import User
import time
import threading
from data.orders import Orders
from data.api_account import Api_account
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, render_template, url_for, redirect, request, make_response
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
#position: absolute; left:25%; width: 50%; margin: 10;
from funs import pcheck
from flask_apscheduler import APScheduler
from smtplib import SMTP
import logging

application = Flask(__name__)
application.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(application)
logging.basicConfig(level=logging.INFO, filename="py_log.log",filemode="w")

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)




def main():
    db_session.global_init("db/data.db")
    c = threading.Thread(target=thread_function)
    x = threading.Thread(target=check_orders)
    c.start()
    x.start()
    application.run(host='0.0.0.0')

def thread_function():
    pos = []
    ord = {}
    db_sess = db_session.create_session()
    info = db_sess.query(Api_account).filter((Api_account.id == 1)).first()
    logging.basicConfig(filename="pybit.log", level=logging.DEBUG,
                        format="%(asctime)s %(levelname)s %(message)s")
    print('Работает')

    print(info.api)

    ws_linear = usdt_perpetual.WebSocket(
        test=False,
        api_key=info.api,
        api_secret=info.secret
    )

    def order_msg(message):
        print(message)
        account = db_sess.query(Api_account).filter((Api_account.id != 1)).all()

        for j in account:
            try:
                #if ord[message['data'][0]['symbol']] == message['data'][0]['side']:
                order = Orders(id_users=j.id_acc, order_id=message['data'][0]['order_id'], profit=0, symbol=message['data'][0]['symbol']
                       , price_input=message['data'][0]['last_exec_price'], price_mark=message['data'][0]['last_exec_price'], side=message['data'][0]['side'],
                       status=message['data'][0]['order_status'], qty=message['data'][0]['qty'])
                #else:
                #    orders = db_sess.query(Orders).filter((Orders.id != 0)).all()
                #    for f in orders:
                #        if f.symbol == message['data'][0]['symbol'] and f.side != message['data'][0]['side'] and f.status != 'Заполнено':
                #            f.order_id = message['data'][0]['order_id']
            except Exception as e:
                print(e)
            #    order = Orders(id_users=j.id_acc, order_id=message['data'][0]['order_id'], profit=0,
            #                   symbol=message['data'][0]['symbol']
            #                   , price_input=message['data'][0]['last_exec_price'],
            #                   price_mark=message['data'][0]['last_exec_price'], side=message['data'][0]['side'],
            #                   status=message['data'][0]['order_status'], qty=message['data'][0]['qty'])
            try:
                db_sess.add(order)
                db_sess.commit()
            except Exception as e:
                print(e)

        for i in account:
            print(i.api, i.secret)
            try:
                #print('-----------------')
                #print(message['data'][0]['order_id'])
                #print(pos)
                #print(message['data'][0]['order_status'])
                #print('-----------------')
                if message['data'][0]['order_id'] in pos and message['data'][0]['order_status'] == 'Cancelled':
                    session_auth = usdt_perpetual.HTTP(
                        endpoint="https://api.bybit.com",
                        api_key=i.api,
                        api_secret=i.secret
                    )
                    print(session_auth.cancel_all_active_orders(
                        symbol=message['data'][0]['symbol'],
                    ))

                else:
                    session_auth = usdt_perpetual.HTTP(
                        endpoint="https://api.bybit.com",
                        api_key=i.api,
                        api_secret=i.secret
                    )
                    try:
                        print(session_auth.set_leverage(
                            symbol=message['data'][0]['symbol'],
                            buy_leverage=20,
                            sell_leverage=20
                        ))
                    except Exception:
                        pass
                    print(session_auth.place_active_order(
                        symbol=message['data'][0]['symbol'],
                        side=message['data'][0]['side'],
                        order_type=message['data'][0]['order_type'],
                        price=message['data'][0]['price'],
                        qty=message['data'][0]['qty'],
                        stop_loss=message['data'][0]['stop_loss'],
                        take_profit=message['data'][0]['take_profit'],
                        time_in_force="GoodTillCancel",
                        position_idx=message['data'][0]['position_idx'],
                        reduce_only=message['data'][0]['reduce_only'],
                        close_on_trigger=message['data'][0]['close_on_trigger']
                    ))
                    pos.append(message['data'][0]['order_id'])
                    ord[message['data'][0]['symbol']] = message['data'][0]['side']
            except Exception as e:
                print(e)
    ws_linear.order_stream(order_msg)

    while True:
        time.sleep(1)



def check_orders():
    db_sess = db_session.create_session()
    while True:
        try:
            session_unauth = usdt_perpetual.HTTP(
                endpoint="https://api.bybit.com"
            )
            account = db_sess.query(Api_account).filter((Api_account.id == 1)).first()
            orders = db_sess.query(Orders).filter((Orders.id != 0)).all()
            session_auth = usdt_perpetual.HTTP(
                endpoint="https://api.bybit.com",
                api_key=account.api,
                api_secret=account.secret
            )
            for i in orders:
                price = session_unauth.latest_information_for_symbol(
                    symbol=i.symbol
                )['result'][0]['last_price']
                pnl = session_auth.closed_profit_and_loss(
                    symbol=i.symbol
                )
                print(f'pnl: {pnl}')
                for x in pnl['result']['data']:
                    #print(x)
                    #print(x['order_id'])
                    if x['order_id'] == i.order_id:
                        print(x['closed_pnl'])
                        i.profit = x['closed_pnl']
                        i.status = 'Закрыто'
                #print(price)
                k = float(i.price_input) / float(price)
                #print(k)
                profit = 100 / (k * 10)
                #print(profit)
                order = session_auth.get_active_order(
                    symbol=i.symbol
                )
                #print(order)
                if i.status != 'Закрыто':
                    i.price_mark = price
                    db_sess.commit()
                    time.sleep(1)
        except Exception as e:
            print(e)




@application.route('/', methods=['GET', 'POST'])
@application.route('/index', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated == False:
        return redirect('/create-account')
    db_sess = db_session.create_session()
    #test_job()

    db_sess = db_session.create_session()
    # print(current_user.email)
    if request.method == 'POST':
        db_sess = db_session.create_session()
        api = request.form['api-key']
        secret = request.form['secret-key']
        api_acc = Api_account(id_acc=current_user.id, api=api, secret=secret)
        try:
            if db_sess.query(Api_account).filter((Api_account.id_acc == current_user.id)).all():
                user = db_sess.query(Api_account).filter((Api_account.id_acc == current_user.id)).first()
                user.api = api
                user.secret = secret
                db_sess.commit()
                return redirect('/')
            db_sess.add(api_acc)
            db_sess.commit()
            return redirect('/')
        except Exception as e:
            print(e)
            return "При добавление api произошла ошибка"
    db_sess = db_session.create_session()


    return render_template('index.html')




@application.route('/create-account', methods=['GET', 'POST'])
def register():
    return render_template('create-account.html')


@application.route('/create', methods=['POST'])
def create():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        password_again = request.form['password_again']

        print(email)
        print(password)
        print(password_again)

        if password != password_again:
            return redirect('/create-account')
            #Пароли не совпадают
        error = pcheck(password)
        if not error:
            return redirect('/create-account')
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == email).first():
            return redirect('/create-account')
        user = User(
            email=email,
        )
        user.set_password(password)
        db_sess.add(user)
        db_sess.commit()
        message = 'Вы зарегистрировались'
        return redirect('/index')
    else:
        return redirect('/create-account')



@application.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if current_user.is_authenticated:
            return redirect(url_for('index'))

        email = request.form['email']
        password = request.form['password']

        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect("/")
        return redirect(url_for('login'))
    else:
        return render_template('login.html')



@application.route('/store', methods=['GET', 'POST'])
def store():
    if current_user.is_authenticated == False:
        return redirect('/create-account')
    db_sess = db_session.create_session()
    orders = db_sess.query(Orders).filter((Orders.id_users == current_user.id)).all()
    return render_template('store.html', orders=orders)


@application.route("/logout")
def logout():
    logout_user()
    return redirect("/index")

if __name__ == '__main__':
    main()