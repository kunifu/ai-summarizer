# ai-summarizer
Script to summarize text using ChatGPT and notify the contents to Slack.

## Installation
```zsh
rye sync
```

## Usage

### Required

```.env
CHATGPT_USERNAME=<your_username>
CHATGPT_PASSWORD=<your_password>
SLACK_WEBHOOK_URL=<your_webhook_url>
```

## Tips

### Run the script periodically
You can run the script periodically using `cron`.

```cron
0 9 * * * /Users/kunifu/workspace/ai-summarizer/.venv/bin/python /Users/kunifu/workspace/ai-summarizer/main.py
```

