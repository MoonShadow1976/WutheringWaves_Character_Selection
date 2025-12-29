#!/usr/bin/env python3
"""
资源全量同步脚本
功能：
1. 检查目标仓库的 data/resource.json 是否有更新
2. 下载最新的 id2role.json
3. 智能下载角色图片 (GitHub优先 -> hakush.in备用)
4. 生成最终的 src/role.json
"""

import io
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from PIL import Image

# ---------- 基础配置 ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)

TARGET_REPO = "MoonShadow1976/WutheringWaves_OverSea_StaticAssets"
STATE_FILE = Path(".github/asset_sync_state.json")

SOURCE_JSON_URL = "https://api.hakush.in/ww/data/character.json"
LOCAL_JSON_PATH = Path("src/id2role.json")

ROLE_IMG_API_URL = (
    f"https://api.github.com/repos/{TARGET_REPO}/contents/data/resource/role_pile"
)
ROLE_PILE_JSON_URL = (
    f"https://raw.githubusercontent.com/{TARGET_REPO}/main/data/resource/role_pile.json"
)
LOCAL_IMG_DIR = Path("src/role/")

# hakush.in 备用下载配置
HAKUSH_MAIN_URL = "https://api.hakush.in/ww"
ROLE_PILE_PATH = LOCAL_IMG_DIR  # 统一图片输出目录


# ---------- 状态管理 ----------
def load_state() -> dict[str, Any]:
    """加载上次同步的状态记录"""
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"last_updated": None, "last_checked": None}


def save_state(key: str, value: Any):
    """保存本次同步状态"""
    state = load_state()
    state[key] = value
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


# ---------- 核心检查函数 ----------
def check_for_updates() -> tuple[bool, str | None]:
    """
    检查目标仓库是否有更新
    返回: (是否更新, 最新时间戳/None)
    """
    logging.info("🔍 检查目标仓库更新...")
    try:
        # 1. 获取目标文件的原始内容
        resp = requests.get(ROLE_PILE_JSON_URL, timeout=30)
        resp.raise_for_status()
        current_data = resp.json()
        current_time = current_data.get("last_updated")

        # 2. 获取上次记录的状态
        last_state = load_state()
        last_sync_time = last_state.get("last_updated")

        # 3. 比较判断
        if not current_time:
            logging.warning("⚠️  目标文件未找到时间戳，将尝试同步")
            return True, datetime.now(timezone.utc).isoformat()

        if current_time != last_sync_time:
            logging.info(f"✅ 发现更新! 旧: {last_sync_time}, 新: {current_time}")
            return True, current_time
        else:
            logging.info(f"⏭️  无新更新。上次同步: {last_sync_time}")
            return False, current_time

    except requests.RequestException as e:
        logging.error(f"❌ 检查更新失败: {e}")
        # 网络失败时，保守起见尝试同步
        return True, f"error_{datetime.now(timezone.utc).isoformat()}"


# ---------- JSON下载 ----------
def download_json() -> bool:
    """下载并保存角色JSON文件，返回是否成功"""
    logging.info("📥 下载角色JSON...")
    try:
        resp = requests.get(SOURCE_JSON_URL, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        LOCAL_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(LOCAL_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logging.info(f"✅ JSON已保存至: {LOCAL_JSON_PATH}")
        return True
    except Exception as e:
        logging.error(f"❌ 下载JSON失败: {e}")
        return False


# ---------- 图片下载 (GitHub优先) ----------
def download_from_github() -> tuple[int, int]:
    """
    从GitHub仓库下载图片，优先使用 role_pile.json 进行文件大小对比
    返回: (成功数, 失败数)
    """
    logging.info("🖼️  从GitHub仓库同步图片 (使用清单文件)...")
    LOCAL_IMG_DIR.mkdir(parents=True, exist_ok=True)

    success, fail = 0, 0
    files_to_download = []  # 存储需要下载的文件信息

    try:
        # 1. 优先尝试获取并解析 role_pile.json
        pile_resp = requests.get(ROLE_PILE_JSON_URL, timeout=30)

        if pile_resp.status_code == 200:
            try:
                pile_data = pile_resp.json()
                last_updated = pile_data.get("last_updated", "N/A")
                file_list = pile_data.get("files", [])

                logging.info(
                    f"✅ 获取到图片清单，包含 {len(file_list)} 个文件，更新时间: {last_updated}"
                )

                # 分析本地文件，构建需要下载的列表
                for file_info in file_list:
                    filename = file_info.get("name")
                    remote_size = file_info.get("size")

                    if not filename or remote_size is None:
                        continue

                    local_path = LOCAL_IMG_DIR / filename
                    needs_download = True

                    # 核心对比逻辑：检查文件是否存在且大小一致
                    if local_path.exists():
                        local_size = local_path.stat().st_size
                        if local_size == remote_size:
                            needs_download = False
                            logging.debug(
                                f"⏭️  跳过 {filename} (大小一致: {local_size} bytes)"
                            )

                    if needs_download:
                        # 构建下载URL (使用 raw.githubusercontent.com)
                        download_url = ROLE_PILE_JSON_URL.replace(".json", f"/{filename}")
                        files_to_download.append(
                            {
                                "url": download_url,
                                "local_path": local_path,
                            }
                        )

                logging.info(f"📋 需要下载 {len(files_to_download)} 个新/更新文件")

            except json.JSONDecodeError as e:
                logging.warning(f"❌ 解析 role_pile.json 失败: {e}，将回退到API方式")
                files_to_download = None  # 触发回退

        else:
            logging.warning(
                f"⚠️  无法获取 role_pile.json (HTTP {pile_resp.status_code})，将回退到API方式"
            )
            files_to_download = None  # 触发回退

        # 2. 回退方案：如果获取JSON失败，使用原来的GitHub API方式
        if files_to_download is None:
            logging.info("🔄 回退到GitHub API方式获取文件列表...")
            files_to_download = []
            try:
                resp = requests.get(ROLE_IMG_API_URL, timeout=30)
                resp.raise_for_status()

                if isinstance(resp.json(), dict) and "message" in resp.json():
                    logging.error(f"❌ GitHub API错误: {resp.json()['message']}")
                    return 0, 1

                files = resp.json()
                for item in files:
                    if item["type"] != "file":
                        continue

                    filename = item["name"]
                    download_url = item.get("download_url")
                    remote_size = item.get("size")

                    if not download_url:
                        continue

                    local_path = LOCAL_IMG_DIR / filename

                    # 大小比较
                    if local_path.exists() and remote_size:
                        local_size = local_path.stat().st_size
                        if local_size == remote_size:
                            continue

                    files_to_download.append(
                        {
                            "url": download_url,
                            "local_path": local_path,
                        }
                    )

                logging.info(f"📋 (回退方式) 需要下载 {len(files_to_download)} 个文件")

            except Exception as e:
                logging.error(f"❌ GitHub API回退方式也失败: {e}")
                return 0, 1

        # 3. 执行下载
        if files_to_download:
            logging.info(f"🚀 开始批量下载 {len(files_to_download)} 个文件...")

            for file_info in files_to_download:
                download_url = file_info["url"]
                local_path = file_info["local_path"]

                try:
                    img_resp = requests.get(download_url, timeout=60)
                    img_resp.raise_for_status()

                    with open(local_path, "wb") as f:
                        f.write(img_resp.content)

                    success += 1
                    logging.info(f"  ✅ 已下载: {local_path}")

                    # 避免请求过快
                    if len(files_to_download) > 10:
                        time.sleep(0.1)

                except Exception as e:
                    logging.error(f"  ❌ 下载失败 {local_path}: {e}")
                    fail += 1

        return success, fail

    except Exception as e:
        logging.error(f"❌ GitHub下载流程失败: {e}")
        return 0, 1


# ---------- 备用下载 (hakush.in) ----------
def download_from_hakush_backup() -> tuple[int, int]:
    """
    从hakush.in备用源下载缺失的图片
    需要 id2role.json 中的 icon 字段
    返回: (成功数, 失败数)
    """
    logging.info("🔄 尝试从备用源(hakush.in)下载缺失图片...")

    # 1. 加载id2role.json数据
    if not LOCAL_JSON_PATH.exists():
        logging.error("❌ 无法使用备用源: id2role.json 不存在")
        return 0, 0

    try:
        with open(LOCAL_JSON_PATH, encoding="utf-8") as f:
            id2role_data = json.load(f)
    except Exception as e:
        logging.error(f"❌ 读取id2role.json失败: {e}")
        return 0, 0

    # 2. 准备下载
    success, fail = 0, 0
    download_tasks = []

    for char_id, char_info in id2role_data.items():
        expected_filename = f"role_pile_{char_id}.png"
        local_path = LOCAL_IMG_DIR / expected_filename

        # 如果文件已存在，跳过
        if local_path.exists():
            continue

        # 构建备用下载URL (WebP格式)
        icon_path = char_info.get("background", "")
        if not icon_path:
            logging.warning(f"角色 {char_id} 无background字段，跳过")
            continue

        # 处理路径：移除前缀和文件扩展名
        resource_path = str(icon_path).split(".")[0].replace("/Game/Aki/", "")
        webp_url = f"{HAKUSH_MAIN_URL}/{resource_path}.webp"
        download_tasks.append((char_id, webp_url, local_path))

    if not download_tasks:
        logging.info("⏭️  无缺失图片需要从备用源下载")
        return 0, 0

    logging.info(f"📋 从备用源下载 {len(download_tasks)} 个缺失图片")

    # 3. 执行下载（带重试）
    for char_id, webp_url, local_path in download_tasks:
        max_retries = 3
        downloaded = False

        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    wait_time = 2 ** (attempt - 1)  # 指数退避: 1, 2, 4秒
                    logging.debug(f"第{attempt}次重试 ({wait_time}秒后): {char_id}")
                    time.sleep(wait_time)

                # 下载WebP图片
                resp = requests.get(webp_url, timeout=30)
                resp.raise_for_status()

                # 转换为PNG格式保存
                webp_image = Image.open(io.BytesIO(resp.content))
                rgb_image = webp_image.convert("RGB")
                rgb_image.save(local_path, "PNG")

                success += 1
                downloaded = True
                logging.info(f"  ✅ 备用源下载: {char_id} -> {local_path.name}")
                break

            except Exception as e:
                if attempt == max_retries:
                    logging.error(f"  ❌ 备用源下载失败 {char_id}: {e}")
                    fail += 1
                continue

        # 短暂暂停，避免请求过快
        if downloaded and len(download_tasks) > 5:
            time.sleep(0.5)

    return success, fail


# ---------- 生成最终role.json ----------
def generate_final_role_json():
    """根据id2role.json和本地图片生成最终的role.json"""
    logging.info("📄 生成最终role.json...")

    # 读取id2role.json
    if not LOCAL_JSON_PATH.exists():
        logging.error("❌ 无法生成role.json: id2role.json 不存在")
        return False

    try:
        with open(LOCAL_JSON_PATH, encoding="utf-8") as f:
            id2role_data = json.load(f)
    except Exception as e:
        logging.error(f"❌ 读取id2role.json失败: {e}")
        return False

    # 构建数据
    data = []
    for char_id, char_info in id2role_data.items():
        # 检查对应的图片文件是否存在
        expected_filename = f"role_pile_{char_id}.png"
        local_img_path = LOCAL_IMG_DIR / expected_filename

        # 构建角色数据
        char_data = {
            "id": char_id,
            "url": f"src/role/{expected_filename}" if local_img_path.exists() else None,
        }

        # 添加多语言名称
        for lang, name in char_info.items():
            if lang in ["icon", "background", "rank", "weapon", "element", "desc"]:
                continue
            if lang == "zh-Hans":
                lang_key = "zh"
            else:
                lang_key = lang
            char_data[lang_key] = name

        data.append(char_data)

    # 构建最终结构
    result = {
        "status": 200,
        "info": "Wuthering Waves Role Data",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": data,
    }

    # 保存文件
    output_path = Path("src/role.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    logging.info(f"✅ role.json 已生成: {output_path}")
    logging.info(f"   包含 {len(data)} 个角色数据")
    return True


# ---------- 主函数 ----------
def main():
    print("=" * 60)
    print("鸣潮资源全量同步脚本")
    print("=" * 60)

    # 1. 检查更新
    has_update, new_timestamp = check_for_updates()
    if not has_update:
        logging.info("🔄 未发现新内容，本次同步结束。")
        save_state("last_checked", datetime.now(timezone.utc).isoformat())
        sys.exit(0)

    logging.info("🚀 开始同步流程...")

    # 2. 下载JSON数据
    if not download_json():
        logging.error("❌ JSON下载失败，同步终止")
        sys.exit(1)

    # 3. 图片下载：GitHub优先
    logging.info("\n" + "-" * 50)
    gh_success, gh_fail = download_from_github()

    # 4. 备用下载：如果有失败或缺失
    if gh_fail > 0 or gh_success == 0:
        logging.info("\n" + "-" * 50)
        backup_success, backup_fail = download_from_hakush_backup()
        total_success = gh_success + backup_success
        total_fail = gh_fail + backup_fail
    else:
        total_success = gh_success
        total_fail = gh_fail

    # 5. 生成最终文件
    logging.info("\n" + "-" * 50)
    if not generate_final_role_json():
        logging.warning("⚠️  生成role.json失败，但其他同步已完成")

    # 6. 保存状态
    save_state("last_updated", new_timestamp)
    save_state("last_synced", datetime.now(timezone.utc).isoformat())
    save_state(
        "last_sync_stats",
        {
            "images_downloaded": total_success,
            "images_failed": total_fail,
            "timestamp": new_timestamp,
        },
    )

    # 7. 输出总结
    print("\n" + "=" * 60)
    print("✅ 同步完成！")
    print(f"   图片: 成功 {total_success}, 失败 {total_fail}")
    print("   数据: id2role.json, role.json")
    print(f"   状态: 已更新至时间戳 {new_timestamp}")
    print("=" * 60)

    # 提示：如果total_fail>0，可能需要手动检查
    if total_fail > 0:
        print(f"\n⚠️  注意: 有 {total_fail} 个图片下载失败")
        print("     将在下次同步时重试")


if __name__ == "__main__":
    main()
