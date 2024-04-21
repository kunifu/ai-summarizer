# ai-summarizer
ChatGPTを使って、論文を要約＆その内容をSlackに通知するスクリプト。

## インストール
```zsh
rye install ai-summarizer
```

## 使い方

### 事前準備
.env ファイルを作成し、以下の環境変数を設定してください。

```.env
CHAT_GPT_USERNAME=<your_username>
CHAT_GPT_PASSWORD=<your_password>
SLACK_WEBHOOK_URL=<your_webhook_url>
```

### 定期実行化
毎日 9 時に実行する場合、以下のように cron を設定してください。
```cron
0 9 * * * /Users/hogehoge/.rye/shims/python /Users/hogehoge/renga/workspace/ai-summarizer/main.py
```

