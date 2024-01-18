from typing import Optional

from google.cloud.firestore import AsyncCollectionReference, AsyncDocumentReference

from isabot.firebase.setup import db


def collection_ref(collection_path: str) -> AsyncCollectionReference:
    return db.collection(collection_path)


def document_ref(
    collection_path: str, document_id: Optional[str]
) -> AsyncDocumentReference:
    if not document_id:
        return collection_ref(collection_path).document()
    return collection_ref(collection_path).document(document_id)


async def create_document(
    collection_path: str,
    document_id: Optional[str],
    data: dict,
    include_autogen_id_field: bool = False,
):
    doc_ref = document_ref(collection_path, document_id)
    if include_autogen_id_field:
        data["id"] = doc_ref.id
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
