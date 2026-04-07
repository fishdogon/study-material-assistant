from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_documents(documents: list[dict]) -> list[dict]:
    """
    把读取到的原始文档切分成多个 chunk（文本块）。
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=120,
        chunk_overlap=20
    )

    chunks = []

    for doc in documents:
        split_texts = splitter.split_text(doc["content"])

        for idx, chunk_text in enumerate(split_texts):
            chunks.append({
                "id": f"{doc['source']}_{idx}",
                "source": doc["source"],
                "content": chunk_text,

                # 下面这些 metadata 继续往后传
                "source_type": doc.get("source_type", "unknown"),
                "parser_name": doc.get("parser_name", "unknown"),
                "is_ocr": doc.get("is_ocr", False)
            })

    return chunks