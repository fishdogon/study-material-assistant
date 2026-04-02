# 导入读取所有资料的函数
from app.loader import load_all_documents

# 导入 chunk 切分函数
from app.chunker import chunk_documents

# 导入向量建库和检索函数
from app.retriever import build_vector_store, search_relevant_chunks

# 导入普通问答生成函数
from app.generator import generate_answer

# 导入教学讲解生成函数
from app.explainer import generate_teaching_explanation

# 导入练习题生成函数
from app.exercise_generator import generate_exercise


def init_pipeline():
    """
    初始化整个项目资料流程：
    1. 读取 txt + pdf 资料
    2. 切 chunk
    3. 建立向量库
    """

    documents = load_all_documents("data/raw")
    chunks = chunk_documents(documents)
    build_vector_store(chunks)

    return chunks


def ask_question(query: str) -> tuple[str, list[dict]]:
    """
    资料问答模式：
    检索资料后，生成普通回答。
    """
    retrieved_chunks = search_relevant_chunks(query, top_k=3)
    answer = generate_answer(query, retrieved_chunks)
    return answer, retrieved_chunks


def explain_for_teaching(query: str) -> tuple[str, list[dict]]:
    """
    教学讲解模式：
    检索资料后，生成适合教学的讲解。
    """
    retrieved_chunks = search_relevant_chunks(query, top_k=3)
    answer = generate_teaching_explanation(query, retrieved_chunks)
    return answer, retrieved_chunks


def generate_exercise_from_material(query: str) -> tuple[dict, list[dict]]:
    """
    练习题生成模式：
    检索资料后，基于资料内容生成结构化练习题。
    """
    retrieved_chunks = search_relevant_chunks(query, top_k=3)
    answer = generate_exercise(query, retrieved_chunks)
    return answer, retrieved_chunks