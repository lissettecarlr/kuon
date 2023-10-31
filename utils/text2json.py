# 该文件用于将1.txt转化为JSON文件
import json

def convert_text_to_json(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    json_data = []
    for i in range(0, len(lines), 2):
        user_content = lines[i].strip()
        assistant_content = lines[i+1].strip()
        json_data.append({
            "role": "user",
            "content": user_content
        })
        json_data.append({
            "role": "assistant",
            "content": assistant_content
        })
    
    return json_data

# 请将文本文件的路径替换为实际的文件路径
file_path = './虚伪的假面字幕/以处理文本.txt'
json_data = convert_text_to_json(file_path)

# 请将保存JSON文件的路径替换为实际的文件路径
output_file_path = './kuon_.json'
with open(output_file_path, 'w', encoding='utf-8') as output_file:
    json.dump(json_data, output_file, indent=4, ensure_ascii=False)
print("转化完成并保存为JSON文件。")
