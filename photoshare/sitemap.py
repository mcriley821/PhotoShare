import time
import math

from flask import (Blueprint, render_template, url_for, g, request, redirect,
                   flash, current_app, send_from_directory)
from werkzeug.datastructures import FileStorage

from photoshare.image_database import get_database
from os.path import basename, splitext, exists, abspath, join as joinpath


blueprint = Blueprint('sitemap', __name__, url_prefix='/')


@blueprint.route("/")
def index():
   db = get_database()

   cards = db.execute(
        "SELECT * FROM images ORDER BY created DESC LIMIT 6"
    ).fetchall()

   return render_template("index.html", cards=cards)


@blueprint.get("/upload")
def upload():
    return render_template("upload.html")


ALLOWED_EXTS = (".jpg", ".jpeg", ".heic", ".png", ".gif", ".mov", ".mp4")


def is_file_allowed(file: FileStorage) -> bool:
    fname = file.filename
    return (
        basename(fname) == fname and splitext(fname)[1].lower() in ALLOWED_EXTS
    )


@blueprint.post("/upload")
def post_upload():
    files = request.files.getlist("files")
    if not files:
        flash("No files selected...")
        return redirect(url_for("sitemap.upload"))

    uploads = current_app.config["UPLOADS_FOLDER"]
    for file in filter(is_file_allowed, files):
        ext = splitext(file.filename)[1].lower()
        if ext in  (".mov", ".mp4"):
            fname = f"video_{time.time_ns():.0f}{ext}"
        else:
            fname = f"image_{time.time_ns():.0f}{ext}"
        try:
            db = get_database()
            db.execute(
                "INSERT INTO images (source_path) VALUES (?)", (fname,)
            )
            db.commit()
        except:
            continue
        else:
            file.save(joinpath(uploads, fname))

    return redirect(url_for("sitemap.upload"))


@blueprint.get("/uploads/<path:filename>")
def uploads(filename: str):
    uploads = current_app.config["UPLOADS_FOLDER"]
    return send_from_directory(abspath(uploads), filename)


@blueprint.route("/album")
def album():
    db = get_database()
    images = db.execute("SELECT * FROM images").fetchall()
    page_max = math.ceil(len(images) / 25)
    try: 
        requested_page = int(request.args.get("page"))
        if not 0 < requested_page <= page_max:
            raise ValueError
    except ValueError:
        page_range = range(1, page_max if page_max < 6 else 6)
        return render_template(
            "album.html",
            page_range=page_range,
            page_max=page_max,
            active_index=1,
            cards=[])

    cards = images[(requested_page - 1) * 25:requested_page * 25]
    if requested_page <= 3:
        page_low = 1
        page_high = 5 if page_max > 5 else page_max
    elif requested_page >= page_max - 3:
        page_low = 1 if page_max - 5 < 1 else page_max - 4
        page_high = page_max
    else:
        page_low = requested_page - 2
        page_high = requested_page + 2
    
    page_range = range(page_low, page_high + 1)
    return render_template("album.html", 
                           page_range=page_range,
                           page_max=page_max,
                           active_index=requested_page,
                           cards=cards)

