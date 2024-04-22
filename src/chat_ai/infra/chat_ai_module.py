from injector import Module

from chat_ai.domain.i_chat_comleter import IChatCompleter
from chat_ai.infra.chatgpt_completer import ChatGPTCompleter


class ChatAIModule(Module):
    def configure(self, binder):
        binder.bind(IChatCompleter, to=ChatGPTCompleter)
