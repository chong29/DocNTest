from openai import OpenAI
import pandas as pd
from config import settings


def generate_test_cases(code: str) -> str:
    client = OpenAI(
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.chat_completion_kwargs.base_url,
        timeout=settings.chat_completion_kwargs.request_timeout,
    )
    prompt = f"根据以下代码生成相应的测试用例：\n\n{code}\n\n请以excel表格的格式返回测试用例的代码。"

    # 使用新的 `openai.chat_completions.create` 方法生成测试用例
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        timeout=30  # 设置更长的超时时间
    )

    # 获取生成的测试用例内容
    test_cases = response.choices[0].message.content
    return test_cases


def save_test_cases_to_excel(test_cases: str, file_path: str):
    # 将测试用例分割为行并构建 DataFrame
    lines = test_cases.strip().split('\n')
    df = pd.DataFrame(lines, columns=["测试用例"])

    # 将 DataFrame 保存为 Excel 文件
    df.to_excel(file_path, index=False)
    print("Saved to", file_path)


# 点击确认按钮的回调函数
'''
def on_confirm():
    code = input_text.get("1.0", "end").strip()
    if not code:
        messagebox.showerror("错误", "请输入代码以生成测试用例。")
        return
    try:
        test_cases = generate_test_cases(code)
        output_text.config(state=tk.NORMAL)
        output_text.delete("1.0", "end")
        output_text.insert("end", test_cases)
        output_text.config(state=tk.DISABLED)
        save_test_cases_to_excel(test_cases, "test_cases.xlsx")
        messagebox.showinfo("成功", "测试用例已生成并保存到 test_cases.xlsx")
    except Exception as e:
        messagebox.showerror("错误", f"生成测试用例时出错：{str(e)}")

# 创建主窗口
root = tk.Tk()
root.title("测试用例生成器")
root.geometry("600x400")

# 设置行和列的权重，使控件随窗口大小变化
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(3, weight=1)
root.grid_columnconfigure(0, weight=1)

# 输入标签和输入框
label = tk.Label(root, text="请输入代码：")
label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

input_text = tk.Text(root, height=10)
input_text.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

# 确认按钮
confirm_button = tk.Button(root, text="生成测试用例", command=on_confirm)
confirm_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

# 输出标签和输出框
output_label = tk.Label(root, text="生成的测试用例：")
output_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")

output_text = tk.Text(root, height=10, state=tk.DISABLED)
output_text.grid(row=4, column=0, sticky="nsew", padx=5, pady=5)

# 使输出框的行也随窗口大小调整
root.grid_rowconfigure(4, weight=2)

# 运行主窗口
root.mainloop()
'''
