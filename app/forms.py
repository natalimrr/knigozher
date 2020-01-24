from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SubmitField, IntegerField, validators

class LoginForm(FlaskForm):
    login = StringField('Логин', [validators.DataRequired()])
    password = PasswordField('Пароль', [validators.DataRequired()])
    remember_me = BooleanField('Запомнить')
    submit = SubmitField('Войти')

class NewAccountForm(FlaskForm):
    login = StringField('Логин', [validators.DataRequired()])
    password = PasswordField('Пароль', [validators.DataRequired()])
    password_replay = PasswordField('Повторите пароль', [validators.DataRequired()])
    fio = StringField('ФИО', [validators.DataRequired()])
    email = StringField('Email', [validators.DataRequired(), validators.Email()])
    submit = SubmitField('Зарегистрироваться')

class ChoiceBookForm(FlaskForm):
    id = StringField('id')
    quantity = StringField('quantity')
    submit = SubmitField('Добавить книгу в корзину')

class IdForm(FlaskForm):
    id = StringField('id')
    submit = SubmitField('submit')

class NewBookForm(FlaskForm):
    isbn = IntegerField('ISBN', [validators.NumberRange(min=1000000000000, max=9999999999999)])
    title = StringField('Название книги', [validators.DataRequired()])
    categories = TextAreaField('Введите все категории через двоеточие с пробелом')
    authors = TextAreaField('Введите всех авторов через двоеточие с пробелом')
    price = IntegerField('Цена', [validators.DataRequired()])
    publishing_house = StringField('Издательство', [validators.DataRequired()])
    quantity_in_stock = IntegerField('Количество на складе', [validators.DataRequired()])
    image = StringField('Изображение обложки')
    description = TextAreaField('Краткое описание')
    submit = SubmitField('Добавить')

class ChangeBookForm(FlaskForm):
    price = IntegerField('Цена', [validators.DataRequired()])
    quantity_in_stock = IntegerField('Количество на складе', [validators.DataRequired()])
    image = StringField('Изображение обложки')
    description = TextAreaField('Краткое описание')
    submit = SubmitField('Изменить')

class NewOrderForm(FlaskForm):
    adress = StringField('Адрес', [validators.DataRequired()])
    submit = SubmitField('Оформить заказ')