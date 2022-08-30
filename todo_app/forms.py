from todo_app import db
from todo_app.security import check_password_hash


async def validate_login_form(conn, form):

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

async def validate_registration_form(form):

    username = form['username']
    password = form['password']
    if not username:
        return 'username is required'
    if not password:
        return 'password is required'
    if len(username)<6:
        return 'Your nickname must be at least 6 characters'
    if len(password)<6:
        return 'Your password must be at least 6 characters'
    return None