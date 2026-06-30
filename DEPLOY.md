# 网易新闻抓取API - 部署指南

## 方案选择

经过评估，推荐使用 **Zeabur** 进行部署，原因：
- ✅ 完全免费（每月$5额度，个人项目足够）
- ✅ **无需信用卡/银行卡验证**
- ✅ 国内团队开发，**国内访问速度快**
- ✅ 支持Python Flask应用
- ✅ 支持外网请求（可调用网易API）
- ✅ 自动HTTPS证书
- ✅ 支持GitHub一键部署

---

## 一、推送代码到GitHub

### 1. 创建GitHub仓库
打开 https://github.com/ljx19900710/news-api （如果还未创建，先创建一个空仓库）

### 2. 推送代码
```bash
cd news-api
git remote add origin git@github.com:ljx19900710/news-api.git
git branch -M main
git push -u origin main
```

> 如果SSH不可用，使用HTTPS：
> ```bash
> git remote add origin https://github.com/ljx19900710/news-api.git
> git push -u origin main
> ```

---

## 二、Zeabur部署

### 1. 注册Zeabur
访问 https://zeabur.com → 点击"Sign Up" → 用GitHub账号登录
- 无需信用卡，无需银行卡
- 注册即获得每月$5免费额度

### 2. 创建项目并部署
1. 登录后点击「New Project」
2. 项目名称填写：`news-api`
3. 点击「Add Service」→ 选择「GitHub」
4. 授权Zeabur访问GitHub仓库
5. 选择仓库 `ljx19900710/news-api`
6. Zeabur会自动检测到Python项目（通过Dockerfile）
7. 点击「Deploy」开始部署

### 3. 配置端口
部署完成后：
1. 进入服务 → 点击「Settings」
2. 端口设置为 `5000`
3. 健康检查路径设置为 `/health`

### 4. 获取访问域名
1. 在服务页面点击「Networking」
2. 点击「Generate Domain」生成域名
3. 格式如：`https://news-api.zeabur.app`
4. 等待1-2分钟域名生效

---

## 三、验证部署

部署完成后，使用以下命令测试：

```bash
# 1. 健康检查
curl https://你的域名.zeabur.app/health

# 2. 获取板块列表
curl https://你的域名.zeabur.app/api/categories

# 3. 获取新闻（默认5条头条）
curl "https://你的域名.zeabur.app/api/news?size=5"

# 4. 按关键字搜索
curl "https://你的域名.zeabur.app/api/news?keyword=科技&size=10"

# 5. 按日期范围过滤
curl "https://你的域名.zeabur.app/api/news?start_date=2026-06-01&end_date=2026-06-30&size=20"

# 6. 指定板块
curl "https://你的域名.zeabur.app/api/news?category=军事&size=5"
```

### 测试脚本
也可运行本地测试脚本（修改BASE_URL为你的域名）：
```bash
# 编辑 test_api.py 中的 BASE_URL
# BASE_URL = "https://你的域名.zeabur.app"
python test_api.py
```

---

## 四、API使用说明

### 接口地址
```
GET https://你的域名.zeabur.app/api/news
```

### 请求参数
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| start_date | string | 否 | 开始日期，格式：2026-01-01 |
| end_date | string | 否 | 结束日期，格式：2026-01-31 |
| size | int | 否 | 获取条数，默认20，最大100 |
| category | string | 否 | 板块名称（头条/国内/国际/军事/财经/科技/娱乐/体育等） |
| keyword | string | 否 | 关键字搜索 |

### 返回格式
```json
{
  "code": 200,
  "message": "成功获取 5 条新闻",
  "data": [
    {
      "title": "新闻标题",
      "content": "纯文本内容...",
      "html_content": "<p>HTML内容...</p>",
      "image_urls": ["https://xxx.jpg"],
      "source": "来源",
      "ptime": "2026-06-30 12:43:56",
      "docid": "L0LV1KIU000189PS",
      "url": "https://www.163.com/news/article/L0LV1KIU000189PS.html",
      "digest": "新闻摘要"
    }
  ],
  "params": { ... }
}
```

---

## 五、注意事项

1. **自动休眠**：Zeabur免费版在无流量一段时间后会自动休眠，下次请求会有几秒冷启动延迟
2. **请求频率**：不要过于频繁请求网易API，避免被限流
3. **免费额度**：每月$5，用完后服务暂停，下月重置
4. **扩展方案**：如果免费额度不够用，可升级到Dev Plan（$5/月）

---

## 六、备选方案

如果Zeabur不可用，备选方案：

### Render (render.com)
- 免费版支持Python Flask
- 需要GitHub账号
- 可能需信用卡验证（视地区而定）
- 域名格式：`xxx.onrender.com`

### Railway (railway.app)
- 注册送$5额度
- 需要GitHub账号
- 目前可能需要信用卡验证
