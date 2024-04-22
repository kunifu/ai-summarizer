from injector import inject

from document.domain.i_document_selector import IDocumentSelector


class DocumentRecommendService:
    @inject
    def __init__(self, document_selector: IDocumentSelector) -> None:
        self.__document_selector = document_selector

    def recommend(self) -> str:
        return self.__document_selector.select()
