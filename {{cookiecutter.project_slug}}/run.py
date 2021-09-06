from {{ cookiecutter.project_slug }}.processors import app, db

db.connect()
app.include_routers()
server = app.server  # for running via uvicorn

if __name__ == '__main__':
    app.run()
