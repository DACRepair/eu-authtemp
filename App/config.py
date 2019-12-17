import os
import uuid

FLASK_HOST = str(os.getenv("FLASK_HOST", "127.0.0.1"))
FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))
FLASK_TITLE = str(os.getenv("FLASK_TITLE", "Twitch API Portal"))
FLASK_SECRET = str(os.getenv("FLASK_SECRET", str(uuid.uuid4())))
FLASK_DEBUG = str(os.getenv('FLASK_DEBUG', 'false')).lower() == "true"

DB_URI = str(os.getenv("DB_URI", "sqlite:///app.db"))

TWITCH_CLIENT = str(os.getenv("TWITCH_CLIENT"))
TWITCH_SECRET = str(os.getenv("TWITCH_SECRET"))
TWITCH_REDIRECT = str(os.getenv("TWITCH_REDIRECT", "http://{}:{}/callback".format(FLASK_HOST, FLASK_PORT)))
