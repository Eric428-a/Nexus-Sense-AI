"""FastAPI dependency providers."""
from nexus.database.repositories.documents import DocumentRepository
_document_repository=DocumentRepository()
def get_document_repository(): return _document_repository
