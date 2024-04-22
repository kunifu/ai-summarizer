import os
import sys

from dotenv import load_dotenv
from injector import Injector
from slack_sdk.webhook import WebhookClient

sys.path.append("src")
from chat_ai.infra.chat_ai_module import ChatAIModule
from chat_ai.service.chat_ai_summarize_service import ChatAISummarizeService
from document.infra.document_module import DocumentModule
from document.service.document_recommend_service import DocumentRecommendService

PROMPT_FORMAT = """以下を要約しSlackのマークダウン形式で出力してください。
{}
なお、リンクの形式は<URL|タイトル>としてください。

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
*<https://www.kaggle.com/code/susanta21/transformer-building-autoencoders|transformer-Building Autoencoders>*
:thinking_face: 課題> ディープラーニングモデルの訓練時の過剰適合を緩和
:bulb: 特徴> Kerasを使用してオートエンコーダーを構築
:heart_hands: 利点> 効率的なデータ圧縮と特徴抽出が可能
```"""

if __name__ == "__main__":
    injector = Injector([ChatAIModule(), DocumentModule()])

    url = injector.get(DocumentRecommendService).recommend()

    prompt = PROMPT_FORMAT.format(url)
    summary = injector.get(ChatAISummarizeService).summarize(prompt)

    # FIXME: MM化したい
    load_dotenv()
    webhook = WebhookClient(os.getenv("SLACK_WEBHOOK_URL"))
    webhook.send(text=summary)
