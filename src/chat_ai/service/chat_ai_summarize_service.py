from injector import inject

from chat_ai.domain.i_chat_comleter import IChatCompleter


class ChatAISummarizeService:
    @inject
    def __init__(self, chat_completer: IChatCompleter) -> None:
        self.__chat_completer = chat_completer

    def summarize(self, prompt: str) -> str:
        return self.__chat_completer.complete(prompt)
