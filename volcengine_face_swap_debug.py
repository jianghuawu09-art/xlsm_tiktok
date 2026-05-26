import os
import sys
import json
import base64
import hmac
import hashlib
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime

HOST = "visual.volcengineapi.com"
ENDPOINT = f"https://{HOST}/"
REGION = "cn-beijing"
SERVICE = "cv"
ACTION = "CVProcess"
VERSION = "2022-08-31"


def sign(key: bytes, msg: str) -> bytes:
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_authorization(access_key: str, secret_key: str, x_date: str, short_date: str, payload: bytes) -> str:
    canonical_uri = "/"
    canonical_querystring = urllib.parse.urlencode({"Action": ACTION, "Version": VERSION})
    canonical_headers = f"content-type:application/json\nhost:{HOST}\nx-date:{x_date}\n"
    signed_headers = "content-type;host;x-date"
    payload_hash = sha256_hex(payload)
    canonical_request = "\n".join([
        "POST",
        canonical_uri,
        canonical_querystring,
        canonical_headers,
        signed_headers,
        payload_hash,
    ])

    string_to_sign = "\n".join([
        "HMAC-SHA256",
        x_date,
        f"{short_date}/{REGION}/{SERVICE}/request",
        sha256_hex(canonical_request.encode("utf-8")),
    ])

    k_date = sign(secret_key.encode("utf-8"), short_date)
    k_region = sign(k_date, REGION)
    k_service = sign(k_region, SERVICE)
    k_signing = sign(k_service, "request")
    signature = hmac.new(k_signing, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

    return (
        f"HMAC-SHA256 Credential={access_key}/{short_date}/{REGION}/{SERVICE}/request, "
        f"SignedHeaders={signed_headers}, Signature={signature}"
    )


def check_image_url(url: str, timeout: int = 10) -> bool:
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            print(f"输入图片可访问: {url} -> HTTP {resp.status}")
            return 200 <= resp.status < 300
    except Exception as e:
        print(f"输入图片不可访问: {url} -> {e}")
        return False


def save_output(base64_str: str, index: int) -> None:
    data = base64.b64decode(base64_str)
    filename = f"face_swap_result_{index}.png"
    with open(filename, "wb") as f:
        f.write(data)
    print(f"已保存图片: {filename}")


def main() -> int:
    access_key = os.getenv("VOLCENGINE_ACCESS_KEY_ID")
    secret_key = os.getenv("VOLCENGINE_SECRET_ACCESS_KEY")
    if not access_key or not secret_key:
        print("请先设置环境变量 VOLCENGINE_ACCESS_KEY_ID 和 VOLCENGINE_SECRET_ACCESS_KEY")
        return 1

    source_url = "https://img-reg-ab.imagency.cn/e/f904881a88072327e2815d4b5594338c.png"
    template_url = "https://img-reg-ab.imagency.cn/e/d5f94165fd984328af453f30f8d94821.png"

    print("检查输入图片是否可访问...")
    if not check_image_url(source_url) or not check_image_url(template_url):
        print("请换成可被 VolcEngine 服务端下载的公开图片链接。")
        return 2

    body = {
        "req_key": "face_swap3_6",
        "image_urls": [source_url, template_url],
        "face_type": "area",
        "merge_infos": [{"location": 1, "template_location": 1}],
        "return_url": False,
    }

    payload = json.dumps(body, separators=(",", ":")).encode("utf-8")
    now = datetime.utcnow()
    x_date = now.strftime("%Y%m%dT%H%M%SZ")
    short_date = now.strftime("%Y%m%d")
    authorization = build_authorization(access_key, secret_key, x_date, short_date, payload)

    headers = {
        "Host": HOST,
        "Content-Type": "application/json",
        "X-Date": x_date,
        "Authorization": authorization,
    }

    url = f"{ENDPOINT}?Action={urllib.parse.quote(ACTION)}&Version={urllib.parse.quote(VERSION)}"
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            text = resp.read().decode("utf-8")
            print("状态码:", resp.status)
            data = json.loads(text)
            print(json.dumps(data, indent=2, ensure_ascii=False))

            binary_list = None
            if isinstance(data, dict):
                binary_list = data.get("data", {}).get("binary_data_base64") if isinstance(data.get("data"), dict) else None
                if binary_list is None:
                    data_field = data.get("data")
                    if isinstance(data_field, dict):
                        binary_list = data_field.get("binary_data_base64")

            if binary_list:
                for idx, item in enumerate(binary_list, start=1):
                    filename = f"face_swap_result_{idx}.png"
                    with open(filename, "wb") as f:
                        f.write(base64.b64decode(item))
                    print(f"已保存图片: {filename}")
            else:
                print("未检测到返回的 binary_data_base64，请检查返回结果。")

            return 0
    except urllib.error.HTTPError as e:
        try:
            error_body = e.read().decode("utf-8")
        except Exception:
            error_body = ""
        print("HTTP 错误:", e.code)
        print(error_body)
        return 3
    except Exception as e:
        print("请求异常:", e)
        return 4


if __name__ == "__main__":
    sys.exit(main())
