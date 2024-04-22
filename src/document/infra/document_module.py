from injector import Module

from document.domain.i_document_selector import IDocumentSelector
from document.infra.document_selector import DocumentSelector


class DocumentModule(Module):
    def configure(self, binder):
        binder.bind(IDocumentSelector, to=DocumentSelector)
