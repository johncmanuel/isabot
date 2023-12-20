from fastapi import Request, Response
from nacl.encoding import HexEncoder
from nacl.signing import VerifyKey


def hex_to_bytes(hex_str: str):
    return bytes.fromhex(hex_str)


async def verify_request(req: Request, public_key: str):
    """Verify if the incoming request is from Discord."""

    if req.headers.get("Content-Type") != "application/json":
        return {"error": Response("Unsupported media type", 415), "body": None}

    signature, timestamp = req.headers.get("X-Signature-Ed25519"), req.headers.get(
        "X-Signature-Timestamp"
    )
    if not signature:
        return {
            "error": Response("Missing header: X-Signature-Ed25519", 401),
            "body": None,
        }
    if not timestamp:
        return {
            "error": Response("Missing header: X-Signature-Timestamp", 401),
            "body": None,
        }

    body = await req.body()

    message = timestamp.encode("utf-8") + body
    valid = VerifyKey(hex_to_bytes(public_key), encoder=HexEncoder).verify(
        message, hex_to_bytes(signature)
    )

    if not valid:
        return {
            "error": Response("Invalid request", 401),
            "body": None,
        }

    return {"body": req.json(), "error": None}
