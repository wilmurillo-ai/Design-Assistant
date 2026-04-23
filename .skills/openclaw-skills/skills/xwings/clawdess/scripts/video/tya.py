"""TYA (Tuoyi) video provider — base64 upload/download."""

import base64
import os
import random
import string
import sys
import time
import urllib.request

from common import api_post, api_get, MEDIA_CACHE


def generate(api_key, prompt, image_url):
    """Submit video to TYA, poll until ready, return local file path.
    api_key format: UID:TOKEN
    """
    if ":" not in api_key:
        sys.exit("Error: --video-api for TYA must be in UID:TOKEN format (e.g. 12345:abcdef).")
    tya_uid_str, tya_token = api_key.split(":", 1)
    tya_uid = int(tya_uid_str)
    task_id = "".join(random.choices(string.ascii_letters + string.digits, k=12))

    # Download and base64-encode the image
    with urllib.request.urlopen(image_url) as resp:
        img_b64 = "data:image/png;base64," + base64.b64encode(resp.read()).decode()

    payload = {
        "uid": tya_uid,
        "token": tya_token,
        "taskid": task_id,
        "img": img_b64,
        "mode": 2,
    }
    headers = {"Content-Type": "application/json"}
    code, body = api_post("https://api.tuoyiapi88.cc/api/app/aipost", headers, payload)
    print(f"TYA video submitted ({code}): taskid={task_id}")

    # Poll for completion
    poll_payload = {"taskid": task_id, "token": tya_token, "type": 1}
    for i in range(300):
        _, resp = api_get(
            "https://s1.tuoyiapi88.cc/api/app/get_task",
            {"Content-Type": "application/json"},
            payload=poll_payload,
        )
        status = str(resp.get("status", ""))
        print(f"TYA poll {i}: status={status}")
        if status == "200":
            b64_data = resp.get("data", {}).get("base64", "")
            if not b64_data:
                print(f"TYA poll {i}: status 200 but no base64 data, retrying...")
                time.sleep(5)
                continue
            if "," in b64_data:
                b64_data = b64_data.split(",", 1)[1]
            os.makedirs(MEDIA_CACHE, exist_ok=True)
            local_path = os.path.join(MEDIA_CACHE, f"clawdess_{task_id}.png")
            with open(local_path, "wb") as f:
                f.write(base64.b64decode(b64_data))
            print(f"TYA video saved: {local_path}")
            return local_path
        time.sleep(5)
    return None
