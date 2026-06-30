# 🚀 Zeabur 部署指南 — 3步完成

> **前提**：代码已推送到 GitHub `https://github.com/ljx19900710/news-api`，且项目包含 `Dockerfile` + `zeabur.json`，Zeabur 会自动识别。

---

## 第1步：打开 Zeabur 用 GitHub 登录

浏览器打开 👉 **https://dash.zeabur.com**

点击 **"Continue with GitHub"** 按钮，授权登录。

## 第2步：创建项目并部署

1. 点击 **"Create Project"** → 输入项目名 `news-api`
2. 选择 **"Deploy Service"** → 选 **"GitHub"**
3. 授权 Zeabur GitHub App（首次会跳转 GitHub 确认，点击 **Install**）
4. 搜索框输入 `ljx19900710/news-api` → 选中仓库
5. Zeabur 自动识别 `Dockerfile`，直接点 **"Deploy"**

> ⏱️ 首次部署约 2-3 分钟，Zeabur 会自动构建 Docker 镜像并启动。

## 第3步：获取访问域名

部署完成后，在项目页面点击服务名，复制 **"Domain"** 地址。

示例：`https://news-api.zeabur.app`

---

## 🧪 验证部署

部署完成后，用以下命令测试：

```bash
# 健康检查
curl https://你的域名.zeabur.app/health

# 获取新闻
curl "https://你的域名.zeabur.app/api/news?size=3&category=头条"

# 关键字搜索
curl "https://你的域名.zeabur.app/api/news?keyword=科技&size=5"
```

---

## 📌 注意事项

- **免费额度**：Zeabur 每月 $5 免费额度，无需绑定信用卡
- **自动休眠**：无流量时自动休眠，下次访问唤醒需几秒
- **自动部署**：之后 `git push` 到 GitHub，Zeabur 会自动重新部署
