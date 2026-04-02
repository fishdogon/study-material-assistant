# 导入三种模式的入口函数
from app.pipeline import init_pipeline, ask_question, explain_for_teaching, generate_exercise_from_material


def main():
    """
    综合项目升级版入口：
    1. 初始化资料库
    2. 让用户选择模式
    3. 根据模式执行不同能力
    """

    print("=== 学习资料智能助手 ===")
    print("正在初始化资料库（txt + pdf），请稍候...\n")

    # 初始化资料库
    chunks = init_pipeline()

    print(f"初始化完成，共生成 {len(chunks)} 个文本块。\n")

    # 统计不同来源文件对应的 chunk 数量
    source_count = {}

    for chunk in chunks:
        source = chunk["source"]
        source_count[source] = source_count.get(source, 0) + 1

    print("当前资料来源统计：")
    for source, count in source_count.items():
        print(f"- {source}: {count} 个文本块")
    print()

    # 进入循环模式
    while True:
        print("请选择模式：")
        print("1. 资料问答模式")
        print("2. 教学讲解模式")
        print("3. 练习题生成模式")
        print("输入 exit 退出\n")

        mode = input("请输入模式编号：").strip()

        # 用户输入 exit，直接退出
        if mode.lower() == "exit":
            print("已退出。")
            break

        # 如果模式编号不合法，重新选择
        if mode not in {"1", "2", "3"}:
            print("无效输入，请重新选择。\n")
            continue

        # 先给 exercise_style 一个默认值
        # 普通模式不会用到它，只有模式 3 会真正赋值
        exercise_style = None


        # =========================
        # 模式 1：资料问答模式
        # =========================
        if mode == "1":
            query = input("请输入你的问题：").strip()

            if query.lower() == "exit":
                print("已退出。")
                break

            if not query:
                print("输入不能为空。\n")
                continue

            answer, retrieved_chunks = ask_question(query)
            mode_name = "资料问答模式"

        # =========================
        # 模式 2：教学讲解模式
        # =========================
        elif mode == "2":
            query = input("请输入你的问题：").strip()

            if query.lower() == "exit":
                print("已退出。")
                break

            if not query:
                print("输入不能为空。\n")
                continue

            answer, retrieved_chunks = explain_for_teaching(query)
            mode_name = "教学讲解模式"

        # =========================
        # 模式 3：练习题生成模式
        # =========================
        else:
            # 先选风格，再输入问题
            print("\n请选择练习题输出风格：")
            print("1. 只出题")
            print("2. 出题 + 答案")
            print("3. 出题 + 讲解")
            print("输入 exit 退出\n")

            exercise_style = input("请输入风格编号：").strip()

            if exercise_style.lower() == "exit":
                print("已退出。")
                break

            if exercise_style not in {"1", "2", "3"}:
                print("无效输入，默认使用“出题 + 答案”。\n")
                exercise_style = "2"

            # 风格选完后，再输入用户需求
            query = input("请输入你的出题需求：").strip()

            if query.lower() == "exit":
                print("已退出。")
                break

            if not query:
                print("输入不能为空。\n")
                continue

            answer, retrieved_chunks = generate_exercise_from_material(query)
            mode_name = "练习题生成模式"

        # =========================
        # 统一打印检索结果
        # =========================
        print(f"\n当前模式：{mode_name}")
        print("\n检索到的资料片段：")
        for idx, chunk in enumerate(retrieved_chunks, start=1):
            print(f"{idx}. 来源：{chunk['source']}")
            print(f"   内容：{chunk['content']}")
            print(f"   距离：{chunk['distance']}")
            print()

        print("最终回答：")

        # =========================
        # 模式 3：结构化打印练习题
        # =========================
        if mode == "3":
            print(f"主题：{answer['topic']}")
            print(f"适合年级：{answer['grade']}\n")

            for idx, item in enumerate(answer["exercises"], start=1):
                print(f"题目 {idx}：{item['title']}")
                print(f"题目内容：{item['problem']}")
                print(f"出题意图：{item['intent']}")
                print(f"提示：{item['hint']}")

                # 风格 1：只出题
                if exercise_style == "1":
                    pass

                # 风格 2：出题 + 答案
                elif exercise_style == "2":
                    print(f"参考答案：{item['answer']}")

                # 风格 3：出题 + 讲解
                elif exercise_style == "3":
                    print(f"参考答案：{item['answer']}")
                    print(f"讲解思路：{item['explanation']}")

                print("\n" + "-" * 40 + "\n")

        # =========================
        # 模式 1 / 2：直接打印字符串答案
        # =========================
        else:
            print(answer)

        print("\n" + "=" * 50 + "\n")


if __name__ == "__main__":
    main()