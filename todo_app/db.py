import aiopg.sa
from sqlalchemy import (
    MetaData, Table, Column, ForeignKey,
    Integer, String, Date
)

from todo_app.security import generate_password_hash
from todo_app.settings import config
__all__ = ['users', 'task']

metadata = MetaData()

users = Table(
    'users', metadata,

    Column('id', Integer, primary_key=True),
    Column('username', String(64), nullable=False, unique=True),
    Column('email', String(120)),
    Column('password_hash', String(128), nullable=False)
)

task = Table(
    'task', metadata,

    Column('id', Integer, primary_key=True),
    Column('body', String(200), nullable=False),

    Column('user_id',
           Integer,
           ForeignKey('users.id'))
)


async def get_user_tasks(conn, user):
    result = await conn.execute(task
                                .select()
                                .where(task.c.user_id == user))
    return await result.fetchall()

async def delete_task(conn, id):
    await conn.execute(task.delete().where(
        task.c.id==id))
    

async def create_task(conn, task_body, user):
    result = await conn.execute(task.insert().values(
        body=task_body,
        user_id=user).returning(task.c.id, task.c.body))
    return await result.fetchone()


async def create_user(conn, form):
    result = await conn.execute(users.insert().values(
        username=form['username'],
        email=form.get('email', None),
        password_hash=generate_password_hash(form['password'])).returning(users.c.id, users.c.username))
    return await result.fetchone()


async def get_user_by_name(conn, username):
    result = await conn.execute(
        users
        .select()
        .where(users.c.username == username)
    )
    return await result.first()


async def get_user_by_id(conn, id):
    result = await conn.execute(
        users
        .select()
        .where(users.c.id == id)
    )
    return await result.first()


async def get_users(conn):
    records = await conn.fetch(
        users.select().order_by(users.c.id)
    )
    return records


async def pg_context(app):
    await init_db(app)
    yield

    app['db'].close()
    await app['db'].wait_closed()

DSN = "postgresql://{user}:{password}@{host}:{port}/{database}"


async def init_db(app):
    conf = app['config']['postgres']

    pool = await aiopg.sa.create_engine(
        database=conf['database'],
        user=conf['user'],
        password=conf['password'],
        host=conf['host'],
        port=conf['port'],
        minsize=conf['minsize'],
        maxsize=conf['maxsize'],
    )
    app['db'] = pool
    return pool
