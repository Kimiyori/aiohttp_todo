from aiohttp_security.abc import AbstractAuthorizationPolicy

from todo_app import db
from aiohttp import web

class DBAuthorizationPolicy(AbstractAuthorizationPolicy):

    def __init__(self, db_pool):
        self.db_pool = db_pool

    async def authorized_userid(self, identity):
        async with self.db_pool.acquire() as conn:
            user = await db.get_user_by_id(conn, identity['user_id'])
            if user:
                return identity

        return None

    async def permits(self, identity, permission, context=None):
        if identity is None:
            return False
        return True

IDENTITY_KEY = 'aiohttp_security_identity_policy'

async def remember(request, response, identity, **kwargs):
    identity_policy = request.config_dict.get(IDENTITY_KEY)
    if identity_policy is None:
        text = ("Security subsystem is not initialized, "
                "call aiohttp_security.setup(...) first")
        # in order to see meaningful exception message both: on console
        # output and rendered page we add same message to *reason* and
        # *text* arguments.
        raise web.HTTPInternalServerError(reason=text, text=text)
    await identity_policy.remember(request, response, identity, **kwargs)
