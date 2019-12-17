import os
import requests
import uuid
import pprint
from flask import Flask, render_template, redirect, request, session, url_for
from flask_admin import Admin
from flask_bootstrap import Bootstrap
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy

from App.config import DB_URI, FLASK_TITLE, FLASK_SECRET, FLASK_DEBUG, TWITCH_CLIENT, TWITCH_SECRET, TWITCH_REDIRECT

base_dir = os.path.normpath(os.getcwd())
app = Flask(FLASK_TITLE,
            static_folder=os.path.normpath(base_dir + "/static"),
            template_folder=os.path.normpath(base_dir + "/templates"))

app.debug = FLASK_DEBUG
app.secret_key = FLASK_SECRET
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_TYPE'] = "sqlalchemy"
app.config['SESSION_SQLALCHEMY_TABLE'] = 'sessions'
app.config['TITLE'] = FLASK_TITLE

sql = SQLAlchemy(app)
app.config['SESSION_SQLALCHEMY'] = sql
app.config['SESSION_USE_SIGNER'] = False
admin = Admin(app)

Session(app)
Bootstrap(app)


class AuthTokens(sql.Model):
    __tablename__ = "auth_tokens"
    key = sql.Column(sql.Integer, primary_key=True, autoincrement=True)
    id = sql.Column(sql.Integer, unique=True)
    name = sql.Column(sql.String(255))
    scope = sql.Column(sql.String(2048))
    client = sql.Column(sql.String(255))
    secret = sql.Column(sql.String(255))
    code = sql.Column(sql.String(255))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/create-request", methods=['POST', 'GET'])
def create_request():
    state = str("{}-{}".format(str(request.form.get('twitchname')).lower(), str(uuid.uuid4()))).lstrip('--')
    session['state'] = state

    url = "https://id.twitch.tv/oauth2/authorize?response_type=code&client_id={}&redirect_uri={}&scope={}&state={}"
    scope = [
        "analytics:read:extensions",
        "analytics:read:games",
        "bits:read",
        "channel:read:subscriptions",
        "user:read:broadcast",
        "user:read:email",
        "channel_check_subscription",
        "channel_feed_read",
        "channel_read",
        "channel_subscriptions",
        "user_blocks_read",
        "user_read",
        "user_subscriptions",
        "viewing_activity_read",
        "chat:read",
        "whispers:read"
    ]
    url = url.format(TWITCH_CLIENT, TWITCH_REDIRECT, "+".join(scope), state)
    return redirect(url)


@app.route("/callback")
def callback():
    if request.args.get('state') == session['state']:
        scope = request.args.get('scope')
        code = request.args.get('code')
        with requests.Session() as rses:
            params = {
                "client_id": TWITCH_CLIENT,
                "client_secret": TWITCH_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": TWITCH_REDIRECT
            }
            token = rses.post("https://id.twitch.tv/oauth2/token", params=params).json()
        token = "OAuth {}".format(token['access_token'])
        with requests.Session() as rses:
            rses.headers.update({'Accept': 'application/vnd.twitchtv.v5+json', 'Authorization': token})
            rses.headers.update({'Client-ID': TWITCH_CLIENT})
            data = rses.get("https://api.twitch.tv/kraken")
            if data.status_code == 200:
                data = data.json()
                cnt = sql.session.query(AuthTokens).filter(AuthTokens.id == data['token']['user_id'])
                if cnt.count() > 0:
                    for record in cnt.all():
                        sql.session.delete(record)
                        sql.session.commit()
                sql.session.add(AuthTokens(id=data['token']['user_id'],
                                           name=data['token']['user_name'],
                                           scope=scope,
                                           client=TWITCH_CLIENT,
                                           secret=TWITCH_SECRET,
                                           code=code))
                sql.session.commit()
                session['user_id'] = int(data['token']['user_id'])
    return redirect("finished")


@app.route("/finished")
def finished():
    user_id = session['user_id']
    user_name = sql.session.query(AuthTokens).filter(AuthTokens.id == user_id).one()

    return render_template("finished.html", user_id=user_id, user_name=user_name.name)
