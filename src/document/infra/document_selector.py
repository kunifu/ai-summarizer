import random

from dotenv import load_dotenv
from kaggle import KaggleApi

from document.domain.i_document_selector import IDocumentSelector


class DocumentSelector(IDocumentSelector):
    def __init__(self) -> None:
        load_dotenv()
        # FIXME: ドメインサービス化したい
        self.__api = KaggleApi()
        self.__api.authenticate()

    def select(self) -> str:
        page_num = random.randint(0, 30)
        page_size = 10
        type = random.choice(["code", "models"])
        url = None
        if type == "code":
            model = random.choice(self.__api.model_list(sort_by="hotness", page_size=page_size, page_token=page_num))
            url = "https://www.kaggle.com/models/{}".format(model.__dict__["ref"])
        if type == "models":
            code = random.choice(self.__api.kernels_list(sort_by="hotness", page_size=page_size, page=page_num))
            url = "https://www.kaggle.com/code/{}".format(code.__dict__["ref"])
        return url
