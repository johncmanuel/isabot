from isabot.firebase.crud import create_document, delete_document, read_document


def store_access_token(name: str, token: dict):
    access_token_doc_ref = create_document(
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
    token = read_document(collection_name, token_id)
    return token


def delete_access_token(
    token_id: str, collection_name: str = "authorization_flow_tokens"
):
    return delete_document(collection_name, token_id)


def store_bnet_userinfo(userinfo: dict, collection_name: str = "users"):
    userinfo_doc_ref = create_document(
        collection_name, userinfo.get("sub", "None"), userinfo
    )
    return userinfo_doc_ref


def store_wow_accounts(
    collection_name: str, wow_accounts: dict, collection_path: str = "characters"
):
    ref = create_document(collection_path, collection_name, wow_accounts)
    return ref


def store_cc_access_token(
    collection_name: str,
    token: dict,
    collection_path: str = "client_credentials_token",
):
    ref = create_document(collection_path, collection_name, token)
    return ref
