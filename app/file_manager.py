# 导入 Path，用来处理文件路径
from pathlib import Path

# 导入 UploadFile，这是 FastAPI 里处理上传文件的类型
from fastapi import UploadFile


def save_upload_file(file: UploadFile, save_dir: str = "data/raw") -> str:
    """
    保存上传的文件到指定目录。

    参数:
        file: FastAPI 接收到的上传文件对象
        save_dir: 文件保存目录，默认是 data/raw

    返回:
        保存后的文件路径（字符串）
    """

    # 把保存目录转成 Path 对象
    save_path = Path(save_dir)

    # 如果目录不存在，就自动创建
    save_path.mkdir(parents=True, exist_ok=True)

    # 拼出最终文件路径
    target_file = save_path / file.filename

    # 读取上传文件内容并写入本地
    with open(target_file, "wb") as f:
        f.write(file.file.read())

    # 返回文件路径字符串
    return str(target_file)