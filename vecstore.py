from abc import ABC, abstractmethod
from pathlib import Path

from llama_index import ServiceContext
from llama_index import StorageContext
from llama_index.vector_stores import FaissVectorStore
from llama_index.vector_stores import ChromaVectorStore
from llama_index import VectorStoreIndex
from langchain.embeddings.huggingface import HuggingFaceBgeEmbeddings
from llama_index import ServiceContext

embed_model = HuggingFaceBgeEmbeddings(model_name="BAAI/bge-base-en")

service_context = ServiceContext.from_defaults(embed_model=embed_model)

DEFAULT_INDEX_SETTINGS = {
    "vector_store": "faiss",
    "faiss_index_type": "IDMap,Flat",
    "faiss_metric_type": "L2",
    "faiss_params": {
        "nprobe": 10
    },
    "embedding_model": {
        "model_name": "paraphrase-xlm-r-multilingual-v1",
    }

}


class BaseStore(ABC):
    @abstractmethod
    def search(self, query, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def write(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def add(self, *args, **kwargs):
        raise NotImplementedError


class LocalStore(BaseStore, ABC):
    def __init__(self, collection_name, persist_dir: Path = './data', settings=None):
        self.settings = settings or {}
        self.persist_dir = persist_dir
        self.collection_name = collection_name
        self.store = self._load()

    def _get_index_and_store_fname(self):
        index_file = self.persist_dir / f"{self.collection_name}.index"
        store_file = self.persist_dir / f"{self.collection_name}.pkl"
        return index_file, store_file

    @abstractmethod
    def _load(self):
        raise NotImplementedError

    @abstractmethod
    def _write(self, docs, metadatas):
        raise NotImplementedError


class VecStore(LocalStore):
    """
    Class to abstract over different vector stores.
    """

    def __init__(self, collection_name, persist_dir: Path = './data', settings=None):
        super().__init__(collection_name, persist_dir, settings)

        self.service_context = ServiceContext.from_defaults(embed_model=self.settings.get('embedding_model'))

        if self.settings.get('vector_store').lower() == 'faiss':
            try:
                self.index = FaissVectorStore.from_persist_path(self.persist_dir.as_posix())
            except FileNotFoundError:
                self.index = None

            # self.index = faiss.index_factory(768, self.settings.get('faiss_index_type'))
            # self.index_metric_type = self.settings.get('faiss_metric_type')
            # self.index.nprobe = self.settings.get('faiss_params').get('nprobe')
            # self.store = FaissVectorStore(self.index)
            # self.storage_context = StorageContext.from_defaults(vector_store=self.store)

            # raise NotImplementedError
        elif self.settings.get('vector_store').lower() == 'chroma':
            import chromadb
            chroma_client = chromadb.PersistentClient(path=self.persist_dir.as_posix())
            chroma_collection = chroma_client.create_collection(self.collection_name)
            self.store = ChromaVectorStore(chroma_collection=chroma_collection)
            self.storage_context = StorageContext.from_defaults(vector_store=self.store)

    def _load(self):
        index_file, store_file = self._get_file_names()
        if not index_file.exists() or not store_file.exists():
            return None
        index = VectorStoreIndex.load(index_file, storage_context=self.storage_context)
        return index

    def _get_file_names(self):
        index_file = self.persist_dir / f"{self.collection_name}.index"
        store_file = self.persist_dir / f"{self.collection_name}.pkl"
        return index_file, store_file

    def get_index(self, documents):
        return VectorStoreIndex.from_documents(documents,
                                               storage_context=self.storage_context,
                                               service_context=self.service_context)

    def add_documents(self, documents, metadatas=None):
        if not self.index:
            VectorStoreIndex.from_documents(documents, storage_context=self.storage_context)
        self.index = self.get_index(documents, metadatas)
        return self
