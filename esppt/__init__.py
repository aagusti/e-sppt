from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from pyramid.renderers import JSON
import datetime    
from esppt.models.model_base import (
    DBSession,
    Base,
    )

from esppt.models.other_base import (
    OtherDBSession,
    OtherBase,
    )

from esppt_route import esppt_route

def add_route(config, rc):
    for c, v in rc:
        config.add_route(c, v)

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    OtherEngine = engine_from_config(settings, 'othersql.')
    OtherEngine.echo=False
    OtherDBSession.configure(bind=OtherEngine)
    OtherBase.metadata.bind = OtherEngine
    
    os_session_factory = UnencryptedCookieSessionFactoryConfig('itsaseekreet')
    
    config = Configurator(settings=settings, session_factory = os_session_factory)
    
    config.include('pyramid_chameleon')
    
    json_renderer = JSON()
    def datetime_adapter(obj, request):
        return obj.isoformat()
    json_renderer.add_adapter(datetime.datetime, datetime_adapter)
    config.add_renderer('json', json_renderer)
    
    #config.add_renderer('json', JSON(indent=0))    
    
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('deform_static', 'deform:static')

    config.add_route('home', '/home')
    config.add_route('login', '/')
    config.add_route('login_it', '/login_it')
    config.add_route('logout', '/logout')
    config.add_route('lupa', '/lupa')
    config.add_route('change', '/change')

    add_route(config, esppt_route)
 
    config.scan()
    
    return config.make_wsgi_app()
    
