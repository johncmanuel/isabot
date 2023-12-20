from fastapi import Request, Response
from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey


async def verify_request(req: Request, public_key: str):
    """Verify if the incoming request is from Discord."""

    if req.headers.get("Content-Type") != "application/json":
        return {"error": Response("Unsupported media type", 415), "body": None}

    signature, timestamp = req.headers.get("X-Signature-Ed25519"), req.headers.get(
        "X-Signature-Timestamp"
    )

    if not timestamp or not signature:
        return {
            "error": Response("Bad request", 401),
            "body": None,
        }

    body = await req.body()
    key = VerifyKey(bytes.fromhex(public_key))

    try:
        key.verify(
            timestamp.encode() + body,
            bytes.fromhex(signature),
        )
    except BadSignatureError as e:
        return {
            "error": Response("Bad signature", 401),
            "body": None,
        }

    return {"body": await req.json(), "error": None}
