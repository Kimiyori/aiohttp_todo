
import pathlib
from todo_app.views import create_task,  index,  logout, delete_task,LoginView,RegistrationView,update_task

PROJECT_ROOT = pathlib.Path(__file__).parent

def setup_routes(app):
    app.router.add_get('/', index, name='index')

    app.router.add_view('/login', LoginView, name='login')
    app.router.add_view('/registration', RegistrationView, name='registration')
    app.router.add_get('/logout', logout, name='logout')
    
    app.router.add_post('/create_task', create_task, name='create_task')
    app.router.add_post('/delete_task', delete_task, name='delete_task')
    app.router.add_post('/update_task', update_task, name='update_task')
    setup_static_routes(app)

def setup_static_routes(app):
    app.router.add_static('/static/',
                          path=PROJECT_ROOT / 'static',
                          name='static')