import os
import re
import sys

from dotenv import load_dotenv
from injector import Injector
from slack_sdk.webhook import WebhookClient

sys.path.append("src")
from chat_ai.infra.chat_ai_module import ChatAIModule
from chat_ai.service.chat_ai_summarize_service import ChatAISummarizeService
from document.infra.document_module import DocumentModule
from document.service.document_recommend_service import DocumentRecommendService

PROMPT_FORMAT = """以下を要約しマークダウン形式で出力してください。
{}
なお、コピー可能な形式でお願いします。

#制約
・タイトルは原文まま。
・箇条書きで3行以内で要約する。
・日本語で要約する。
・重要なキーワードを含める。
・課題や特徴、利点を含める。
・1行あたりの文字数は100文字以内。
・文章は簡潔にまとめる。

#出力例
```
**[transformer-Building Autoencoders](https://www.kaggle.com/code/susanta21/transformer-building-autoencoders)**
:thinking_face: 課題> ディープラーニングモデルの訓練時の過剰適合を緩和
:bulb: 特徴> Kerasを使用してオートエンコーダーを構築
:heart_hands: 利点> 効率的なデータ圧縮と特徴抽出が可能
```"""


def markdown_to_slack_mrkdwn(text):
    # MarkdownリンクをSlackのリンク形式に変換
    slack_link_format = re.sub(r"\[(.*?)\]\((.*?)\)", r"<\2|\1>", text)

    # 強調（太字）をMarkdownからSlack形式に変換
    slack_bold_format = re.sub(r"\*\*(.*?)\*\*", r"*\1*", slack_link_format)

    return slack_bold_format


if __name__ == "__main__":
    injector = Injector([ChatAIModule(), DocumentModule()])

    url = injector.get(DocumentRecommendService).recommend()

    prompt = PROMPT_FORMAT.format(url)
    summary = injector.get(ChatAISummarizeService).summarize(prompt)

    # mrkdwn形式に変換
    summary = markdown_to_slack_mrkdwn(summary)

    # FIXME: MM化したい
    load_dotenv()
    webhook = WebhookClient(os.getenv("SLACK_WEBHOOK_URL"))
    webhook.send(text=summary)
