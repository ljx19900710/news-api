"""
网易新闻API抓取服务
基于 Flask 的 REST API，抓取网易新闻数据
"""
import os
import re
import logging
from datetime import datetime, timedelta
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify

# ── 配置 ──────────────────────────────────────────────
app = Flask(__name__)

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# 环境配置
PORT = int(os.getenv("PORT", "5000"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
MAX_PAGE_SIZE = int(os.getenv("MAX_PAGE_SIZE", "100"))

# 网易新闻板块映射表
# key: 中文板块名 / 拼音  -> value: 网易频道ID (新API使用)
CATEGORY_MAP = {
    # 新版 API 频道ID（3g.163.com/touch/reconstruct）
    "头条": "BBM54PGAwangning",
    "精选": "BA8E6OEOwangning",  # 综合新闻
    "国内": "BDC4QSV3wangning",   # 健康频道临时用，见下方 fallback
    "国际": "BA8E6OEOwangning",   # 综合
    "军事": "BAI67OGGwangning",
    "财经": "BA8EE5GMwangning",
    "科技": "BA8D4A3Rwangning",
    "娱乐": "BA10TA81wangning",
    "体育": "BA8E6OEOwangning",
    "汽车": "BA8E6OEOwangning",
    "房产": "BA8E6OEOwangning",
    "旅游": "BEO4GINLwangning",
    "教育": "BA8FF5PRwangning",
    "健康": "BDC4QSV3wangning",
    "游戏": "BAI6RHDKwangning",
    "时尚": "BA8F6ICNwangning",
    "数码": "BAI6JOD9wangning",
    "手机": "BAI6I0O5wangning",
    # 别名
    "新闻": "BBM54PGAwangning",
    "headline": "BBM54PGAwangning",
    "domestic": "BDC4QSV3wangning",
    "international": "BA8E6OEOwangning",
    "military": "BAI67OGGwangning",
    "finance": "BA8EE5GMwangning",
    "tech": "BA8D4A3Rwangning",
    "sports": "BA8E6OEOwangning",
    "entertainment": "BA10TA81wangning",
}

# 旧版API频道ID作为补充
OLD_CATEGORY_MAP = {
    "头条_old": "T1348647853363",
    "国内_old": "T1348648037603",
    "国际_old": "T1348648141035",
    "军事_old": "T1348648141035",
    "财经_old": "T1348648756099",
    "科技_old": "T1348649580692",
    "娱乐_old": "T1348648517839",
    "体育_old": "T1348649079062",
}

# 新版新闻列表API
NEWS_LIST_API = "https://3g.163.com/touch/reconstruct/article/list/{channel_id}/0-{size}.html"
# 新闻详情API
NEWS_DETAIL_API = "https://c.m.163.com/nc/article/{docid}/full.html"
# 备用新闻列表API
OLD_NEWS_LIST_API = "https://c.m.163.com/nc/article/list/{channel_id}/0-{size}.html"

# 通用请求头
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/json,*/*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}


# ── 工具函数 ──────────────────────────────────────────

def normalize_date(date_str: str) -> str:
    """将多种日期格式统一为 YYYY-MM-DD"""
    if not date_str:
        return ""
    # 清理空格
    date_str = date_str.strip()
    # 尝试解析各种格式
    formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    # 尝试 dateutil
    try:
        from dateutil import parser
        return parser.parse(date_str).strftime("%Y-%m-%d")
    except Exception:
        return date_str


def parse_ptime(ptime_str: str) -> datetime:
    """解析网易新闻的 ptime 字段"""
    if not ptime_str:
        return None
    try:
        return datetime.strptime(ptime_str.strip(), "%Y-%m-%d %H:%M:%S")
    except ValueError:
        pass
    try:
        from dateutil import parser
        return parser.parse(ptime_str)
    except Exception:
        return None


def extract_images_from_html(html_content: str) -> list:
    """从HTML内容中提取所有图片URL"""
    if not html_content:
        return []
    soup = BeautifulSoup(html_content, "lxml")
    images = []
    for img in soup.find_all("img"):
        src = img.get("src", "")
        if src and not src.startswith("data:"):
            images.append(src)
    return images


def clean_html(html_content: str) -> str:
    """清理HTML内容，移除脚本和样式"""
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "lxml")
    # 移除脚本和样式
    for tag in soup(["script", "style"]):
        tag.decompose()
    return str(soup)


def get_text_from_html(html_content: str) -> str:
    """从HTML中提取纯文本"""
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "lxml")
    return soup.get_text(separator="\n", strip=True)


# ── 核心抓取逻辑 ──────────────────────────────────────

def resolve_channel_id(category: str) -> str:
    """解析板块名称为频道ID"""
    if not category:
        return "BBM54PGAwangning"  # 默认头条

    # 直接匹配
    if category in CATEGORY_MAP:
        return CATEGORY_MAP[category]

    # 模糊匹配（不区分大小写）
    category_lower = category.lower()
    for key, value in CATEGORY_MAP.items():
        if key.lower() == category_lower:
            return value

    # 如果看起来像频道ID就直接返回
    if re.match(r'^[A-Z0-9]+wangning$', category, re.IGNORECASE):
        return category

    # 默认返回头条
    logger.warning(f"未识别的板块 '{category}'，使用默认头条频道")
    return "BBM54PGAwangning"


def fetch_news_list(channel_id: str, size: int = 20) -> list:
    """从网易新闻API获取新闻列表"""
    url = NEWS_LIST_API.format(channel_id=channel_id, size=min(size, MAX_PAGE_SIZE))
    logger.info(f"请求新闻列表: {url}")

    try:
        resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"请求新闻列表失败: {e}")
        return []

    # 网易新版API返回的是JSONP格式: artiList({...})
    text = resp.text.strip()
    # 去除 artiList( 和末尾的 )
    if text.startswith("artiList("):
        text = text[9:-1]
    elif text.startswith("artiListCallback("):
        text = text[17:-1]

    try:
        import json
        data = json.loads(text)
    except json.JSONDecodeError as e:
        logger.error(f"JSON解析失败: {e}")
        return []

    # 获取频道对应的新闻列表
    if channel_id not in data:
        # 尝试第一个key
        first_key = next(iter(data.keys()), None)
        if first_key:
            news_list = data.get(first_key, [])
        else:
            return []
    else:
        news_list = data.get(channel_id, [])

    return news_list if isinstance(news_list, list) else []


def fetch_news_detail(docid: str) -> dict:
    """获取单条新闻的详细内容 - 进入新闻详情页抓取完整HTML和纯文本"""
    url = NEWS_DETAIL_API.format(docid=docid)
    logger.info(f"进入新闻详情页抓取: {url}")

    try:
        resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"请求新闻详情失败 ({docid}): {e}")
        return {}

    try:
        import json
        data = json.loads(resp.text)
    except json.JSONDecodeError:
        logger.error(f"新闻详情JSON解析失败 ({docid})")
        return {}

    article = data.get(docid, {})
    if not article:
        logger.warning(f"新闻详情中未找到 {docid} 的数据")
        return {}

    # ── 提取图片列表 ──
    img_list = article.get("img", [])
    image_urls = []
    for img_info in img_list:
        src = img_info.get("src", "")
        if src:
            image_urls.append(src)

    # ── 处理HTML正文 ──
    body_html = article.get("body", "")

    # 1. 替换图片占位符 <!--IMG#N--> 为完整的 <img> 标签（含尺寸信息）
    for img_info in img_list:
        ref = img_info.get("ref", "")
        src = img_info.get("src", "")
        alt = img_info.get("alt", "")
        pixel = img_info.get("pixel", "")  # 格式: "800*571"

        if ref and src:
            # 解析尺寸
            width_attr = ""
            height_attr = ""
            if pixel and "*" in pixel:
                parts = pixel.split("*")
                try:
                    w, h = int(parts[0]), int(parts[1])
                    width_attr = f' width="{w}"'
                    height_attr = f' height="{h}"'
                except ValueError:
                    pass

            img_tag = f'<img src="{src}" alt="{alt}"{width_attr}{height_attr} loading="lazy">'
            body_html = body_html.replace(ref, img_tag)

    # 2. 替换链接占位符 <!--linkN--> 为实际的 <a> 标签
    link_list = article.get("link", [])
    for link_info in link_list:
        ref = link_info.get("ref", "")
        href = link_info.get("href", "")
        title = link_info.get("title", "")
        if ref and href:
            a_tag = f'<a href="{href}" target="_blank" rel="noopener">{title or href}</a>'
            body_html = body_html.replace(ref, a_tag)

    # 3. 替换学术词汇占位符 <!--AcademicWord#N-->
    academic_words = article.get("academicWords", [])
    for ac_word in academic_words:
        ref = ac_word.get("ref", "")
        word = ac_word.get("title", "")
        if ref and word:
            body_html = body_html.replace(ref, word)

    # ── 提取纯文本内容 ──
    content_text = get_text_from_html(body_html)

    return {
        "title": article.get("title", ""),
        "content": content_text,
        "html_content": body_html,
        "image_urls": image_urls,
        "source": article.get("source", ""),
        "ptime": article.get("ptime", ""),
        "docid": docid,
        "url": article.get("shareLink", "") or f"https://www.163.com/news/article/{docid}.html",
        "digest": article.get("digest", "") or article.get("shareDigest", ""),
    }


def filter_by_date(news_items: list, start_date: str, end_date: str) -> list:
    """按日期范围过滤新闻"""
    if not start_date and not end_date:
        return news_items

    start = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
    # end_date 包含当天，所以加一天
    end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1) if end_date else None

    filtered = []
    for item in news_items:
        ptime = parse_ptime(item.get("ptime", ""))
        if not ptime:
            # 如果没有时间信息，保留
            filtered.append(item)
            continue

        if start and ptime < start:
            continue
        if end and ptime >= end:
            continue
        filtered.append(item)

    return filtered


def filter_by_keyword(news_items: list, keyword: str) -> list:
    """按关键字过滤新闻（匹配标题和摘要）"""
    if not keyword:
        return news_items

    keyword_lower = keyword.lower()
    filtered = []
    for item in news_items:
        title = (item.get("title") or "").lower()
        digest = (item.get("digest") or "").lower()
        if keyword_lower in title or keyword_lower in digest:
            filtered.append(item)
    return filtered


# ── API 路由 ───────────────────────────────────────────

@app.route("/health", methods=["GET"])
def health_check():
    """健康检查接口"""
    return jsonify({
        "status": "ok",
        "service": "网易新闻抓取API",
        "version": "1.0.0",
    })


@app.route("/api/news", methods=["GET"])
def get_news():
    """
    新闻抓取接口

    入参:
        start_date  (str, 可选): 新闻发布开始日期，格式 2026-01-01
        end_date    (str, 可选): 新闻发布结束日期，格式 2026-01-31
        size        (int, 可选): 获取条数，默认20，最大100
        category    (str, 可选): 板块，如: 头条/国内/国际/军事/财经/科技/娱乐/体育
        keyword     (str, 可选): 关键字，用于模糊匹配新闻标题和摘要

    出参:
        code:       状态码
        message:    提示信息
        data:       新闻列表
            - title:        标题
            - content:      纯文本内容
            - html_content: HTML内容
            - image_urls:   图片URL列表
            - source:       来源
            - ptime:        发布时间
            - docid:        文档ID
            - url:          原始链接
            - digest:       摘要
    """
    # 解析参数
    start_date = request.args.get("start_date", "").strip()
    end_date = request.args.get("end_date", "").strip()
    category = request.args.get("category", "").strip()
    keyword = request.args.get("keyword", "").strip()

    try:
        size = int(request.args.get("size", "20"))
    except ValueError:
        size = 20

    # 参数校验
    size = min(max(1, size), MAX_PAGE_SIZE)

    # 日期格式校验
    if start_date:
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            return jsonify({
                "code": 400,
                "message": f"start_date 格式错误，应为 YYYY-MM-DD，收到: {start_date}",
                "data": []
            }), 400

    if end_date:
        try:
            datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            return jsonify({
                "code": 400,
                "message": f"end_date 格式错误，应为 YYYY-MM-DD，收到: {end_date}",
                "data": []
            }), 400

    # 解析频道
    channel_id = resolve_channel_id(category)

    # 获取新闻列表
    logger.info(f"抓取参数: category={category}, channel_id={channel_id}, size={size}, "
                f"start_date={start_date}, end_date={end_date}, keyword={keyword}")

    raw_news = fetch_news_list(channel_id, size)

    if not raw_news:
        return jsonify({
            "code": 200,
            "message": "未获取到新闻数据",
            "data": [],
            "params": {
                "category": category,
                "channel_id": channel_id,
                "size": size,
                "start_date": start_date,
                "end_date": end_date,
                "keyword": keyword,
            }
        })

    # 日期过滤
    if start_date or end_date:
        raw_news = filter_by_date(raw_news, start_date, end_date)

    # 关键字过滤
    if keyword:
        raw_news = filter_by_keyword(raw_news, keyword)

    # 限制返回条数
    raw_news = raw_news[:size]

    # 获取每一条新闻的详细内容
    result = []
    for item in raw_news:
        docid = item.get("docid", "")
        if not docid:
            continue

        detail = fetch_news_detail(docid)

        # 合并列表数据和详情数据
        news_item = {
            "title": detail.get("title") or item.get("title", ""),
            "content": detail.get("content", ""),
            "html_content": detail.get("html_content", ""),
            "image_urls": detail.get("image_urls", []) or (
                [item.get("imgsrc", "")] if item.get("imgsrc") else []
            ),
            "source": detail.get("source") or item.get("source", ""),
            "ptime": detail.get("ptime") or item.get("ptime", ""),
            "docid": docid,
            "url": detail.get("url") or item.get("url", ""),
            "digest": detail.get("digest") or item.get("digest", ""),
        }
        result.append(news_item)

    logger.info(f"成功获取 {len(result)} 条新闻")

    return jsonify({
        "code": 200,
        "message": f"成功获取 {len(result)} 条新闻",
        "data": result,
        "params": {
            "category": category,
            "channel_id": channel_id,
            "size": size,
            "start_date": start_date,
            "end_date": end_date,
            "keyword": keyword,
        }
    })


@app.route("/api/categories", methods=["GET"])
def get_categories():
    """获取支持的板块列表"""
    categories = {}
    for name, ch_id in CATEGORY_MAP.items():
        # 只取中文名
        if re.search(r'[\u4e00-\u9fff]', name):
            categories[name] = ch_id

    return jsonify({
        "code": 200,
        "message": "获取板块列表成功",
        "data": {
            "categories": list(categories.keys()),
            "total": len(categories),
        }
    })


@app.errorhandler(404)
def not_found(e):
    return jsonify({"code": 404, "message": "接口不存在", "data": []}), 404


@app.errorhandler(500)
def server_error(e):
    logger.error(f"服务器内部错误: {e}")
    return jsonify({"code": 500, "message": "服务器内部错误", "data": []}), 500


# ── 启动入口 ───────────────────────────────────────────

if __name__ == "__main__":
    logger.info(f"网易新闻API服务启动，端口: {PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=False)
