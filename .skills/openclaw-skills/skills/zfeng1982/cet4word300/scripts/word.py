import json
import random
import sys

def get_random_words(count=0):
    # 1. 读取文件并加载所有单词行
    try:
        with open("word.txt", "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return json.dumps([{"error": "未找到 word.txt 文件"}], ensure_ascii=False, indent=2)

    # 2. 处理入参范围：0=全部，1-10，超过10按10
    if count <= 0:
        sample_count = len(lines)
    else:
        sample_count = min(count, 10)

    # 3. 随机抽取
    selected = random.sample(lines, sample_count)

    # 4. 按 # 分割成 5 个字段
    result = []
    for line in selected:
        parts = line.split("#")
        if len(parts) >= 5:
            item = {
                "word": parts[0],
                "phonetic": parts[1],
                "meaning": parts[2],
                "sentence_en": parts[3],
                "sentence_cn": parts[4]
            }
            result.append(item)

    # 5. 返回格式化 JSON
    return json.dumps(result, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    try:
        if len(sys.argv) < 2:
            print("Usage: python word.py <param>")
            sys.exit(1)
        query = sys.argv[1]
        if  not query.isdigit:
            print("Usage: python word.py <param>")
            sys.exit(1)

        output = get_random_words(int(query))

        print(output)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

