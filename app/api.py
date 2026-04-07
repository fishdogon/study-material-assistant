# 导入 FastAPI 主类
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# 导入你已经写好的核心逻辑
from app.pipeline import init_pipeline, ask_question, explain_for_teaching, generate_exercise_from_material

# 导入请求体结构
from pathlib import Path

from app.schemas import AskRequest, ExplainRequest, ExerciseRequest, MaterialMetadataUpdateRequest

# 导入文件保存函数
from app.file_manager import save_upload_file, list_materials, delete_material_file, filter_materials
from app.material_metadata import update_material_ai_suggestions, update_material_metadata
from app.material_tagger import infer_material_metadata

def build_source_summary(retrieved_chunks: list[dict]) -> dict:
    """
    根据检索结果，生成更适合前端展示的来源摘要。
    """

    source_types = [chunk.get("source_type", "unknown") for chunk in retrieved_chunks]
    unique_source_types = sorted(list(set(source_types)))
    contains_ocr = any(chunk.get("is_ocr", False) for chunk in retrieved_chunks)

    # 用第一条命中的来源类型，作为 primary source
    primary_source_type = retrieved_chunks[0].get("source_type", "unknown") if retrieved_chunks else "unknown"

    if contains_ocr:
        note = "本次答案包含 OCR 图片资料，可能存在识别误差。"
    else:
        note = "本次答案来自文本资料。"

    return {
        "source_types": unique_source_types,
        "primary_source_type": primary_source_type,
        "contains_ocr": contains_ocr,
        "note": note
    }


def resolve_source_names(
    source_names: list[str],
    subject: str,
    grade: str,
    topic: str
) -> list[str] | None:
    """
    统一把显式文件名过滤和元信息过滤解析成 source 名称列表。
    """

    has_filters = bool(source_names or subject.strip() or grade.strip() or topic.strip())
    if not has_filters:
        return None

    filtered = filter_materials(
        source_names=source_names,
        subject=subject,
        grade=grade,
        topic=topic,
    )
    return [item["filename"] for item in filtered]

# 创建 FastAPI 应用实例
app = FastAPI(
    title="Study Material Assistant API",
    description="学习资料智能助手后端接口",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    suggested_metadata = {"subject": "", "grade": "", "topic": ""}

    try:
        suggested_metadata = infer_material_metadata(Path(saved_path))
        update_material_ai_suggestions(file.filename, suggested_metadata)
    except Exception:
        pass

    return {
        "message": "文件上传成功",
        "filename": file.filename,
        "saved_path": saved_path,
        "suggested_metadata": suggested_metadata,
    }


@app.get("/materials")
def get_materials():
    """
    获取当前资料列表。
    """
    return {
        "materials": list_materials()
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

    try:
        chunks = init_pipeline()
        INDEX_READY = True
    except Exception as exc:
        INDEX_READY = False
        raise HTTPException(status_code=500, detail=f"索引构建失败：{exc}") from exc

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


@app.delete("/materials/{filename:path}")
def remove_material(filename: str):
    """
    删除指定资料，并重建索引。
    """

    deleted = delete_material_file(filename)
    if not deleted:
        raise HTTPException(status_code=404, detail="资料不存在")

    global INDEX_READY
    try:
        chunks = init_pipeline()
        INDEX_READY = len(chunks) > 0
    except Exception as exc:
        INDEX_READY = False
        raise HTTPException(status_code=500, detail=f"资料已删除，但索引重建失败：{exc}") from exc

    return {
        "message": "资料删除成功",
        "filename": filename,
        "index_ready": INDEX_READY,
        "chunk_count": len(chunks)
    }


@app.patch("/materials/{filename:path}")
def update_material(filename: str, request: MaterialMetadataUpdateRequest):
    """
    更新资料元信息。
    """
    material_names = {item["filename"] for item in list_materials()}
    if filename not in material_names:
        raise HTTPException(status_code=404, detail="资料不存在")

    metadata = update_material_metadata(filename, request.model_dump())

    return {
        "message": "资料元信息更新成功",
        "filename": filename,
        "metadata": metadata
    }


@app.post("/materials/{filename:path}/suggest-metadata")
def suggest_material_metadata(filename: str):
    """
    为指定资料重新生成 AI 建议标签。
    """
    material_names = {item["filename"] for item in list_materials()}
    if filename not in material_names:
        raise HTTPException(status_code=404, detail="资料不存在")

    file_path = Path("data/raw") / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="资料不存在")

    suggestions = infer_material_metadata(file_path)
    metadata = update_material_ai_suggestions(filename, suggestions)

    return {
        "message": "AI 建议标签已更新",
        "filename": filename,
        "metadata": metadata,
        "suggested_metadata": suggestions,
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

    resolved_source_names = resolve_source_names(
        source_names=request.source_names,
        subject=request.subject,
        grade=request.grade,
        topic=request.topic,
    )
    if resolved_source_names == []:
        raise HTTPException(status_code=404, detail="未找到符合筛选条件的资料")

    answer, retrieved_chunks = ask_question(
        request.query,
        source_names=resolved_source_names,
        exclude_ocr=request.exclude_ocr
    )
    source_summary = build_source_summary(retrieved_chunks)

    return {
        "mode": "qa",
        "display_type": "text",
        "query": request.query,
        "answer": answer,
        "source_summary": source_summary,
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

    resolved_source_names = resolve_source_names(
        source_names=request.source_names,
        subject=request.subject,
        grade=request.grade,
        topic=request.topic,
    )
    if resolved_source_names == []:
        raise HTTPException(status_code=404, detail="未找到符合筛选条件的资料")

    answer, retrieved_chunks = explain_for_teaching(
        request.query,
        source_names=resolved_source_names,
        exclude_ocr=request.exclude_ocr,
        teaching_mode=request.teaching_mode,
        explanation_depth=request.explanation_depth,
    )
    source_summary = build_source_summary(retrieved_chunks)

    return {
        "mode": "teaching",
        "display_type": "text",
        "query": request.query,
        "answer": answer,
        "source_summary": source_summary,
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

    resolved_source_names = resolve_source_names(
        source_names=request.source_names,
        subject=request.subject,
        grade=request.grade,
        topic=request.topic,
    )
    if resolved_source_names == []:
        raise HTTPException(status_code=404, detail="未找到符合筛选条件的资料")

    answer, retrieved_chunks = generate_exercise_from_material(
        request.query,
        style=request.style,
        source_names=resolved_source_names,
        exclude_ocr=request.exclude_ocr,
        difficulty=request.difficulty,
        expected_count=request.expected_count,
    )
    source_summary = build_source_summary(retrieved_chunks)

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
        "display_type": "exercise_set",
        "query": request.query,
        "style": request.style,
        "answer": final_answer,
        "source_summary": source_summary,
        "retrieved_chunks": retrieved_chunks
    }
