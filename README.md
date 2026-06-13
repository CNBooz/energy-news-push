# 能源电力要闻 - GitHub Actions 自动化

每天自动抓取能源电力行业新闻，通过 **DeepSeek AI** 生成要闻汇总，发送邮件并归档到知识库。

## ✨ 功能特性

- 📰 **自动抓取**：从国家能源局、国家电网、能源杂志等网站抓取最新新闻
- 🤖 **AI 生成**：使用 **DeepSeek-V3** 生成专业要闻汇总（超低价）
- 📧 **邮件推送**：自动发送到 QQ 邮箱
- 📚 **知识库归档**：自动归档到 IMA 知识库（可选）
- ⏰ **定时运行**：每天北京时间 20:00 自动运行

## 🚀 快速开始

### 1. 获取 DeepSeek API Key（超低价）

1. 访问 [DeepSeek 开放平台](https://platform.deepseek.com/)
2. 注册登录
3. 进入 **"API Keys"** → **"创建 API Key"**
4. 复制 Key（格式：`sk-xxxxxxxxxx`）
5. **价格**：约 ¥0.001/千 Token（充值 ¥10 可用很久）

### 2. 创建仓库

将本仓库推送到你的 GitHub 账号下。

### 3. 配置 GitHub Secrets

在 GitHub 仓库 → Settings → Secrets and variables → Actions 中，添加以下 Secrets：

| Secret 名称 | 说明 | 获取方式 |
|-------------|------|----------|
| `DEEPSEEK_API_KEY` | DeepSeek API Key | 从 [DeepSeek 平台](https://platform.deepseek.com/) 获取 |
| `QQ_EMAIL_ACCOUNT` | QQ 邮箱账号 | 你的 QQ 邮箱（如：67340337@qq.com） |
| `QQ_EMAIL_AUTH_CODE` | QQ 邮箱授权码 | QQ 邮箱 → 设置 → 账户 → 开启 SMTP → 获取授权码 |
| `IMA_CLIENT_ID` | IMA 客户端 ID（可选） | 从 IMA 平台获取 |
| `IMA_API_KEY` | IMA API Key（可选） | 从 IMA 平台获取 |

### 4. 启用 GitHub Actions

1. 进入仓库 → Actions 选项卡
2. 启用 Workflows
3. 可以手动触发测试：Actions → 能源电力要闻每日推送 → Run workflow

## 📁 项目结构

```
.
├── .github/workflows/energy-news.yml  # GitHub Actions 配置
├── scripts/                            # Python 脚本
│   ├── energy_news.py                  # 主脚本
│   ├── rss_fetcher.py                 # 新闻抓取
│   ├── gemini_generator.py            # DeepSeek AI 调用（原 gemini 命名保留）
│   ├── email_sender.py                # 邮件发送
│   └── ima_uploader.py               # IMA 归档（可选）
├── output/                             # 生成的文件（.gitignore）
├── history/                            # 历史记录（用于去重）
├── requirements.txt                    # Python 依赖
└── README.md                          # 本文件
```

## ⚙️ 自定义配置

### 修改新闻源

编辑 `scripts/rss_fetcher.py`，修改 `RSS_SOURCES` 列表：

```python
RSS_SOURCES = [
    {"name": "你的新闻源", "url": "https://...", "type": "rss", "rss": "https://.../rss"},
    # 或
    {"name": "你的新闻源", "url": "https://...", "type": "web"},
]
```

### 修改邮件收件人

编辑 `.github/workflows/energy-news.yml`，修改环境变量或直接修改 `scripts/email_sender.py` 中的默认收件人。

### 修改运行时间

编辑 `.github/workflows/energy-news.yml`，修改 `cron` 表达式：

```yaml
schedule:
  - cron: '0 12 * * *'  # 每天 UTC 12:00 = 北京时间 20:00
```

## 🐛 故障排查

### DeepSeek API 调用失败

- 检查 `DEEPSEEK_API_KEY` 是否正确
- 检查账户余额是否充足（约 ¥0.001/千 Token）
- 查看 GitHub Actions 日志

### 邮件发送失败

- 检查 `QQ_EMAIL_AUTH_CODE` 是否正确（不是邮箱密码，是授权码）
- 确认 QQ 邮箱已开启 SMTP 服务

### 新闻抓取失败

- 某些网站可能有反爬机制
- 可以修改为使用 RSS 源（更稳定）

## 📝 许可证

MIT License

## 🙏 致谢

- [DeepSeek](https://www.deepseek.com/) - 超低价 AI 生成
- [GitHub Actions](https://github.com/features/actions) - 免费自动化
- [feedparser](https://feedparser.readthedocs.io/) - RSS 解析库
