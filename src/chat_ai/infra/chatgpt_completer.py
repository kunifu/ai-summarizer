import os

import clipboard
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

from chat_ai.domain.i_chat_comleter import IChatCompleter


class ChatGPTCompleter(IChatCompleter):
    def __init__(self) -> None:
        self.playwright = sync_playwright().start()
        self.__browser = self.playwright.chromium.launch(headless=False)
        self.__context = self.__browser.new_context(locale="ja-JP", timezone_id="Asia/Tokyo")
        self.__page = self.__context.new_page()

    def __del__(self):
        self.__page.close()
        self.__context.close()
        self.__browser.close()
        self.playwright.stop()

    def complete(self, prompt: str) -> str:
        load_dotenv()
        self.__login(os.getenv("CHAT_GPT_USERNAME"), os.getenv("CHAT_GPT_PASSWORD"))
        self.__switch_chat("https://chat.openai.com/g/g-pNWGgUYqS-webpilot")
        return self.__interact(prompt)

    def __login(self, username: str, password: str) -> None:
        chatgpt_url = "https://chat.openai.com/"
        self.__page.goto(chatgpt_url)
        self.__page.wait_for_url(chatgpt_url)
        self.__page.wait_for_timeout(1000)

        self.__page.click("//div[text()='Log in']")
        self.__page.click("//span[text()='Google で続ける']")
        self.__page.wait_for_timeout(1000)

        self.__page.fill("//input[@type='email']", username)
        self.__page.keyboard.press("Enter")
        self.__page.wait_for_timeout(1000)

        self.__page.fill("//input[@name='Passwd']", password)
        self.__page.keyboard.press("Enter")
        stealth_sync(self.__page)
        self.__page.wait_for_timeout(1000)

        # ワークスペースを選択
        self.__page.wait_for_url(chatgpt_url)
        self.__page.click("svg.icon-lg.my-auto")
        self.__page.wait_for_timeout(1000)

    def __switch_chat(self, url: str = None) -> None:
        self.__page.goto(url)
        self.__page.wait_for_url(url)
        self.__page.wait_for_timeout(1000)

    def __interact(self, prompt: str) -> str:
        self.__page.fill("textarea", prompt)
        self.__page.keyboard.press("Enter")

        self.__page.wait_for_selector("//button[@aria-label='Stop generating']", state="visible")
        self.__page.wait_for_selector("//button[@aria-label='Stop generating']", state="hidden")
        self.__page.wait_for_selector("//button[@data-testid='send-button']", state="visible")

        self.__page.click("//button[text()='Copy code']")
        return clipboard.paste()
