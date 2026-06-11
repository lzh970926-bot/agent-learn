"""
多格式文档解析：PDF / Word / Markdown / HTML
"""
from pathlib import Path
from llama_index.core import SimpleDirectoryReader


def parse_documents(directory: str | Path) -> list:
    """统一解析入口"""
    # TODO(作者)：配置 file_extractor
    #   - PDF: PyMuPDFReader
    #   - Word: DocxReader
    #   - MD: MarkdownReader
    reader = SimpleDirectoryReader(
        input_dir=directory,
        recursive=True,
    )
    return reader.load_data()


# TODO(作者)：添加 OCR 支持（扫描版 PDF）
# TODO(作者）：支持结构化表格抽取
