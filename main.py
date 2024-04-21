import os
import random
import time

import clipboard
import selenium.common.exceptions as Exceptions
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from slack_sdk.webhook import WebhookClient
from talkingheads import ChatGPTClient


class ConsensusGPT(ChatGPTClient):
    def __init__(self, **kwargs) -> None:
        super().__init__(
            username=os.getenv("CHAT_GPT_USERNAME"),
            password=os.getenv("CHAT_GPT_PASSWORD"),
            **kwargs,
        )

    def login(self, username: str, password: str):
        # Find login button, click it
        login_button = self.wait_until_appear(By.XPATH, "//div[text()='Log in']")
        login_button.click()
        self.logger.info("Clicked login button")
        time.sleep(1)

        # Find Google login button, click it
        google_button = self.wait_until_appear(By.XPATH, "//span[text()='Google で続ける']")
        google_button.click()
        self.logger.info("Clicked Google login button")
        time.sleep(1)

        # Find email textbox, enter e-mail
        email_box = self.wait_until_appear(By.XPATH, "//input[@type='email']")
        email_box.send_keys(username)
        self.logger.info("Filled email box")
        # Click continue
        email_box.send_keys(Keys.ENTER)
        time.sleep(1)
        self.logger.info("Clicked continue button")

        # Find password textbox, enter password
        pass_box = self.wait_until_appear(By.XPATH, "//input[@name='Passwd']")
        pass_box.send_keys(password)
        self.logger.info("Filled password box")
        # Click continue
        pass_box.send_keys(Keys.ENTER)
        time.sleep(1)
        self.logger.info("Logged in")

        # Select a Workspace
        # 会社のワークスペースを選択（現状は一番目が会社のワークスペースになっている）
        workspace = self.wait_until_appear(By.CSS_SELECTOR, "svg.icon-lg.my-auto")
        workspace.click()
        time.sleep(1)

        # Jump to the chat page
        self.browser.get(self.url)
        time.sleep(1)

        try:
            # Pass introduction
            WebDriverWait(self.browser, 5).until(
                EC.presence_of_element_located((By.XPATH, self.markers.tutorial_xq))
            ).click()

            self.logger.info("Info screen passed")
        except Exceptions.TimeoutException:
            self.logger.info("Info screen skipped")
        except Exception as err:
            self.logger.error("Something unexpected: %s", err)

    def open_chat(self, url: str = None):
        # Open chat
        self.browser.get(url)
        self.browser.forward()
        time.sleep(1)
        self.logger.info("Chat opened")

    def get_summary(self, prompt: str):
        self.logger.info("Prompt: \n%s", prompt)
        # メッセージを送信
        text_area = self.browser.find_elements(By.TAG_NAME, self.markers.textarea_tq)
        if not text_area:
            self.logger.info("Unable to locate text area tag. Switching to ID search")
            text_area = self.browser.find_elements(By.ID, self.markers.textarea_iq)
        if not text_area:
            raise RuntimeError("Unable to find the text prompt area. Please raise an issue with verbose=True")

        text_area = text_area[0]

        for each_line in prompt.split("\n"):
            text_area.send_keys(each_line)
            text_area.send_keys(Keys.SHIFT + Keys.ENTER)
        text_area.send_keys(Keys.RETURN)
        time.sleep(1)

        # レスポンスを取得
        self.logger.info("Message sent, waiting for response")
        self.wait_until_disappear(By.XPATH, self.markers.wait_xq)
        self.wait_until_appear(By.XPATH, self.markers.send_btn_xq)
        time.sleep(1)

        response = None
        for _ in range(5):
            time.sleep(1)
            l_response = self.find_or_fail(By.XPATH, self.markers.chatbox_xq, return_type="last")
            if l_response.text and l_response.text == response:
                break
            response = l_response.text

        if not response:
            self.logger.error("There is no response, something is wrong")
            raise RuntimeError("No response")

        self.logger.info("response is ready")

        # マークダウン部分を取得
        markdown = self.browser.find_element(By.XPATH, "//button[text()='Copy code']")
        markdown.click()
        time.sleep(1)
        summary = clipboard.paste()
        self.logger.info("Summary: \n%s", summary)

        return summary

    def get_summary_with_retries(self, prompt, max_retries=5):
        for attempt in range(max_retries):
            try:
                self.open_chat("https://chat.openai.com/g/g-bo0FiWLY7-consensus")
                return self.get_summary(prompt)
            except Exception as e:
                self.logger.error(f"Attempt {attempt+1} failed: {e}")
                if attempt < max_retries - 1:
                    self.logger.info("Retrying...")
                    time.sleep(1)
                else:
                    self.logger.error("Failed to get the summary")
                    raise e


TOPICS = [
    "レコメンドシステム",
    "自然言語処理",
    "人工知能",
    "機械学習",
    "Web開発",
    "データサイエンス",
    "データ分析",
    "ソフトウェア設計",
]


if __name__ == "__main__":
    load_dotenv()

    # Get the summary
    try:
        bot = ConsensusGPT(headless=False, verbose=True)
        prompt = """{}に関する技術論文を1つ選び、要約しSlackのマークダウン形式で出力してください。
なお、リンクの形式は<URL|タイトル>としてください。

#制約
・タイトルは原文まま。
・箇条書きで3行以内で要約する。
・日本語で要約する。
・重要なキーワードを含める。
・1行あたりの文字数は100文字以内。
・文章は簡潔にまとめる。
・被引用数が最低3件以上ある。
・できるだけ新しい論文を選ぶ。

#出力例
```
*<https://research.google/pubs/pub42186|Deep Neural Networks for YouTube Recommendations>*
・YouTubeのレコメンドシステムにおいて、深層学習を用いたアーキテクチャを提案。
・ユーザーの視聴履歴を入力とし、モデルはユーザーの好みを予測する。
・ニューラルネットワークは、ユーザーの関心を高い精度で予測することが可能。
```""".format(random.choice(TOPICS))
        summary = bot.get_summary_with_retries(prompt)
    finally:
        if bot:
            del bot

    # Send the summary to Slack
    webhook = WebhookClient(os.getenv("SLACK_WEBHOOK_URL"))
    webhook.send(text=summary)
