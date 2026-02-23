#!/usr/bin/env python3
"""
鸣潮资源全量同步脚本（使用 encore.moe API v2）
功能：
1. 检查目标仓库的 data/resource.json 是否有更新
2. 从 encore.moe 获取角色多语言数据并生成 id2role.json
3. 智能下载角色图片 (GitHub优先 -> encore.moe备用)
4. 生成最终的 src/role.json
"""

from datetime import datetime, timezone
import io
import json
import logging
from pathlib import Path
import sys
import time
from typing import Any

from PIL import Image
import requests

# ---------- 基础配置 ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)

TARGET_REPO = "MoonShadow1976/WutheringWaves_OverSea_StaticAssets"
STATE_FILE = Path(".github/asset_sync_state.json")

# encore.moe API 配置
ENCORE_API_BASE = "https://api-v2.encore.moe/api"
SUPPORTED_LANGS = [
    "en",
    "zh-Hans",
    "ja",
    "ko",
]

LOCAL_JSON_PATH = Path("src/id2role.json")

# GitHub 图片仓库配置
ROLE_IMG_API_URL = f"https://api.github.com/repos/{TARGET_REPO}/contents/data/resource/role_pile"
ROLE_PILE_JSON_URL = f"https://raw.githubusercontent.com/{TARGET_REPO}/main/data/resource/role_pile.json"
LOCAL_IMG_DIR = Path("src/role/")

# encore.moe 备用下载配置
ENCORE_RESOURCE_BASE = "https://api.encore.moe/resource/Data"


# ---------- 状态管理 ----------
def load_state() -> dict[str, Any]:
    """加载上次同步的状态记录"""
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"last_updated": None, "last_checked": None}


def save_state(key: str, value: Any) -> None:
    """保存本次同步状态"""
    state = load_state()
    state[key] = value
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


# ---------- 核心检查函数 ----------
def check_for_updates() -> tuple[bool, str | None]:
    """检查目标仓库是否有更新"""
    logging.info("🔍 检查目标仓库更新...")
    try:
        resp = requests.get(ROLE_PILE_JSON_URL, timeout=30)
        resp.raise_for_status()
        current_data = resp.json()
        current_time = current_data.get("last_updated")

        last_state = load_state()
        last_sync_time = last_state.get("last_updated")

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
        return True, f"error_{datetime.now(timezone.utc).isoformat()}"


# ---------- 从 encore.moe 获取角色数据 ----------
def fetch_character_list(lang: str) -> list[dict[str, Any]]:
    """获取指定语言的角色列表"""
    url = f"{ENCORE_API_BASE}/{lang}/character"
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data.get("roleList", [])
    except Exception as e:
        logging.error(f"获取角色列表失败 [{lang}]: {e}")
        return []


def fetch_character_detail(char_id: int, lang: str = "en") -> dict[str, Any]:
    """获取角色详情（用于背景图、描述等）"""
    url = f"{ENCORE_API_BASE}/{lang}/character/{char_id}"
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logging.error(f"获取角色详情失败 [id={char_id}, lang={lang}]: {e}")
        return {}


def build_id2role() -> dict[str, dict[str, str]]:
    """
    从 encore.moe 聚合多语言数据，生成 id2role.json 内容
    """
    logging.info("🌐 开始从 encore.moe 获取多语言角色数据...")

    # 收集所有语言的角色名称
    names_by_lang: dict[str, dict[str, str]] = {}
    all_ids: set[str] = set()

    for lang in SUPPORTED_LANGS:
        logging.info(f"  正在获取 [{lang}] 角色列表...")
        role_list = fetch_character_list(lang)
        lang_names = {}
        for role in role_list:
            char_id = str(role["Id"])
            name = role.get("Name", "")
            if name:
                lang_names[char_id] = name
                all_ids.add(char_id)
        names_by_lang[lang] = lang_names
        time.sleep(0.2)  # 避免请求过快

    logging.info(f"📋 共发现 {len(all_ids)} 个角色")

    id2role: dict[str, dict[str, str]] = {}

    # 填充角色立绘
    logging.info("  获取角色立绘...")
    for char_id in all_ids:
        detail = fetch_character_detail(int(char_id), lang="en")
        if detail:
            img = detail.get("FormationRoleCard", "")
            if img:
                logging.debug(f"    获取角色立绘成功 [id={char_id}]...")
                id2role.setdefault(char_id, {})["icon"] = img
        time.sleep(0.1)

    # 合并其他语言名称
    for lang, names in names_by_lang.items():
        for char_id, name in names.items():
            logging.debug(f"    获取角色名称成功 [id={char_id}, lang={lang}]...")
            id2role.setdefault(char_id, {})[lang] = name

    # 按 char_id 排序
    id2role = dict(sorted(id2role.items(), key=lambda item: int(item[0])))
    logging.info(f"✅ 多语言数据聚合完成，共 {len(id2role)} 个角色")
    return id2role


def download_json() -> bool:
    """生成并保存 id2role.json"""
    logging.info("📥 从 encore.moe 构建角色数据...")
    try:
        id2role_data = build_id2role()
        LOCAL_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(LOCAL_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(id2role_data, f, ensure_ascii=False, indent=2)
        logging.info(f"✅ id2role.json 已保存至: {LOCAL_JSON_PATH}")
        return True
    except Exception as e:
        logging.error(f"❌ 构建 id2role.json 失败: {e}")
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
    files_to_download: list[dict[str, str | Path]] = []

    try:
        pile_resp = requests.get(ROLE_PILE_JSON_URL, timeout=30)

        if pile_resp.status_code == 200:
            try:
                pile_data = pile_resp.json()
                file_list = pile_data.get("files", [])
                logging.info(f"✅ 获取到图片清单，包含 {len(file_list)} 个文件")

                for file_info in file_list:
                    filename: str = file_info.get("name")
                    remote_size: int = file_info.get("size")
                    if not filename or remote_size is None:
                        continue

                    local_path = LOCAL_IMG_DIR / filename
                    if local_path.exists() and local_path.stat().st_size == remote_size:
                        continue

                    download_url = ROLE_PILE_JSON_URL.replace(".json", f"/{filename}")
                    files_to_download.append({"url": download_url, "local_path": local_path})

                logging.info(f"📋 需要下载 {len(files_to_download)} 个新/更新文件")

            except json.JSONDecodeError as e:
                logging.warning(f"解析 role_pile.json 失败: {e}，将回退到API方式")
                files_to_download = []
        else:
            logging.warning("无法获取 role_pile.json，回退到API方式")
            files_to_download = []

        # 如果清单方式未获取到文件列表，回退到API方式
        if not files_to_download:
            logging.info("🔄 回退到GitHub API方式获取文件列表...")
            resp = requests.get(ROLE_IMG_API_URL, timeout=30)
            resp.raise_for_status()
            if isinstance(resp.json(), dict) and "message" in resp.json():
                logging.error(f"❌ GitHub API错误: {resp.json()['message']}")
                return 0, 1
            files = resp.json()
            for item in files:
                if item["type"] != "file":
                    continue
                filename: str = item["name"]
                download_url: str = item.get("download_url")
                remote_size: int = item.get("size")
                if not download_url:
                    continue
                local_path = LOCAL_IMG_DIR / filename
                if local_path.exists() and remote_size and local_path.stat().st_size == remote_size:
                    continue
                files_to_download.append({"url": download_url, "local_path": local_path})
            logging.info(f"📋 (回退方式) 需要下载 {len(files_to_download)} 个文件")

        # 执行下载
        for file_info in files_to_download:
            try:
                img_resp = requests.get(str(file_info["url"]), timeout=60)
                img_resp.raise_for_status()
                with open(file_info["local_path"], "wb") as f:
                    f.write(img_resp.content)
                success += 1
                logging.info(f"  ✅ 已下载: {file_info['local_path']}")
                if len(files_to_download) > 10:
                    time.sleep(0.1)
            except Exception as e:
                logging.error(f"  ❌ 下载失败 {file_info['local_path']}: {e}")
                fail += 1

        return success, fail

    except Exception as e:
        logging.error(f"❌ GitHub下载流程失败: {e}")
        return 0, 1


# ---------- 备用下载 (encore.moe) ----------
def download_from_encore_backup() -> tuple[int, int]:
    """
    从 encore.moe 资源服务器下载缺失的背景图
    需要 id2role.json 中的 background 字段
    """
    logging.info("🔄 尝试从备用源(encore.moe)下载缺失图片...")

    if not LOCAL_JSON_PATH.exists():
        logging.error("❌ 无法使用备用源: id2role.json 不存在")
        return 0, 0

    try:
        with open(LOCAL_JSON_PATH, encoding="utf-8") as f:
            id2role_data = json.load(f)
    except Exception as e:
        logging.error(f"❌ 读取id2role.json失败: {e}")
        return 0, 0

    success, fail = 0, 0
    download_tasks: list[tuple[str, str, Path]] = []

    for char_id, char_info in id2role_data.items():
        expected_filename = f"role_pile_{char_id}.png"
        local_path = LOCAL_IMG_DIR / expected_filename

        if local_path.exists():
            continue

        img_url = char_info.get("icon", "")
        if not img_url:
            logging.warning(f"角色 {char_id} 无 icon 字段，跳过")
            continue

        download_tasks.append((char_id, img_url, local_path))

    if not download_tasks:
        logging.info("⏭️  无缺失图片需要从备用源下载")
        return 0, 0

    logging.info(f"📋 从备用源下载 {len(download_tasks)} 个缺失图片")

    for char_id, img_url, local_path in download_tasks:
        max_retries = 3
        downloaded = False

        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    wait_time = 2 ** (attempt - 1)
                    logging.debug(f"第{attempt}次重试 ({wait_time}秒后): {char_id}")
                    time.sleep(wait_time)

                resp = requests.get(img_url, timeout=30)
                resp.raise_for_status()

                content_type = resp.headers.get("Content-Type", "")
                if "image/png" in content_type:
                    with open(local_path, "wb") as f:
                        f.write(resp.content)
                else:
                    # 尝试用 PIL 转换
                    img = Image.open(io.BytesIO(resp.content))
                    img.save(local_path, "PNG")

                success += 1
                downloaded = True
                logging.info(f"  ✅ 备用源下载: {char_id} -> {local_path.name}")
                break

            except Exception as e:
                if attempt == max_retries:
                    logging.error(f"  ❌ 备用源下载失败 {char_id}: {e}")
                    fail += 1
                continue

        if downloaded and len(download_tasks) > 5:
            time.sleep(0.5)

    return success, fail


# ---------- 生成最终role.json ----------
def generate_final_role_json() -> bool:
    """根据id2role.json和本地图片生成最终的role.json"""
    logging.info("📄 生成最终role.json...")

    if not LOCAL_JSON_PATH.exists():
        logging.error("❌ 无法生成role.json: id2role.json 不存在")
        return False

    try:
        with open(LOCAL_JSON_PATH, encoding="utf-8") as f:
            id2role_data = json.load(f)
    except Exception as e:
        logging.error(f"❌ 读取id2role.json失败: {e}")
        return False

    data: list[dict[str, Any]] = []
    for char_id, char_info in id2role_data.items():
        expected_filename = f"role_pile_{char_id}.png"
        local_img_path = LOCAL_IMG_DIR / expected_filename

        char_data: dict[str, Any] = {
            "id": char_id,
            "url": f"src/role/{expected_filename}" if local_img_path.exists() else None,
        }

        # 添加多语言名称（排除非语言字段）
        exclude_keys = {"icon", "background", "rank", "weapon", "element", "desc"}
        for key, value in char_info.items():
            if key in exclude_keys:
                continue
            # 将 zh-Hans 映射为 zh（与之前保持一致）
            if key == "zh-Hans":
                char_data["zh"] = value
            else:
                char_data[key] = value

        data.append(char_data)

    result = {
        "status": 200,
        "info": "Wuthering Waves Role Data",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": data,
    }

    output_path = Path("src/role.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    logging.info(f"✅ role.json 已生成: {output_path} (包含 {len(data)} 个角色)")
    return True


# ---------- 主函数 ----------
def main() -> None:
    print("=" * 60)
    print("鸣潮资源全量同步脚本 (encore.moe API v2)")
    print("=" * 60)

    has_update, new_timestamp = check_for_updates()
    if not has_update:
        logging.info("🔄 未发现新内容，本次同步结束。")
        save_state("last_checked", datetime.now(timezone.utc).isoformat())
        sys.exit(0)

    logging.info("🚀 开始同步流程...")

    # 1. 构建角色 JSON 数据（从 encore.moe）
    if not download_json():
        logging.error("❌ 角色数据构建失败，同步终止")
        sys.exit(1)

    # 2. 图片下载：GitHub优先
    logging.info("\n" + "-" * 50)
    gh_success, gh_fail = download_from_github()

    # 3. 备用下载：如果有失败或缺失，从 encore.moe 下载
    if gh_fail > 0 or gh_success == 0:
        logging.info("\n" + "-" * 50)
        backup_success, backup_fail = download_from_encore_backup()
        total_success = gh_success + backup_success
        total_fail = gh_fail + backup_fail
    else:
        total_success = gh_success
        total_fail = gh_fail

    # 4. 生成最终文件
    logging.info("\n" + "-" * 50)
    if not generate_final_role_json():
        logging.warning("⚠️  生成role.json失败，但其他同步已完成")

    # 5. 保存状态
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

    print("\n" + "=" * 60)
    print("✅ 同步完成！")
    print(f"   图片: 成功 {total_success}, 失败 {total_fail}")
    print("   数据: id2role.json, role.json")
    print(f"   状态: 已更新至时间戳 {new_timestamp}")
    print("=" * 60)

    if total_fail > 0:
        print(f"\n⚠️  注意: 有 {total_fail} 个图片下载失败")
        print("     将在下次同步时重试")


if __name__ == "__main__":
    main()
