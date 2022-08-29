import aiohttp_jinja2
from aiohttp import web
from aiohttp_security import forget, authorized_userid
from todo_app import db
from todo_app.forms import validate_login_form
from todo_app.security import generate_password_hash
import aiohttp_session
from todo_app.db_auth import remember


def redirect(router, route_name):
    location = router[route_name].url_for()
    return web.HTTPFound(location)




async def delete_task(request):
    if request.method == 'POST':
        async with request.app['db'].acquire() as conn:
            form = await request.json()
            await db.delete_task(conn, form['id'])
            return web.json_response({})

async def create_task(request):

    if request.method == 'POST':
        async with request.app['db'].acquire() as conn:
            form = await request.json()
            task = await db.create_task(conn, form['task'], form['user_id'])
            return web.json_response({'id': task[0], 'body': task[1]})


@aiohttp_jinja2.template('index.html')
async def index(request):
    async with request.app['db'].acquire() as conn:
        session = await aiohttp_session.get_session(request)
        records = await db.get_user_tasks(conn, session['AIOHTTP_SECURITY']['user_id'])
        tasks = [dict(q) for q in records]
        return {'tasks': tasks}


@aiohttp_jinja2.template('login.html')
async def login(request):
    username = await authorized_userid(request)
    if username:
        raise redirect(request.app.router, 'index')

    if request.method == 'POST':
        form = await request.post()

        async with request.app['db'].acquire() as conn:
            error = await validate_login_form(conn, form)

            if error:
                return {'error': error}
            else:
                response = redirect(request.app.router, 'index')

                user = await db.get_user_by_name(conn, form['username'])
                user_data = {'user_id': user['id'],
                             'user_name': user['username']}
                await remember(request, response, user_data)

                raise response

    return {}


async def logout(request):
    response = redirect(request.app.router, 'login')
    await forget(request, response)
    return response


@aiohttp_jinja2.template('registration.html')
async def registration(request):
    username = await authorized_userid(request)
    if username:
        raise redirect(request.app.router, 'index')

    if request.method == 'POST':
        form = await request.post()

        async with request.app['db'].acquire() as conn:
            user = await db.create_user(conn, form)
            user_data = {'user_id': user[0], 'user_name': user[1]}
            response = redirect(request.app.router, 'index')
            await remember(request, response, user_data)
            raise response

    return {}
