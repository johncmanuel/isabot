from isabot.firebase.setup import db

# Collections in Firestore:
# users, characters, collections (mounts, toys, etc), pvp


def create_document(collection_path: str, document_id: str, data: dict):
    doc_ref = db.collection(collection_path).document(document_id)
    doc_ref.set(data)
    return doc_ref


def read_document(collection_path: str, document_id: str):
    doc_ref = db.collection(collection_path).document(document_id)
    data = doc_ref.get().to_dict()
    return data


def update_document(collection_path: str, document_id: str, data: dict):
    doc_ref = db.collection(collection_path).document(document_id)
    doc_ref.update(data)
    return doc_ref


def delete_document(collection_path: str, document_id: str):
    document_ref = db.collection(collection_path).document(document_id)
    document_ref.delete()
