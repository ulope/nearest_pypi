from datetime import datetime
from urlparse import urlunsplit
import arrow
from flask.app import Flask
from flask.globals import request
from flask.templating import render_template
from redis.client import StrictRedis
from werkzeug.utils import redirect
from models import Mirror
from logging import getLogger

log = getLogger(__name__)


app = Flask(__name__)
app.config.from_object("config.Config")

if 'SENTRY_DSN' in app.config:
    from raven.contrib.flask import Sentry
    sentry = Sentry(app)

redis = StrictRedis(app.config['REDIS']['HOST'], app.config['REDIS']['PORT'], app.config['REDIS']['DB'])


@app.route("/")
def index():
    remote_addr = request.remote_addr
    if app.config['DEBUG'] and request.args.get('_IP'):
        remote_addr = request.args.get('_IP')

    if remote_addr.startswith("::ffff:"):
        remote_addr = remote_addr.replace("::ffff:", "")

    distances = Mirror.get_mirror_distances(remote_addr)
    context = {
        'ip': remote_addr,
        'last_update': arrow.get(redis.get(app.config['KEY_LAST_UPDATE']))
    }
    if distances:
        nearest_mirror = next(distances.iteritems())
        context['mirror'] = nearest_mirror[0]
        context['mirror_distance'] = nearest_mirror[1]
        context['distances'] = distances
    else:
        context['no_mirror'] = True
        context['fallback_mirror'] = app.config['FALLBACK_MIRROR']
    return render_template("index.html", **context)


@app.route("/simple/")
@app.route("/simple/<path:path>")
def proxy(path=""):
    remote_addr = request.remote_addr
    if app.config['DEBUG'] and request.args.get('_IP'):
        remote_addr = request.args.get('_IP')

    mirror = Mirror.get_nearest_mirror(remote_addr)
    url = urlunsplit((
        "http",
        mirror,
        "simple/{}".format(path),
        request.query_string,
        None
    ))
    log.debug("Redirecting to %s", url)
    return redirect(url)


if __name__ == "__main__":
    app.run("0.0.0.0", 8000, debug=True)
