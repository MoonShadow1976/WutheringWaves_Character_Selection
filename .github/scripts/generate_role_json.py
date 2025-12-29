import os
import json
from pathlib import Path

def generate_role_json():
    # 读取id2role.json
    id2role_path = Path('src/id2role.json')
    data = []
    
    if id2role_path.exists():
        with open(id2role_path, 'r', encoding='utf-8') as f:
            id2role_data = json.load(f)
            
        for char_id, char_info in id2role_data.items():
            # 构建角色数据
            char_data = {
                "id": char_id,
                "url": f"src/role/role_pile_{char_id}.png"
            }
            
            # 添加多语言名称
            for lang, name in char_info.items():
                if lang == 'zh-Hans':
                    lang = 'zh'
                char_data[lang] = name
                
            data.append(char_data)
    
    result = {
        "status": 200,
        "info": "wuthering waves role data",
        "data": data
    }
    
    with open('src/role.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print("role.json generated successfully from id2role.json!")

if __name__ == "__main__":
    generate_role_json()