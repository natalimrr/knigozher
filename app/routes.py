# -*- coding: utf-8 -*-
from app import app, conn
from flask import render_template, flash, redirect, url_for, request
from app.forms import LoginForm, NewAccountForm, ChoiceBookForm, IdForm, NewBookForm, ChangeBookForm, NewOrderForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import logout_user, login_required, login_user, current_user
from app.models import load_user, User
from datetime import date
import os

cursor = conn.cursor()

id_book = None

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Книгожер')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('Вы уже авторизированны!')
        return redirect(url_for('cart'))
    form = LoginForm()
    if form.validate_on_submit():
        cursor.execute('select id, password_hash from account where login = %s;', (form.login.data,))
        user = cursor.fetchone()
        if user is None or not check_password_hash(user[1], form.password.data):
            flash('Неверный логин или пароль!')
            return redirect(url_for('login'))
        login_user(load_user(user[0]), remember=form.remember_me.data)
        flash('Вы успешно авторизировались.')
        return redirect(url_for('cart'))
    return render_template('login.html', title='Вход', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из аккаунта.')
    return redirect(url_for('login'))

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if current_user.is_authenticated:
        flash('У вас уже есть аккаунт!')
        return redirect(url_for('cart'))
    form = NewAccountForm()
    if form.validate_on_submit():
        cursor.execute('select * from account where login = %s or email = %s;', (form.login.data, form.email.data,))
        user = cursor.fetchone()
        if user:
            flash('Аккаунт с таким логином или email уже существует!')
            return redirect(url_for('create_account'))
        if form.password.data == form.password_replay.data:
            cursor.execute('insert into account (email, login, password_hash, fio) values (%s, %s, %s, %s);', (form.email.data, form.login.data, generate_password_hash(form.password.data), form.fio.data,))
            conn.commit()
        else:
            flash('Пароли не совпадают!')
            return redirect(url_for('create_account'))
        cursor.execute('select id from account where login = %s;', (form.login.data,))
        user_id = cursor.fetchone()
        if user_id:
            login_user(load_user(user_id[0]))
            flash('Вы успешно зарегистрировали новый аккаунт!')
            return redirect(url_for('cart'))
    return render_template('create_account.html', title='Регистрация', form=form)

@app.route('/cart', methods=['GET', 'POST'])
@login_required
def cart():
    form = IdForm()
    cursor.execute('select * from book_in_cart where id_account = %s order by id_book asc;', (current_user.id,))
    books_in_cart = cursor.fetchall()
    cursor.execute('select * from book where id in (select id_book from book_in_cart where id_account = %s);', (current_user.id,))
    books = cursor.fetchall()
    cursor.execute('select * from author_book where id_book in (select id_book from book_in_cart where id_account = %s);', (current_user.id,))
    authors_books = cursor.fetchall()
    cursor.execute('select * from author;')
    authors = cursor.fetchall()
    cursor.execute('select * from category_book where id_book in (select id_book from book_in_cart where id_account = %s);', (current_user.id,))
    categories_books = cursor.fetchall()
    cursor.execute('select * from category;')
    categories = cursor.fetchall()
    cursor.execute('select sum(book.price * book_in_cart.quantity) from book_in_cart inner join book on book_in_cart.id_book = book.id group by book_in_cart.id_account having book_in_cart.id_account = %s;', (current_user.id,))
    price = cursor.fetchone()
    if form.validate_on_submit():
        cursor.execute('delete from book_in_cart where id_book = %s and id_account = %s;', (form.id.data, current_user.id,))
        conn.commit()
        flash('Книга удалена из корзины!')
        return redirect(url_for('cart'))
    return render_template('cart.html', form=form, title='Корзина', books_in_cart=books_in_cart, books=books, authors_books=authors_books, authors=authors, categories_books=categories_books, categories=categories, price=price)

@app.route('/change_book', methods=['GET', 'POST'])
@login_required
def change_book():
    if current_user.id != 1:
        flash('Данная страница не доступна для Вас!')
        return redirect(url_for('index'))
    global id_book
    if id_book == None:
        flash('Вы не выбрали книгу для изменения!')
        return redirect(url_for('books'))
    form = ChangeBookForm()
    if form.validate_on_submit():
        cursor.execute('update book set price = %s, quantity_in_stock = %s, image = %s, description = %s where id = %s;', (form.price.data, form.quantity_in_stock.data, form.image.data, form.description.data, id_book,))
        conn.commit()
        flash('Данные изменены!')
        id_book = None
        return redirect(url_for('books'))
    elif request.method == 'GET':
        cursor.execute('select price, quantity_in_stock, image, description from book where id = %s;', (id_book,))
        book = cursor.fetchone()
        form.price.data = book[0]
        form.quantity_in_stock.data = book[1]
        form.image.data = book[2]
        form.description.data = book[3]
    return render_template('new_book.html', title='Редактирование книги', form=form)

@app.route('/new_book', methods=['GET', 'POST'])
@login_required
def new_book():
    if current_user.id != 1:
        flash('Данная страница не доступна для Вас!')
        return redirect(url_for('index'))
    form = NewBookForm()
    if form.validate_on_submit():
        cursor.execute('select id from book where isbn= %s;', (form.isbn.data,))
        book = cursor.fetchone()
        if book is None:
            cursor.execute('insert into book (isbn, title, price, publishing_house, quantity_in_stock, image, description) values(%s, %s, %s, %s, %s, %s, %s);', (form.isbn.data, form.title.data, form.price.data, form.publishing_house.data, form.quantity_in_stock.data, form.image.data, form.description.data,))
            cursor.execute('select id from book where isbn= %s;', (form.isbn.data,))
            id_book = cursor.fetchone()
            conn.commit()
            authors = form.authors.data.split('; ')
            categories = form.categories.data.split('; ')
            for author in authors:
                cursor.execute('select id from author where fio= %s;', (author,))
                id_author = cursor.fetchone()
                if id_author is None:
                    cursor.execute('insert into author (fio) values(%s);', (author,))
                    cursor.execute('select id from author where fio= %s;', (author,))
                    id_author = cursor.fetchone()
                    conn.commit()
                cursor.execute('insert into author_book (id_book, id_author) values(%s, %s);', (id_book, id_author,))
                conn.commit()
            for category in categories:
                cursor.execute('select id from category where title = %s;', (category,))
                id_category = cursor.fetchone()
                if id_category is None:
                    cursor.execute('insert into category (title) values(%s);', (category,))
                    cursor.execute('select id from category where title = %s;', (category,))
                    id_category = cursor.fetchone()
                    conn.commit()
                cursor.execute('insert into category_book (id_book, id_category) values(%s, %s);', (id_book, id_category,))
                conn.commit()
            flash('Книга добавлена в базу!')
            return redirect(url_for('books'))
        else:
            flash('По номеру ISBN уже существует книга в базе!')
            return redirect(url_for('new_book'))
    return render_template('new_book.html', title='Добавление книги в базу', form=form)

@app.route('/active_orders', methods=['GET', 'POST'])
@login_required
def active_orders():
    form = IdForm()
    if current_user.id == 1:
        cursor.execute('select id, fio from account where id in (select id_account from order_ where date_of_completion is null);')
        accounts = cursor.fetchall()
        cursor.execute('select * from order_ where date_of_completion is null order by id desc;')
    else:
        accounts = None
        cursor.execute('select * from order_ where id_account = %s and date_of_completion is null order by id desc;', (current_user.id,))
    orders = cursor.fetchall()
    if current_user.id == 1:
        cursor.execute('select * from book_in_order where id_order in (select id from order_ where date_of_completion is null);')
    else:
        cursor.execute('select * from book_in_order where id_order in (select id from order_ where id_account = %s and date_of_completion is null);', (current_user.id,))
    books_in_orders = cursor.fetchall()
    if current_user.id == 1:
        cursor.execute('select * from book where id in (select id_book from book_in_order where id_order in (select id from order_ where date_of_completion is null));')
    else:
        cursor.execute('select * from book where id in (select id_book from book_in_order where id_order in (select id from order_ where id_account = %s and date_of_completion is null));', (current_user.id,))
    books = cursor.fetchall()
    if current_user.id == 1:
        cursor.execute('select * from author_book where id_book in (select id_book from book_in_order where id_order in (select id from order_ where date_of_completion is null));')
    else:
        cursor.execute('select * from author_book where id_book in (select id_book from book_in_order where id_order in (select id from order_ where id_account = %s and date_of_completion is null));', (current_user.id,))
    authors_books = cursor.fetchall()
    cursor.execute('select * from author;')
    authors = cursor.fetchall()
    if current_user.id == 1:
        cursor.execute('select * from category_book where id_book in (select id_book from book_in_order where id_order in (select id from order_ where date_of_completion is null));')
    else:
        cursor.execute('select * from category_book where id_book in (select id_book from book_in_order where id_order in (select id from order_ where id_account = %s and date_of_completion is null));', (current_user.id,))
    categories_books = cursor.fetchall()
    cursor.execute('select * from category;')
    categories = cursor.fetchall()
    if form.validate_on_submit():
        cursor.execute('update order_ set date_of_completion = %s where id = %s;', (date.today(), form.id.data,))
        conn.commit()
        flash('Заказ выполнен!')
        return redirect(url_for('orders'))
    return render_template('orders.html', title='Активные заказы', form=form, orders=orders, accounts=accounts, books_in_orders=books_in_orders, books=books, authors_books=authors_books, authors=authors, categories_books=categories_books, categories=categories)

@app.route('/orders', methods=['GET', 'POST'])
@login_required
def orders():
    form = None
    if current_user.id == 1:
        cursor.execute('select id, fio from account;')
        accounts = cursor.fetchall()
        cursor.execute('select * from order_ order by id desc;')
    else:
        accounts = None
        cursor.execute('select * from order_ where id_account = %s order by id desc;', (current_user.id,))
    orders = cursor.fetchall()
    if current_user.id == 1:
        cursor.execute('select * from book_in_order;')
    else:
        cursor.execute('select * from book_in_order where id_order in (select id from order_ where id_account = %s);', (current_user.id,))
    books_in_orders = cursor.fetchall()
    if current_user.id == 1:
        cursor.execute('select * from book where id in (select id_book from book_in_order);')
    else:
        cursor.execute('select * from book where id in (select id_book from book_in_order where id_order in (select id from order_ where id_account = %s));', (current_user.id,))
    books = cursor.fetchall()
    if current_user.id == 1:
        cursor.execute('select * from author_book where id_book in (select id_book from book_in_order);')
    else:
        cursor.execute('select * from author_book where id_book in (select id_book from book_in_order where id_order in (select id from order_ where id_account = %s));', (current_user.id,))
    authors_books = cursor.fetchall()
    cursor.execute('select * from author;')
    authors = cursor.fetchall()
    if current_user.id == 1:
        cursor.execute('select * from category_book where id_book in (select id_book from book_in_order);')
    else:
        cursor.execute('select * from category_book where id_book in (select id_book from book_in_order where id_order in (select id from order_ where id_account = %s));', (current_user.id,))
    categories_books = cursor.fetchall()
    cursor.execute('select * from category;')
    categories = cursor.fetchall()
    return render_template('orders.html', title='Все заказы', form=form, orders=orders, accounts=accounts, books_in_orders=books_in_orders, books=books, authors_books=authors_books, authors=authors, categories_books=categories_books, categories=categories)

@app.route('/new_order', methods=['GET', 'POST'])
@login_required
def new_order():
    form = NewOrderForm()
    cursor.execute('select * from book_in_cart where id_account = %s;', (current_user.id,))
    books_in_cart = cursor.fetchall()
    cursor.execute('select * from book where id in (select id_book from book_in_cart where id_account = %s);', (current_user.id,))
    books = cursor.fetchall()
    cursor.execute('select * from author_book where id_book in (select id_book from book_in_cart where id_account = %s);', (current_user.id,))
    authors_books = cursor.fetchall()
    cursor.execute('select * from author;')
    authors = cursor.fetchall()
    cursor.execute('select * from category_book where id_book in (select id_book from book_in_cart where id_account = %s);', (current_user.id,))
    categories_books = cursor.fetchall()
    cursor.execute('select * from category;')
    categories = cursor.fetchall()
    cursor.execute('select sum(book.price * book_in_cart.quantity) from book_in_cart inner join book on book_in_cart.id_book = book.id group by book_in_cart.id_account having book_in_cart.id_account = %s;',(current_user.id,))
    price = cursor.fetchone()
    if form.validate_on_submit():
        cursor.execute('insert into order_ (date_of_registration, price, adress, id_account) values(%s, %s, %s, %s);', (date.today(), price, form.adress.data, current_user.id,))
        cursor.execute('select max(id) from order_ where id_account = %s;', (current_user.id,))
        id_order = cursor.fetchone()
        for book_in_cart in books_in_cart:
            cursor.execute('insert into book_in_order (id_book, id_order, quantity) values (%s, %s, %s);', (book_in_cart[0], id_order, book_in_cart[2],))
            cursor.execute('delete from book_in_cart where id_book = %s and id_account = %s;', (book_in_cart[0], current_user.id,))
        conn.commit()
        flash('Заказ принят в обработку!')
        return redirect(url_for('active_orders'))
    return render_template('new_order.html', title='Проверка заказа', form=form, books_in_cart=books_in_cart, books=books, authors_books=authors_books, authors=authors, categories_books=categories_books, categories=categories, price=price)

@app.route('/books', methods=['GET', 'POST'])
def books():
    if current_user.is_authenticated:
        form = ChoiceBookForm()
    else:
        form = None
    cursor.execute('select * from book order by id desc;')
    books = cursor.fetchall()
    cursor.execute('select * from author_book;')
    authors_books = cursor.fetchall()
    cursor.execute('select * from author;')
    authors = cursor.fetchall()
    cursor.execute('select * from category_book;')
    categories_books = cursor.fetchall()
    cursor.execute('select * from category;')
    categories = cursor.fetchall()
    if form is not None and form.validate_on_submit():
        if current_user.id != 1:
            cursor.execute('select quantity_in_stock from book where id = %s;', (form.id.data,))
            quantity_in_stock = cursor.fetchone()
            if quantity_in_stock[0] < int(form.quantity.data):
                flash('На складе нет такого количества данной книги!')
                return redirect(url_for('books'))
            cursor.execute('select * from book_in_cart where id_book = %s and id_account = %s;', (form.id.data, current_user.id,))
            book_in_cart = cursor.fetchone()
            if book_in_cart:
                cursor.execute('update book_in_cart set quantity = %s where id_book = %s and id_account = %s;', (book_in_cart[2] + int(form.quantity.data), form.id.data, current_user.id,))
                conn.commit()
                flash('Количество данных книг увеличено!')
            else:
                cursor.execute('insert into book_in_cart (id_book, id_account, quantity) values (%s, %s, %s);', (form.id.data, current_user.id, form.quantity.data,))
                conn.commit()
                flash('Книга добавлена в корзины!')
            return redirect(url_for('books'))
        else:
            global id_book
            id_book = form.id.data
            return redirect(url_for('change_book'))
    return render_template('books.html', title='Книги', form=form, books=books, authors_books=authors_books, authors=authors, categories_books=categories_books, categories=categories)
