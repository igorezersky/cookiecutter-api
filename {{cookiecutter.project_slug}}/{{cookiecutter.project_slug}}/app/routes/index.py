from fastapi import APIRouter, Request, status
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse, PlainTextResponse, RedirectResponse

from {{ cookiecutter.project_slug }}.processors import app

router = APIRouter()


@router.get('/', include_in_schema=False)
async def index(request: Request) -> RedirectResponse:
    return await app.render_template('index.html', request=request)


@router.get('/openapi.json', include_in_schema=False)
async def openapi():
    return JSONResponse(get_openapi(title='{{ cookiecutter.project_name }}', version='1.0.0', routes=app.server.routes))


@router.get('/docs', include_in_schema=False)
async def documentation():
    return get_swagger_ui_html(openapi_url=app.url_for('index.openapi'), title='docs')


@router.get('/healthcheck')
async def healthcheck():
    return PlainTextResponse(content='It works', status_code=status.HTTP_200_OK)
