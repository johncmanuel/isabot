from firebase_admin import firestore, initialize_app
from firebase_admin.credentials import Certificate

from env import (
    FIREBASE_CLIENT_EMAIL,
    FIREBASE_DB_URL,
    FIREBASE_PRIVATE_KEY,
    FIREBASE_PROJECT_ID,
)

certificate = Certificate(
    {
        "type": "service_account",
        "token_uri": "https://oauth2.googleapis.com/token",
        "project_id": FIREBASE_PROJECT_ID,
        "client_email": FIREBASE_CLIENT_EMAIL,
        # Fix: https://github.com/firebase/firebase-admin-python/issues/188#issuecomment-410350471
        "private_key": FIREBASE_PRIVATE_KEY.replace("\\n", "\n"),
    }
)

firebase = initialize_app(
    credential=certificate, options={"databaseURL": FIREBASE_DB_URL}
)

db = firestore.client()
