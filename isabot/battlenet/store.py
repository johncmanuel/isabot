from typing import Optional

import isabot.firebase.crud as crud

"""
Interface library with firestore module. Helps with interacting with the Firestore DB 
without knowing the firebase_admin library.  

TODO: refactor this file to create crud, wrapper functions for each collection. This would
reduce code duplication
"""


def store_access_token(name: str, token: dict):
    access_token_doc_ref = crud.create_document(
        name,
        token.get("sub", "None"),
        {
            "access_token": token.get("access_token"),
            "expires_at": token.get("expires_at"),
            "expires_in": token.get("expires_in"),
            "sub": token.get("sub"),
        },
    )
    return access_token_doc_ref


def get_access_token(token_id: str, collection_name: str = "authorization_flow_tokens"):
    token = crud.read_document(collection_name, token_id)
    return token


def delete_access_token(
    token_id: str, collection_name: str = "authorization_flow_tokens"
):
    return crud.delete_document(collection_name, token_id)


def store_bnet_userinfo(userinfo: dict, collection_name: str = "users"):
    userinfo_doc_ref = crud.create_document(
        collection_name, userinfo.get("sub", "None"), userinfo
    )
    return userinfo_doc_ref


def store_wow_accounts(
    collection_name: str, wow_accounts: dict, collection_path: str = "characters"
):
    ref = crud.create_document(collection_path, collection_name, wow_accounts)
    return ref


def store_cc_access_token(
    collection_name: str,
    token: dict,
    collection_path: str = "client_credentials_token",
):
    ref = crud.create_document(collection_path, collection_name, token)
    return ref


def store_len_mounts(
    collection_name: str, len_mounts: int, collection_path: str = "collection"
):
    ref = crud.create_document(
        collection_path, collection_name, {"number_of_mounts": len_mounts}
    )
    return ref


def store_pvp_data(collection_name: str, pvp_data: dict, collection_path: str = "pvp"):
    ref = crud.create_document(collection_path, collection_name, pvp_data)
    return ref


def get_data(collection_name: str, collection_path: str):
    d = crud.read_document(collection_path, collection_name)
    return d


def get_multiple_data(collection_path: str):
    """Returns all documents stored in a collection"""
    c = crud.collection_ref(collection_path)
    l: dict[str, dict] = {}
    for s in c.stream():
        d = s.to_dict()
        if not d:
            continue
        doc_id = s.id
        l[doc_id] = d
    return l


def store_data(
    data: dict,
    collection_path: str,
    collection_name: Optional[str] = None,
):
    """TODO: Use this to replace store_* functions"""
    d = crud.create_document(
        collection_path=collection_path, document_id=collection_name, data=data
    )
    return d
