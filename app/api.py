# 导入 FastAPI 主类
from fastapi import FastAPI, UploadFile, File

# 导入你已经写好的核心逻辑
from app.pipeline import init_pipeline, ask_question, explain_for_teaching, generate_exercise_from_material

# 导入请求体结构
from app.schemas import AskRequest, ExplainRequest, ExerciseRequest

# 导入文件保存函数
from app.file_manager import save_upload_file


# 创建 FastAPI 应用实例
app = FastAPI(
    title="Study Material Assistant API",
    description="学习资料智能助手后端接口",
    version="1.0.0"
)


# 用一个简单的全局变量，记录当前是否已经初始化过索引
# 注意：这是最小版本写法，后面可以继续优化
INDEX_READY = False


@app.get("/")
def root():
    """
    根路径测试接口。
    用来确认服务是否正常启动。
    """
    return {
        "message": "Study Material Assistant API is running"
    }


@app.post("/materials/upload")
def upload_material(file: UploadFile = File(...)):
    """
    上传学习资料文件。

    支持 txt / pdf。
    上传后文件会被保存到 data/raw 目录。
    """

    saved_path = save_upload_file(file)

    return {
        "message": "文件上传成功",
        "filename": file.filename,
        "saved_path": saved_path
    }


@app.post("/materials/index")
def build_index():
    """
    建立 / 重建资料索引。
    它会：
    1. 读取 data/raw 下的资料
    2. 切 chunk
    3. 建向量库
    """

    global INDEX_READY

    chunks = init_pipeline()
    INDEX_READY = True

    # 顺手做一个来源统计
    source_count = {}
    for chunk in chunks:
        source = chunk["source"]
        source_count[source] = source_count.get(source, 0) + 1

    return {
        "message": "索引构建完成",
        "chunk_count": len(chunks),
        "source_count": source_count
    }


@app.post("/qa/ask")
def qa_ask(request: AskRequest):
    """
    资料问答接口。
    """

    if not INDEX_READY:
        return {
            "error": "索引尚未初始化，请先调用 /materials/index"
        }

    answer, retrieved_chunks = ask_question(request.query)

    return {
        "mode": "qa",
        "query": request.query,
        "answer": answer,
        "retrieved_chunks": retrieved_chunks
    }


@app.post("/teaching/explain")
def teaching_explain(request: ExplainRequest):
    """
    教学讲解接口。
    """

    if not INDEX_READY:
        return {
            "error": "索引尚未初始化，请先调用 /materials/index"
        }

    answer, retrieved_chunks = explain_for_teaching(request.query)

    return {
        "mode": "teaching",
        "query": request.query,
        "answer": answer,
        "retrieved_chunks": retrieved_chunks
    }


@app.post("/exercises/generate")
def exercise_generate(request: ExerciseRequest):
    """
    练习题生成接口。
    """

    if not INDEX_READY:
        return {
            "error": "索引尚未初始化，请先调用 /materials/index"
        }

    answer, retrieved_chunks = generate_exercise_from_material(request.query)

    # 这里 answer 是结构化 dict
    # style 用来控制返回时展示哪些字段
    if request.style == "1":
        # 只出题：去掉 answer / explanation
        simplified = {
            "topic": answer["topic"],
            "grade": answer["grade"],
            "exercises": []
        }

        for item in answer["exercises"]:
            simplified["exercises"].append({
                "title": item["title"],
                "problem": item["problem"],
                "intent": item["intent"],
                "hint": item["hint"]
            })

        final_answer = simplified

    elif request.style == "3":
        # 出题 + 讲解：保留全部
        final_answer = answer

    else:
        # 默认：出题 + 答案
        simplified = {
            "topic": answer["topic"],
            "grade": answer["grade"],
            "exercises": []
        }

        for item in answer["exercises"]:
            simplified["exercises"].append({
                "title": item["title"],
                "problem": item["problem"],
                "intent": item["intent"],
                "hint": item["hint"],
                "answer": item["answer"]
            })

        final_answer = simplified

    return {
        "mode": "exercise",
        "query": request.query,
        "style": request.style,
        "answer": final_answer,
        "retrieved_chunks": retrieved_chunks
    }