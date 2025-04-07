import os
import re

def clean_json_string(json_string):
    return json_string.replace("```json", "").replace("```", "")

def replace_server_url_with_localhost(url):
    if os.getenv("ALWAYS_USE_LOCALHOST"):
        """Replaces any HTTP URL with http://localhost:3000/."""
        url = url.replace("https://", "http://")
        return re.sub(r"http://[^/]+/", "http://localhost:3000/", url)
    elif os.getenv("ALWAYS_USE_NO_SSL"):
        """Replaces any HTTPS with HTTP"""
        url = url.replace("https://", "http://")

    return url

