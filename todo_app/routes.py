
import pathlib
from todo_app.views import create_task,  index, login, logout, registration,delete_task

PROJECT_ROOT = pathlib.Path(__file__).parent

def setup_routes(app):
    app.router.add_get('/', index, name='index')
    app.router.add_get('/login', login, name='login')
    app.router.add_post('/login', login, name='login')
    app.router.add_get('/registration', registration, name='registration')
    app.router.add_post('/registration', registration, name='registration')
    # app.router.add_get('/create_task', create_task, name='create_task')
    # app.router.add_post('/create_task', create_task, name='create_task')
    app.router.add_post('/create_task', create_task, name='create_task')
    app.router.add_post('/delete_task', delete_task, name='delete_task')
    app.router.add_get('/logout', logout, name='logout')
    setup_static_routes(app)

def setup_static_routes(app):
    app.router.add_static('/static/',
                          path=PROJECT_ROOT / 'static',
                          name='static')