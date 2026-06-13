# 🚀 推送到 GitHub - 详细指导

## 📁 当前状态

本地 git 仓库已初始化并提交，位于：
```
C:/Users/LENOVO/energy-news-github/
```

包含以下文件：
- `.github/workflows/energy-news.yml` - GitHub Actions 配置
- `scripts/` - Python 脚本
- `requirements.txt` - 依赖
- `README.md` - 说明文档

---

## 🔑 Step 1: 获取 GitHub Personal Access Token (PAT)

1. 访问：https://github.com/settings/tokens
2. 点击 **"Generate new token"** → **"Generate new token (classic)"**
3. 配置：
   - **Note**：`energy-news-push`
   - **Expiration**：建议 90 天
   - **Select scopes**：勾选 `repo`（全选）
4. 点击 **"Generate token"**
5. **⚠️ 立即复制 token**（只显示一次）

示例 token：`ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

---

## 🆕 Step 2: 在 GitHub 上创建新仓库

1. 访问：https://github.com/new
2. 配置：
   - **Repository name**：`energy-news`（或 `energy-news-daily`）
   - **Description**：`能源电力要闻每日自动推送 - GitHub Actions + Gemini AI`
   - **Public/Private**：自选（建议 Public，免费）
   - **⚠️ 不要勾选** "Initialize with README"（保持空仓库）
3. 点击 **"Create repository"**

创建成功后，GitHub 会显示推送指令，类似：
```
https://github.com/CNBooz/energy-news.git
```

---

## 💻 Step 3: 推送本地仓库到 GitHub

打开 **Git Bash** 或 **命令提示符**，执行以下命令：

```bash
# 进入项目目录
cd C:/Users/LENOVO/energy-news-github

# 重命名分支为 main（GitHub 默认）
git branch -M main

# 添加远程仓库（替换 <YOUR_TOKEN> 和 <YOUR_REPO>）
git remote add origin https://<YOUR_TOKEN>@github.com/CNBooz/<YOUR_REPO>.git

# 示例：
# git remote add origin https://ghp_xxxxxxxx@github.com/CNBooz/energy-news.git

# 推送到 GitHub
git push -u origin main
```

**⚠️ 注意**：
- 将 `<YOUR_TOKEN>` 替换为你的 GitHub PAT
- 将 `<YOUR_REPO>` 替换为你的仓库名（如 `energy-news`）

---

## 🔧 Step 4: 配置 GitHub Secrets

推送成功后，配置自动化所需的 Secrets：

1. 访问你的 GitHub 仓库
2. 点击 **Settings** → **Secrets and variables** → **Actions**
3. 点击 **"New repository secret"**
4. 逐个添加以下 Secrets：

| Name | Value | 说明 |
|------|-------|------|
| `GEMINI_API_KEY` | `AIza...` | 从 [Google AI Studio](https://aistudio.google.com/apikey) 获取 |
| `QQ_EMAIL_ACCOUNT` | `67340337@qq.com` | 你的 QQ 邮箱 |
| `QQ_EMAIL_AUTH_CODE` | `xxxxxx` | QQ 邮箱 SMTP 授权码 |
| `IMA_CLIENT_ID` | `dd4962571a67592aa50ec9146343419a` | IMA 客户端 ID（可选） |
| `IMA_API_KEY` | `g8WnLUpeen54d0yrZO+...` | IMA API Key（可选） |

---

## ▶️ Step 5: 手动触发测试

1. 进入 GitHub 仓库 → **Actions** 选项卡
2. 选择 **"能源电力要闻每日推送"**
3. 点击 **"Run workflow"** → **"Run workflow"**
4. 等待运行完成（约 2-5 分钟）
5. 查看日志，确认是否成功

---

## ✅ 完成！

自动化已配置完成，将于每天北京时间 20:00 自动运行。

---

## 🆘 故障排查

### 推送失败（403 错误）
- 检查 token 是否正确
- 检查 token 是否过期
- 检查仓库名是否正确

### GitHub Actions 未运行
- 检查仓库是否启用了 Actions（Settings → Actions → General）
- 检查 cron 表达式是否正确

### Gemini API 调用失败
- 检查 `GEMINI_API_KEY` 是否正确
- 检查是否超出免费额度

---

## 📝 附加说明

### 如果想推送到现有仓库（blogger-daily）

如果你想将文件添加到现有仓库 `CNBooz/blogger-daily`，而不是创建新仓库：

```bash
# 克隆现有仓库
cd ~
git clone https://<YOUR_TOKEN>@github.com/CNBooz/blogger-daily.git
cd blogger-daily

# 复制新文件到仓库
cp -r ~/energy-news-github/.github/workflows/energy-news.yml .github/workflows/
cp -r ~/energy-news-github/scripts/* scripts/
cp ~/energy-news-github/requirements.txt .
cp ~/energy-news-github/README.md .

# 提交并推送
git add .
git commit -m "feat: 添加能源电力要闻自动化"
git push origin main
```

### 如果想使用 SSH 推送（更安全）

1. 生成 SSH 密钥：`ssh-keygen -t ed25519 -C "your_email@example.com"`
2. 添加 SSH 密钥到 GitHub：https://github.com/settings/keys
3. 使用 SSH URL 推送：`git remote add origin git@github.com:CNBooz/energy-news.git`
