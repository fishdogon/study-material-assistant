# 从 pydantic 导入 BaseModel
# BaseModel 的作用是：定义接口请求体的数据结构
from pydantic import BaseModel


class AskRequest(BaseModel):
    """
    资料问答模式的请求体结构。
    例如：
    {
        "query": "平行线专题的常见易错点是什么？"
    }
    """
    query: str
    source_names: list[str] = []
    subject: str = ""
    grade: str = ""
    topic: str = ""
    exclude_ocr: bool = False


class ExplainRequest(BaseModel):
    """
    教学讲解模式的请求体结构。
    例如：
    {
        "query": "和倍问题应该怎么给三年级学生讲？"
    }
    """
    query: str
    source_names: list[str] = []
    subject: str = ""
    grade: str = ""
    topic: str = ""
    exclude_ocr: bool = False
    teaching_mode: str = ""
    explanation_depth: str = ""


class ExerciseRequest(BaseModel):
    """
    练习题生成模式的请求体结构。

    query: 用户出题需求
    style: 输出风格
        1 = 只出题
        2 = 出题 + 答案
        3 = 出题 + 讲解
    """
    query: str
    style: str = "2"
    source_names: list[str] = []
    subject: str = ""
    grade: str = ""
    topic: str = ""
    exclude_ocr: bool = False
    difficulty: str = ""
    expected_count: int = 0


class MaterialMetadataUpdateRequest(BaseModel):
    subject: str = ""
    grade: str = ""
    topic: str = ""


class MaterialMetadataSuggestionResponse(BaseModel):
    subject: str = ""
    grade: str = ""
    topic: str = ""
