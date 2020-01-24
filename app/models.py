# -*- coding: utf-8 -*-
from app import app, conn
from flask_login import LoginManager, UserMixin

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, id, email, login, password_hash, fio):
        self.id = id
        self.email = email
        self.login = login
        self.password_hash = password_hash
        self.fio = fio

    def __repr__(self):
        return '<User {}>'.format(self.login)

@login_manager.user_loader
def load_user(user_id):
    cursor = conn.cursor()
    cursor.execute("select * from account where id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    if user:
        return User(user[0], user[1], user[2], user[3], user[4])
    else:
        return None