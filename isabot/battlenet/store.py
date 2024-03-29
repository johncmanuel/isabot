from typing import Any, Dict, Optional, Union

import isabot.firebase.crud as crud

"""
Interface library with firestore module. Helps with interacting with the Firestore DB 
without knowing the firebase_admin library.  

TODO: refactor this file to create crud, wrapper functions for each collection. This would
reduce code duplication

TODO: move this module somewhere else that's not in the battlenet module
"""


async def store_access_token(name: str, token: dict):
    """Stores the AF (Authorization Flow) token into the database."""
    access_token_doc_ref = await crud.create_document(
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


async def get_access_token(
    token_id: str, collection_name: str = "authorization_flow_tokens"
) -> Union[Dict[str, Any], None]:
    """Gets the AF (Authorization Flow) token from the database."""
    token = await crud.read_document(collection_name, token_id)
    return token


async def delete_access_token(
    token_id: str, collection_name: str = "authorization_flow_tokens"
) -> bool:
    """Deletes the AF (Authorization Flow) token from the database."""
    return await crud.delete_document(collection_name, token_id)


async def store_bnet_userinfo(userinfo: dict, collection_name: str = "users"):
    """Stores the userinfo from the BattleNet OAuth flow into the database."""
    sub = userinfo.pop("sub", "None")
    userinfo["id"] = str(userinfo["id"])

    # Strip the unique identifier from the battletag for privacy reasons.
    # Plus, this would keep the bots from spamming the user with friend requests.
    userinfo["battletag"] = userinfo["battletag"].split("#")[0]

    userinfo_doc_ref = await crud.create_document(collection_name, sub, userinfo)
    return userinfo_doc_ref


async def store_wow_chars(
    collection_name: str, wow_accounts: dict, collection_path: str = "characters"
):
    ref = await crud.create_document(collection_path, collection_name, wow_accounts)
    return ref


async def store_cc_access_token(
    collection_name: str,
    token: dict,
    collection_path: str = "client_credentials_token",
):
    ref = await crud.create_document(collection_path, collection_name, token)
    return ref


async def store_len_mounts(
    collection_name: str, len_mounts: int, collection_path: str = "collection"
):
    ref = await crud.create_document(
        collection_path, collection_name, {"number_of_mounts": len_mounts}
    )
    return ref


async def store_pvp_data(
    collection_name: str, pvp_data: dict, collection_path: str = "pvp"
):
    ref = await crud.create_document(collection_path, collection_name, pvp_data)
    return ref


async def get_data(collection_name: str, collection_path: str):
    d = crud.read_document(collection_path, collection_name)
    return d


async def get_multiple_data(collection_path: str):
    """Returns all documents stored in a collection"""
    c = crud.collection_ref(collection_path)
    l: dict[str, dict] = {}
    async for s in c.stream():  # type: ignore
        d = s.to_dict()
        if not d:
            continue
        doc_id = s.id
        l[doc_id] = d
    return l


async def get_most_recent_doc(collection_path: str, field_path: str, order_type: str):
    # firestore.AsyncQuery.DESCENDING or firestore.AsyncQuery.ASCENDING
    # for order type
    q = (
        crud.collection_ref(collection_path)
        .order_by(field_path, direction=order_type)
        .limit(1)
    )
    async for d in q.stream():
        return d.to_dict()


async def get_first_doc_in_collection(collection_path: str):
    """Mainly used for fetching tokens from DB"""
    ref = crud.collection_ref(collection_path)

    # Only query one document from collection
    q = ref.limit(1)

    async for doc in q.stream():
        return doc.to_dict()


async def store_data(
    data: dict,
    collection_path: str,
    include_autogen_id_field: bool = False,
    collection_name: Optional[str] = None,
):
    """TODO: Use this to replace store_* functions"""
    d = await crud.create_document(
        collection_path=collection_path,
        document_id=collection_name,
        data=data,
        include_autogen_id_field=include_autogen_id_field,
    )
    return d
