# Sealos 部署指南 - 网易新闻抓取 API

## 前提条件

- 已注册 Sealos 账号：https://hzh.sealos.run/ （手机号/微信/GitHub 登录均可）
- GitHub 仓库已就绪：https://github.com/ljx19900710/news-api

---

## 部署步骤（约 2 分钟）

### 步骤 1：登录 Sealos

打开 https://hzh.sealos.run/ → 用手机号/微信/GitHub 登录

### 步骤 2：进入应用管理

登录后，左侧菜单点击 **「应用管理」**（App Launchpad）

### 步骤 3：新建应用

点击右上角 **「新建应用」** 按钮

### 步骤 4：配置应用（填写以下参数）

| 配置项 | 填写内容 |
|--------|---------|
| **应用名称** | `news-api` |
| **部署方式** | 选择 **GitHub 仓库** |
| **GitHub 仓库地址** | `https://github.com/ljx19900710/news-api` |
| **分支** | `main` |
| **Dockerfile 路径** | `./Dockerfile`（默认） |
| **CPU** | 0.5 Core |
| **内存** | 512 Mi |

> 如果没有 GitHub 部署选项，选择「Docker 镜像」方式，镜像名填：
> `python:3.13-slim`，然后在「命令」里填：
> ```
> pip install flask requests beautifulsoup4 lxml python-dateutil && python app.py
> ```

### 步骤 5：配置网络

| 配置项 | 填写内容 |
|--------|---------|
| **容器端口** | `5000` |
| **外网访问** | ✅ 开启（打开开关） |

### 步骤 6：部署

点击右上角 **「部署应用」**，等待状态变为 **Running**（约 1-2 分钟）

### 步骤 7：获取访问地址

应用详情页会显示 **公网地址**，类似：
```
https://xxx.hzh.sealos.run/
```

---

## 测试 API

部署成功后，替换下面的 `{你的域名}` 为实际域名进行测试：

```bash
# 1. 健康检查
curl https://{你的域名}/health

# 2. 获取板块列表
curl https://{你的域名}/api/categories

# 3. 抓取新闻（头条，5条）
curl "https://{你的域名}/api/news?size=5&category=头条"

# 4. 关键字搜索
curl "https://{你的域名}/api/news?size=5&category=科技&keyword=AI"

# 5. 日期范围过滤
curl "https://{你的域名}/api/news?size=5&category=国内&start_date=2026-06-01&end_date=2026-06-30"
```

---

## 常见问题

**Q: 部署失败怎么办？**
- 检查 Dockerfile 路径是否正确
- 尝试增加内存到 1 Gi
- 查看 Sealos 的「日志」面板

**Q: 外网地址打不开？**
- 确认「外网访问」开关已打开
- 确认容器端口填的是 `5000`
- 等待状态变为 Running 后再访问

**Q: 如何更新代码？**
- 推送新代码到 GitHub → 在 Sealos 点击「重新部署」即可
