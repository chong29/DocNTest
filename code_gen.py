import openai
from openai import OpenAI
import os
import requests

from config import settings


def request_ip_address(url):
    """请求指定IP地址并返回响应内容"""
    try:
        response = requests.get(url)
        response.raise_for_status()  # 检查请求是否成功
        return response.json()  # 假设返回的是 JSON 格式的数据
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None


def generate_code_and_structure(prompt):
    """调用OpenAI聊天模型生成代码和结构"""
    client = OpenAI(
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.chat_completion_kwargs.base_url,
        timeout=settings.chat_completion_kwargs.request_timeout,
    )
    model = "gpt-3.5-turbo"
    try:
        messages = [
            {"role": "system",
             "content": "You are a helpful assistant that generates Python project code and structure based on user requirements."},
            {"role": "user", "content": prompt}
        ]
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.2,
            n=1,
        )
        result = response.choices[0].message.content.strip()

        return result
    except Exception as e:
        print(f"Error during API call: {e}")
        return None


def save_code_and_structure(file_path, content):
    """保存生成的代码和结构到文件"""
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"Content saved successfully to {file_path}")
    except Exception as e:
        print(f"Error saving file: {e}")


def sanitize_name(name):
    """清理文件和文件夹名称，去除不必要的字符"""
    return name.replace('/', '_').replace('\\', '_').replace('──', '').strip()


def parse_structure_and_create_files(txt_file_path, base_directory):
    print(f"Reading structure from: {txt_file_path}")

    # 确保主目录存在
    if not os.path.exists(base_directory):
        os.makedirs(base_directory)
        print(f"Created base directory: {base_directory}")

    try:
        with open(txt_file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    current_path = base_directory  # 当前路径为主目录
    folder_stack = [base_directory]  # 用于追踪文件夹层级
    is_within_structure = False  # 用于标记是否处于结构定义区域
    structure_level = 0  # 记录结构层级
    is_within_content = False  # if in file contect area
    is_within_file = False  # if in one sample file
    sample_file_name = ''
    file_mapping = dict()

    for line in lines:
        stripped_line = line.rstrip()

        if not is_within_content:
            # 开始创建文件和文件夹
            if stripped_line.startswith("```") and structure_level == 0:
                is_within_structure = True
                structure_level += 1  # 进入结构定义区域
                continue  # 跳过 "###" 行

            # 停止创建文件和文件夹
            if stripped_line.startswith("```") and structure_level == 1:
                print("Encountered second '###'. Stopping file and folder creation.")
                # break  # 遇到第二个 "###" 时停止
                is_within_content = True
                continue

            # 跳过不在结构定义范围内的行
            if not is_within_structure:
                continue

            level1 = stripped_line.count('│')
            level2 = stripped_line.count('├')
            level3 = stripped_line.count('└')
            indent_level = level1 + level2 + level3  # 根据 │ ├ └ 的数量确定层级
            name = stripped_line.replace('│', '').replace('├', '').replace('└', '').strip()  # 去掉标记和空格

            print(f"Processing line: '{name}' (indent level: {indent_level})")

            # 处理文件夹创建
            if name.endswith('/'):
                folder_name = name[:-1].strip()  # 去掉最后的 /
                folder_name = sanitize_name(folder_name)  # 清理名字
                new_folder_path = os.path.join(folder_stack[indent_level], folder_name)
                os.makedirs(new_folder_path, exist_ok=True)
                print(f"Created folder: {new_folder_path}")

                # 自动创建 __init__.py 文件（除第零层外）
                if indent_level > 0:
                    init_file_path = os.path.join(new_folder_path, '__init__.py')
                    open(init_file_path, 'a').close()  # 创建空的 __init__.py 文件
                    print(f"Created file: {init_file_path}")

                # 更新层级
                if len(folder_stack) > indent_level + 1:
                    folder_stack[indent_level + 1] = new_folder_path
                elif len(folder_stack) == indent_level + 1:
                    folder_stack.append(new_folder_path)
                else:
                    folder_stack[indent_level] = new_folder_path

                current_path = new_folder_path  # 更新当前路径

            # 处理其他 .py 文件创建
            elif name.endswith('.py'):
                file_name = sanitize_name(name)  # 清理文件名
                file_path = os.path.join(current_path, file_name)
                file_mapping[file_name] = file_path
                print(">>> Create mapping " + file_name + " -> " + file_path)
                open(file_path, 'a').close()  # 创建空的 .py 文件
                print(f"Created file: {file_path}")

            # 如果缩进层级减少，则返回到之前的文件夹
            if len(folder_stack) > indent_level:
                current_path = folder_stack[indent_level]
        else:
            if '.py' in line:
                file_name = line.replace('\n', '').strip("/:'`*# ").split('/')[-1]
                print("Try to file mapping for " + file_name)
                sample_file_name = file_mapping.get(file_name)
                if sample_file_name is not None:
                    print("Find sample file " + sample_file_name)
                else:
                    sample_file_name = ''
                continue

            if line.startswith("```python"):
                if sample_file_name != '':
                    is_within_file = True
                    print("Prepare to write file " + sample_file_name)
                continue

            if line.startswith("```"):
                if is_within_file:
                    print("Finish to write file " + sample_file_name)
                    is_within_file = False
                    sample_file_name = ''
                continue

            if is_within_file:
                file = open(sample_file_name, 'a')
                file.write(line + '\n')
                file.close()


# 示例用法
# txt_file = 'structure.txt'  # 包含你提供的结构文本的文件路径
# base_dir = 'wechat_management_system'  # 基本目录
# parse_structure_and_create_files(txt_file, base_dir)

def main():
    print("Welcome to the Project Code Generator!")
    user_input = input("Please describe your project requirements in detail: ").strip()

    prompt = (
        f"Generate a Python project structure and code based on the following requirements:\n\n"
        f"{user_input}\n\n"
        f"Make sure the code is well-organized, uses appropriate libraries, "
        f"and follows best coding practices."
    )

    # 生成项目结构和代码
    result = generate_code_and_structure(prompt)

    if result:
        # 打印生成的内容
        print("\nGenerated Content:\n")
        print(result)

        # 保存内容到 .txt 文件
        txt_file_path = input(
            "\nEnter the file path to save the generated content as a .txt file (e.g., './project_code.txt'): ").strip()
        if txt_file_path:
            save_code_and_structure(txt_file_path, result)

            # 询问用户是否根据 Project Structure 生成文件
            generate_files = input(
                "\nDo you want to generate files based on the Project Structure from the .txt file? (yes/no): ").strip().lower()
            if generate_files == 'yes':
                base_directory = input(
                    "Enter the directory where you want to create the project structure (e.g., './projects/YourProject'): ").strip()
                parse_structure_and_create_files(txt_file_path, base_directory)
    else:
        print("Failed to generate content. Please try again.")


if __name__ == "__main__":
    main()
