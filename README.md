# glue-solara

development installation requires **npm/nodejs**:

    $ pip install -e ".[dev]"
    $ pre-commit install

## Serve on local network

For this, we use [caddy](https://caddyserver.com/) as a reverse proxy. After [installing caddy](https://caddyserver.com/docs/install), run

```bash
$ caddy run
```
