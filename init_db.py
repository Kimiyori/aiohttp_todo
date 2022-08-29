from sqlalchemy import create_engine, MetaData

from todo_app.settings import config
from todo_app.db import users,task
from todo_app.security import generate_password_hash

DSN = "postgresql://{user}:{password}@{host}:{port}/{database}"
db_url = DSN.format(**config['postgres'])

def create_tables(engine):
    meta = MetaData()
    meta.create_all(bind=engine, tables=[users,task])



def get_engine(db_url):
    engine = create_engine(db_url, isolation_level='AUTOCOMMIT')
    return engine

def create_sample_data(db_url):
    engine = get_engine(db_url)

    with engine.connect() as conn:
        conn.execute(users.insert(), [
            {'username': 'test',
             'email': 'test@mail.com',
             'password_hash': generate_password_hash('maxmax17')},
        ])


if __name__ == '__main__':

    #engine = create_engine(db_url)

    #create_tables(engine)
    create_sample_data(db_url)
    