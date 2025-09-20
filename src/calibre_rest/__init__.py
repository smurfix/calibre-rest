import logging

from flask import Flask
from gunicorn.app.base import BaseApplication

from calibre_rest.calibre import CalibreWrapper
from .config import DevConfig

__version__ = "0.1.0"

LOG_FORMAT = "%(asctime)s %(name)s - %(levelname)s - %(message)s"


class GunicornApp(BaseApplication):
    defaults = {
        "bind": "localhost:5000",
        # calibredb supports only one operation at any single time. Increasing
        # the number of workers would result in concurrent execution errors.
        "workers": 1,
        "backlog": 100,
        "worker_class": "sync",
        "timeout": 30,
        "keepalive": 2,
        "spew": False,
        "daemon": False,
        "raw_env": [],
        "pidfile": "/tmp/gunicorn_vm_api.pid",
        "umask": 755,
        "user": 1000,
        "group": 1000,
        "tmp_upload_directory": None,
        # Log errors to stdout
        "error_log": "-",
        "access_log": "-",
    }

    def __init__(self, app_config):
        self.app = create_app(app_config)
        self.options = self.defaults

        bind_addr = app_config.get("bind_addr")
        if bind_addr is not None:
            self.options["bind"] = bind_addr
        super().__init__()

    def load_config(self):
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.app


def create_app(config=None):
    app = Flask(__name__)

    if config is None:
        config = DevConfig()

    app.config.update(config.config())
    app.testing = config.get("testing")
    app.debug = config.get("debug")

    # Only set for dev runs as it does not work well with
    # Docker or reverse proxy
    if isinstance(config, DevConfig):
        app.config["SERVER_NAME"] = config.get("bind_addr")

    # attach gunicorn log handlers if exist
    flog = app.logger
    gunicorn_handlers = logging.getLogger("gunicorn").handlers
    flog.handlers.extend(gunicorn_handlers)
    flog.setLevel(app.config["log_level"])

    app.logger.debug(f"Server config: {config.config()}")

    try:
        cdb = CalibreWrapper(
            app.config["calibredb"],
            app.config["library"],
            app.config["username"],
            app.config["password"],
            flog,
        )
        cdb.check()
        app.config["CALIBRE_WRAPPER"] = cdb
    except FileNotFoundError as exc:
        # exit immediately if fail to initialize wrapper object
        raise SystemExit(exc)

    with app.app_context():
        import calibre_rest.routes  # noqa: F401

    return app
