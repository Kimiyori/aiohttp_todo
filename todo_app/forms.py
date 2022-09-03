from todo_app import db
from todo_app.security import check_password_hash
import re


async def validate_login_form(conn, form:dict):

    username = form['username']
    password = form['password']
    if not username:
        return 'username is required'
    if not password:
        return 'password is required'

    user = await db.get_user_by_name(conn, username)
    if not user:
        return 'Invalid username'
    if not check_password_hash(password, user['password_hash']):
        return 'Invalid password'
    return user


async def validate_registration_form(conn,form:dict):

    username = form['username']
    password = form['password']
    email=form.get('email',None)
    if not username:
        return 'username is required'
    if not password:
        return 'password is required'
    if len(username) < 6:
        return 'Your nickname must be at least 6 characters'
    user = await db.get_user_by_name(conn, username)
    if user:
        return 'Given username already exist'
    check_pass = re.match(
        '^(?=.*\d)(?=.*[A-Z])(?=.*[a-z])(?=.*[^\w\d\s:])([^\s]){6,16}$', password)
    if check_pass is None:
        return 'Your password incorrect'
    if email and re.match('^([a-z0-9_\.-]+\@[\da-z\.-]+\.[a-z\.]{2,6})$',email):
        return 'Incorrect email'
    return None
