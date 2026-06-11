"""
LlamaIndex IngestionPipeline
"""
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.openai import OpenAIEmbedding

from ..config import settings


def build_pipeline():
    """构建摄入管线"""
    return IngestionPipeline(
        transformations=[
            SentenceSplitter(chunk_size=settings.chunk_size, chunk_overlap=settings.chunk_overlap),
            OpenAIEmbedding(model=settings.embedding_model),
            # TODO(作者）：加入 MetadataExtractor（标题、作者、时间）
            # TODO(作者）：加入自定义 Transformer（如脱敏）
        ],
    )


# TODO(作者）：实现增量更新（基于 doc_id 去重）
# TODO(作者）：支持 pipeline cache（避免重复 embedding）
