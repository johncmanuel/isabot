# NOTE: As of 12/24/23, there is an ongoing open issue regarding type annotations
# for functions in the firestore_admin library:
# https://github.com/firebase/firebase-admin-python/issues/626
# I will be using the workaround provided in the issue to type annotate
# Firestore Client.

from firebase_admin import firestore, initialize_app
from firebase_admin.credentials import Certificate
from google.cloud.firestore import Client as FirestoreClient

from env import FIREBASE_CLIENT_EMAIL, FIREBASE_PRIVATE_KEY, FIREBASE_PROJECT_ID

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

initialize_app(credential=certificate)

db: FirestoreClient = firestore.client()
