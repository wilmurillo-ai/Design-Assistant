from __future__ import annotations

import os

DEFAULT_BASE_URL = os.getenv("IMA_BASE_URL", "https://api.imastudio.com")
DEFAULT_IM_BASE_URL = os.getenv("IMA_IM_BASE_URL", "https://imapi.liveme.com")
PREFS_PATH = os.path.expanduser("~/.openclaw/memory/ima_prefs.json")

IMAGE_TASK_TYPES = ("text_to_image", "image_to_image")
DEFAULT_MODEL_BY_TASK_TYPE = {
    "text_to_image": "doubao-seedream-4.5",
    "image_to_image": "doubao-seedream-4.5",
}
DEFAULT_MODEL_LABEL_BY_TASK_TYPE = {
    "text_to_image": "SeeDream 4.5",
    "image_to_image": "SeeDream 4.5",
}
POLL_CONFIG = {
    "text_to_image": {"interval": 5, "max_wait": 600},
    "image_to_image": {"interval": 5, "max_wait": 600},
}

APP_ID = "webAgent"
APP_KEY = "32jdskjdk320eew"
