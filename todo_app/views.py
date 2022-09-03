import aiohttp_jinja2
from aiohttp import web
from todo_app import db
from todo_app.forms import validate_login_form, validate_registration_form
from aiohttp_security import forget
from todo_app.db_auth import remember


def redirect(router, route_name:str):
    location = router[route_name].url_for()
    return web.HTTPFound(location)


async def check_login(request):
    if getattr(request, 'user', None):
        raise redirect(request.app.router, 'index')


class RegistrationView(web.View):

    @aiohttp_jinja2.template('registration.html')
    async def get(self):
        await check_login(self.request)
        return {}

    @aiohttp_jinja2.template('registration.html')
    async def post(self):
        form = await self.request.post()
        async with self.request.app['db'].acquire() as conn:
            error: str | None = validate_registration_form(form)
            if error:
                return {'error': error}
            user: list(int,str)= await db.create_user(conn, form)
            user_data = {'user_id': user[0], 'user_name': user[1]}
            response = redirect(self.request.app.router, 'index')
            await remember(self.request, response, user_data)
            raise response


class LoginView(web.View):

    @aiohttp_jinja2.template('login.html')
    async def get(self):
        await check_login(self.request)
        return {}

    @aiohttp_jinja2.template('login.html')
    async def post(self):
        form = await self.request.post()

        async with self.request.app['db'].acquire() as conn:
            user: str | list(int,str) = await validate_login_form(conn, form)
            if isinstance(user, str):
                return {'error': user}
            response = redirect(self.request.app.router, 'index')
            user_data = {'user_id': user['id'],
                         'user_name': user['username']}
            await remember(self.request, response, user_data)

            raise response


async def logout(request):
    response = redirect(request.app.router, 'login')
    await forget(request, response)
    return response


async def delete_task(request):
    if request.method == 'POST':
        async with request.app['db'].acquire() as conn:
            form: dict(str,str) = await request.json()
            await db.delete_task(conn, form['id'])
            return web.json_response({})


async def create_task(request):

    if request.method == 'POST':
        async with request.app['db'].acquire() as conn:
            form: dict(str,str) = await request.json()
            task = await db.create_task(conn, form['task'], form['user_id'])
            return web.json_response({'id': task[0], 'body': task[1]})

async def update_task(request:web.Request):
    if request.method == 'POST':
        async with request.app['db'].acquire() as conn:
            form: dict(str,str) = await request.json()
            task = await db.update_task(conn, form['body'], form['id'])
            return web.json_response({ 'body': task[0]})



@aiohttp_jinja2.template('index.html')
async def index(request:web.Request):
    async with request.app['db'].acquire() as conn:
        records: dict(int,str) = await db.get_user_tasks(conn, request.user['user_id'])
        tasks = [dict(q) for q in records]
        return {'tasks': tasks}
