# heroku by default sets WEB_CONCURRENCY=2
# see: https://devcenter.heroku.com/changelog-items/618
# which uvicorn picks up, unless we explicitly set --workers --1
# see https://www.uvicorn.org/deployment/
# we also need to bind to 0.0.0.0 otherwise heroku cannot route to our server
web: solara run glue_solara.app --port=$PORT --no-open --host=0.0.0.0 --workers 1
