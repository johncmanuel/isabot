from typing import Optional

from google.cloud.firestore import DocumentReference

from isabot.firebase.setup import db

# Collections in Firestore:
# users, characters, collections (mounts, toys, etc), pvp


def collection_ref(collection_path: str):
    return db.collection(collection_path)


def document_ref(collection_path: str, document_id: Optional[str]):
    if not document_id:
        return collection_ref(collection_path).document()
    return collection_ref(collection_path).document(document_id)


async def get_first_doc_in_collection(collection_path: str):
    ref = collection_ref(collection_path)

    # Only query one document from collection
    query = ref.limit(1)

    async for doc in query.stream():
        return doc.to_dict()


def is_document_exists(doc_ref: DocumentReference):
    return doc_ref.get().exists


async def create_document(collection_path: str, document_id: Optional[str], data: dict):
    doc_ref = document_ref(collection_path, document_id)
    await doc_ref.set(data)
    return doc_ref


async def read_document(collection_path: str, document_id: str):
    doc_ref = document_ref(collection_path, document_id)
    data = (await doc_ref.get()).to_dict()
    return data


async def update_document(collection_path: str, document_id: str, data: dict):
    doc_ref = document_ref(collection_path, document_id)
    await doc_ref.update(data)
    return doc_ref


async def delete_document(collection_path: str, document_id: str) -> bool:
    doc_ref = document_ref(collection_path, document_id)
    await doc_ref.delete()
    return not ((await doc_ref.get()).exists)
