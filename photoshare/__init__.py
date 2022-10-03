import os
import json

from flask import Flask, render_template, flash


CONFS = ("DEBUG", "RELEASE", "TEST")


def create_app(test_config: dict | None = None):
    app = Flask("photoshare", instance_relative_config=True)

    if (mode := os.getenv("CONF", None)) is None:
        raise RuntimeError(f"Could not find CONF env variable."
                           " Set to DEBUG, RELEASE, or TEST!")
    mode = mode.upper()
    if mode not in CONFS:
        raise ValueError(f"CONF must be one of: {','.join(CONFS)}")
    conf_file = f"{mode.lower()}_config.json"
    app.config.from_file(conf_file, load=json.load)

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOADS_FOLDER"], exist_ok=True)

    from . import sitemap
    app.register_blueprint(sitemap.blueprint)
    app.add_url_rule('/', endpoint="index")

    from . import image_database
    image_database.init_app(app)

    return app
