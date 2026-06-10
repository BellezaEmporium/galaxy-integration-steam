from typing import NamedTuple
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey

class SteamPublicKey(NamedTuple):
    rsa_public_key: RSAPublicKey
    timestamp: int