# 网易新闻抓取API

基于 Python Flask 的 REST API 服务，从网易新闻 (news.163.com) 抓取新闻数据。

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动服务
python app.py

# 3. 测试
python test_api.py
```

## API 接口

### 获取新闻列表

```
GET /api/news
```

**请求参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| start_date | string | 否 | - | 新闻发布开始日期，格式 `2026-01-01` |
| end_date | string | 否 | - | 新闻发布结束日期，格式 `2026-01-31` |
| size | int | 否 | 20 | 获取条数，最大100 |
| category | string | 否 | 头条 | 板块：头条/国内/国际/军事/财经/科技/娱乐/体育等 |
| keyword | string | 否 | - | 关键字模糊搜索（匹配标题和摘要） |

**返回格式：**

```json
{
  "code": 200,
  "message": "成功获取 5 条新闻",
  "data": [
    {
      "title": "新闻标题",
      "content": "纯文本内容...",
      "html_content": "<p>HTML内容...</p>",
      "image_urls": ["https://xxx.jpg", "https://yyy.png"],
      "source": "来源",
      "ptime": "2026-06-30 12:43:56",
      "docid": "L0LV1KIU000189PS",
      "url": "https://www.163.com/news/article/L0LV1KIU000189PS.html",
      "digest": "新闻摘要"
    }
  ],
  "params": {
    "category": "头条",
    "size": 5,
    "start_date": "",
    "end_date": "",
    "keyword": ""
  }
}
```

### 获取板块列表

```
GET /api/categories
```

### 健康检查

```
GET /health
```

## 示例请求

```bash
# 获取头条新闻
curl "http://localhost:5000/api/news?size=5"

# 按关键字搜索
curl "http://localhost:5000/api/news?keyword=科技&size=10"

# 按日期范围过滤
curl "http://localhost:5000/api/news?start_date=2026-06-01&end_date=2026-06-30&size=20"

# 指定板块
curl "http://localhost:5000/api/news?category=军事&size=10"

# 组合查询
curl "http://localhost:5000/api/news?category=财经&keyword=股市&start_date=2026-06-01&end_date=2026-06-30&size=20"
```

## 支持的板块

头条、国内、国际、军事、财经、科技、娱乐、体育、汽车、房产、旅游、教育、健康、游戏、时尚、数码、手机

## 技术栈

- Python 3.x
- Flask (Web框架)
- Requests (HTTP请求)
- BeautifulSoup4 + lxml (HTML解析)

## 数据来源

新闻数据来自网易新闻公开API接口：
- 新闻列表: `https://3g.163.com/touch/reconstruct/article/list/{channel_id}/0-{size}.html`
- 新闻详情: `https://c.m.163.com/nc/article/{docid}/full.html`
