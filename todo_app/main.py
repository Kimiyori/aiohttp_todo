import logging
import sys

import aiohttp_jinja2
import jinja2
from aiohttp import web
from aiohttp_security import SessionIdentityPolicy
from aiohttp_security import authorized_userid
from aiohttp_security import setup as setup_security
from aiohttp_session import setup as setup_session
from aiohttp_session.redis_storage import RedisStorage
import aioredis
from todo_app.db import pg_context,init_db
from todo_app.middlewares import setup_middlewares
from todo_app.routes import setup_routes
from todo_app.settings import config, BASE_DIR
from todo_app.db_auth import DBAuthorizationPolicy
import logging


async def setup_redis(app):

    pool = await aioredis.from_url("redis://redis:6379")

    async def close_redis(app):
        pool.close()
        await pool.wait_closed()

    app.on_cleanup.append(close_redis)
    app['redis_pool'] = pool
    return pool


async def current_user_ctx_processor(request):
    user = await authorized_userid(request)
    is_anonymous = not bool(user)
    data={'current_user': {'is_anonymous': is_anonymous}}
    if  not is_anonymous:
        data['current_user']['user_id']=user['user_id']
        data['current_user']['username']=user['user_name']
    return data


async def init_app():

    app = web.Application()

    app['config'] = config
    setup_routes(app)
    db_pool = await init_db(app)

    redis_pool = await setup_redis(app)
    setup_session(app, RedisStorage(redis_pool))
    # setup Jinja2 template renderer
    aiohttp_jinja2.setup(app,
                         loader=jinja2.FileSystemLoader(str(BASE_DIR / 'todo_app' / 'templates')),
                          context_processors=[current_user_ctx_processor],)

    # create db connection on startup, shutdown on exit
    setup_security(
        app,
        SessionIdentityPolicy(),
        DBAuthorizationPolicy(db_pool)
    )
    app.cleanup_ctx.append(pg_context)



    setup_middlewares(app)

    return app


async def main():
    logging.basicConfig(level=logging.DEBUG)

    app = await  init_app()
    return app
    #web.run_app(app)


#if __name__ == '__main__':
    #main()
