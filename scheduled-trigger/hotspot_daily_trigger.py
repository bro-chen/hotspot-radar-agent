#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""热点情报雷达 — 每日定时触发脚本

每天被 Calendar 定时调用时，读取配置文件并向部署的工作流 API
提交异步采集任务，将响应结果写入 output 目录并提交 CodeAct 结果。

参数顺序（codeact_args / Calendar script_args）：result_mode
- result_mode: display_only / notify / no_reply / auto
              默认 display_only；auto 映射为 display_only
"""

import asyncio
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime

from codeact_sdk import CodeActSDK

# === 常量 ===
CONFIG_PATH = "./codeact/config/hotspot_config.json"
OUTPUT_DIR = "./codeact/output"
REQUEST_TIMEOUT = 30  # 秒


def norm_mode(raw: str) -> str:
    """将用户传入的 result_mode 归一化为合法值。"""
    mode = (raw or "display_only").strip().lower()
    if mode == "auto":
        return "display_only"
    return mode if mode in {"display_only", "notify", "no_reply"} else "display_only"


def write_output(data: dict, tag: str = "trigger") -> str:
    """将结果写入 output 目录，返回文件路径。"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"hotspot_{tag}_{timestamp}.json"
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path


def load_config() -> dict:
    """读取配置文件。"""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def send_trigger(config: dict) -> dict:
    """向工作流 API 发送 POST 请求，返回解析后的 JSON 响应。"""
    api_url = config["api_url"]
    payload = {
        "keywords": config["keywords"],
        "recipient_email": config["recipient_email"],
        "trigger_type": config.get("trigger_type", "auto"),
    }
    body = json.dumps(payload).encode("utf-8")
    headers = {
        "Authorization": f'Bearer {config["auth_token"]}',
        "Content-Type": "application/json",
    }
    req = urllib.request.Request(api_url, data=body, headers=headers, method="POST")
    print(f"[请求] POST {api_url}")
    print(f"[参数] keywords={payload['keywords']}, "
          f"recipient_email={payload['recipient_email']}, "
          f"trigger_type={payload['trigger_type']}")

    with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
        resp_body = resp.read().decode("utf-8")
        return json.loads(resp_body)


async def main():
    result_mode = norm_mode(sys.argv[1] if len(sys.argv) > 1 else "display_only")
    print(f"[参数] result_mode={result_mode}")
    sdk = CodeActSDK()

    try:
        # 1. 读取配置
        config = load_config()

        # 2. 发送请求
        resp_data = send_trigger(config)

        # 3. 解析响应
        task_id = str(resp_data.get("task_id", resp_data.get("data", {}).get("task_id", "")))
        status = str(resp_data.get("status", resp_data.get("data", {}).get("status", "")))

        # 4. 写入结果文件
        result = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "success": True,
            "task_id": task_id,
            "status": status,
            "keywords": config["keywords"],
            "recipient_email": config["recipient_email"],
            "trigger_type": config.get("trigger_type", "auto"),
            "api_url": config["api_url"],
            "raw_response": resp_data,
        }
        output_path = write_output(result, tag="trigger")
        print(f"[结果] task_id={task_id}, status={status}")
        print(f"[文件] {output_path}")

        # 5. 提交结果
        abs_path = os.path.abspath(output_path)
        message = (
            f"热点情报雷达已触发。任务ID: {task_id}，状态: {status or '未知'}。"
            f"\n关键词: {', '.join(config['keywords'])}"
            f"\n结果文件: [hotspot_trigger.json](computer://{abs_path})"
        )
        await sdk.submit_result(
            result_mode=result_mode,
            status="success",
            message=message,
            data={
                "task_id": task_id,
                "trigger_status": status,
                "output_path": output_path,
                "keywords": config["keywords"],
            },
        )

    except urllib.error.HTTPError as e:
        # HTTP 错误（4xx/5xx）
        error_body = ""
        try:
            error_body = e.read().decode("utf-8")
        except Exception:
            pass

        error_info = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "success": False,
            "error_type": "HTTPError",
            "error_code": e.code,
            "error_reason": str(e.reason),
            "error_body": error_body[:2000],
        }
        error_path = write_output(error_info, tag="error")
        print(f"[错误] HTTP {e.code}: {e.reason}")

        await sdk.submit_result(
            result_mode="notify",
            status="error",
            message=f"热点情报雷达触发失败：HTTP {e.code} - {e.reason}",
            data={
                "error_type": "HTTPError",
                "error_code": e.code,
                "output_path": error_path,
            },
        )

    except urllib.error.URLError as e:
        # 网络错误（超时、连接失败等）
        error_info = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "success": False,
            "error_type": "URLError",
            "error_reason": str(e.reason),
        }
        error_path = write_output(error_info, tag="error")
        print(f"[错误] URLError: {e.reason}")

        await sdk.submit_result(
            result_mode="notify",
            status="error",
            message=f"热点情报雷达触发失败：网络错误 - {e.reason}",
            data={
                "error_type": "URLError",
                "output_path": error_path,
            },
        )

    except Exception as e:
        # 其他未预期错误
        error_info = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "success": False,
            "error_type": type(e).__name__,
            "error_message": str(e)[:2000],
        }
        error_path = write_output(error_info, tag="error")
        print(f"[错误] {type(e).__name__}: {e}")

        await sdk.submit_result(
            result_mode="notify",
            status="error",
            message=f"热点情报雷达触发失败：{type(e).__name__} - {str(e)[:200]}",
            data={
                "error_type": type(e).__name__,
                "output_path": error_path,
            },
        )


if __name__ == "__main__":
    asyncio.run(main())
