import sys
import streamlit as st
import os
from langchain_openai import OpenAI
from openai import OpenAI
import openai
import config
from AppBuilder import AppBuilder
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from streamlit_float import *
from strategies import GenerateDocumentStrategy, FeatureContext, GenerateProjectCode, GenerateTestCase
from config import settings
from FeatureDecorater import *


def apply_prompt_decorator(content, action):
    context = FeaturePrompt(content)
    if action == "Generate Comment":
        decorated = GenerateCommentDecorator(context)
    elif action == "Optimize Code":
        decorated = OptimizeCodeDecorator(context)
    elif action == "Complete Code":
        decorated = CompleteCodeDecorator(context)
    elif action == "Translate Code":
        decorated = TranslateCodeDecorator(context, st.session_state.target_language)
    else:
        raise ValueError(f"Unsupported action: {action}")

    return decorated.execute()


def select_action(action):
    if st.session_state.selected_action == action:
        st.session_state.selected_action = ""
        print("------------已清空---------------")
    else:
        st.session_state.selected_action = action
        if action == "Translate Code":
            st.session_state.show_language_select = True


def check_openai_api_key(apikey):
    client_test = OpenAI(api_key=apikey)
    try:
        client_test.models.list()
    except openai.AuthenticationError:
        return False
    else:
        return True


# -----------------前端--------------------------------------
st.subheader('DOCNTEST')

st.markdown("""
        <style>
               .block-container {
                    padding-top: 3rem;
                    padding-bottom: 1rem;
                    padding-left: 0rem;
                    padding-right: 0rem;
                }
        </style>
        """, unsafe_allow_html=True)

#  定义侧边栏。在此部分内的所有控件都会被添加到侧边栏。
with st.sidebar:
    api_key = st.text_input('OpenAI API Key:', type='password', placeholder="sk-...")
    #  创建一个文本输入控件，用于输入OpenAI API密钥。输入的内容将被隐藏。

    model_options = ['GPT-3.5', 'GPT-4', 'Custom-Model']
    selected_model = st.selectbox("选择大语言模型", model_options)  # 使用工厂模式
    #  创建一个下拉选择框，让用户选择本地大语言模型（LLM）。

    # 功能选择框
    feature_option = st.selectbox("选择功能", ["无", "生成文档（仅限python项目/文件）", "生成项目级代码", "生成测试用例"])

    # 根据选择初始化策略
    if feature_option == "生成文档（仅限python项目/文件）":
        strategy = GenerateDocumentStrategy()
        repo_link = st.text_input("GitHub 仓库链接")
        target_dir = st.text_input("生成目标目录")
        # 检查必要参数是否存在
        required_params = {"repo_link": repo_link, "target_dir": target_dir}
        run_strategy = st.button("运行")
    elif feature_option == "生成项目级代码":
        strategy = GenerateProjectCode()
        description = st.text_input("项目细节")
        generate_path = st.text_input("本地txt文件路径", placeholder="C:/.../structure.txt").strip()
        generate_project_path = st.text_input("项目文件夹路径", placeholder="C:/.../projects/ProjectName").strip()
        required_params = {"descriptions": description, "generate_txt_path": generate_path,
                           "generate_project_path": generate_project_path}
        run_strategy = st.button("运行")
    elif feature_option == "生成测试用例":
        strategy = GenerateTestCase()
        code = None
        code_file = st.file_uploader("上传文件", type=["py", "js", "java", "cpp", "c", "rb"],
                                     accept_multiple_files=False)
        save_file_path = st.text_input("本地EXCEL文件路径", placeholder="C:/.../urfilename.xlsx")
        if code_file is not None:
            code = code_file.read().decode("utf-8")
            print(code)
        required_params = {"code": code, "save_file_path": save_file_path}
        run_strategy = st.button("运行")
    else:
        strategy = None  # 或者添加更多的策略
        required_params = {}
        run_strategy = False

    # 创建策略上下文
if strategy:
    feature_context = FeatureContext(strategy)
    # 执行策略功能
    if run_strategy and all(required_params.values()):
        feature_context.execute_feature(**required_params)
        st.sidebar.warning(body='运行完成', icon="✅")
    elif run_strategy:
        st.sidebar.warning("请填写所有必需的参数！")

if api_key:
    if check_openai_api_key(api_key):
        os.environ['OPENAI_API_KEY'] = api_key
        #  如果输入了API密钥，则将其设置为环境变量，以供后续使用。
        settings.OPENAI_API_KEY = api_key
        print(settings.OPENAI_API_KEY)
        print("OpenAI API Key set successfully.")

        app = AppBuilder.get_instance(selected_model)
        app.add_model_node()
        app.build()

        print(f"Selected LLM: {app.model}")
    else:
        st.warning(body='API KEY不可用', icon="⚠️")
else:
    st.warning(body='API KEY未设置', icon="👈")

chathistory = st.container(height=400)
inputbox = st.container(border=True)

# 初始化history
if "messages" not in st.session_state:
    st.session_state.messages = []
#  如果会话状态中没有消息记录，则初始化一个空列表。
if "selected_action" not in st.session_state:
    st.session_state.selected_action = None  # 存储当前选择的功能
if "show_language_select" not in st.session_state:
    st.session_state.show_language_select = False  # 控制语言选择框的显示
if "target_language" not in st.session_state:
    st.session_state.target_language = None  # 存储选择的语言

with chathistory:
    # 展示对话
    for msg in st.session_state.messages:
        with st.chat_message(msg['role']):
            st.markdown(msg["content"])
    #  遍历会话状态中的所有消息，并在应用中显示它们。

with inputbox:
    buttonbox = st.container()
    inputcontainer = st.container()
    # React to user input
    with buttonbox:
        b1, b2, b3, b4 = st.columns(4, gap="small")
        with b1:
            if st.session_state.selected_action == "Generate Comment":
                st.button("✅ 添加注释", key="add_comment", on_click=select_action, args=("Generate Comment",),
                          help="当前选中：添加注释")
                print(f"选中注释")

            else:
                st.button("添加注释", key="add_comment", on_click=select_action, args=("Generate Comment",))

        with b2:
            if st.session_state.selected_action == "Optimize Code":
                st.button("✅ 优化代码", key="optimize_code", on_click=select_action, args=("Optimize Code",),
                          help="当前选中：优化代码")
                print(f"选中优化")

            else:
                st.button("优化代码", key="optimize_code", on_click=select_action, args=("Optimize Code",))

        with b3:
            if st.session_state.selected_action == "Complete Code":
                st.button("✅ 补全代码", key="complete_code", on_click=select_action, args=("Complete Code",),
                          help="当前选中：补全代码")
                print(f"选中补全")

            else:
                st.button("补全代码", key="complete_code", on_click=select_action, args=("Complete Code",))

        with b4:
            if st.session_state.selected_action == "Translate Code":
                st.button("✅ 翻译代码", key="translate_code", on_click=select_action, args=("Translate Code",),
                          help="当前选中：翻译代码")
                print(f"选中翻译")

            else:
                st.button("翻译代码", key="translate_code", on_click=select_action, args=("Translate Code",))
                st.session_state.show_language_select = False

        if st.session_state.show_language_select:
            st.session_state.target_language = st.selectbox("选择目标语言",
                                                            ["Python", "JavaScript", "Java", "C++", "Ruby"])
            if st.button("确认"):
                st.session_state.show_language_select = False  # 关闭选择框

with inputcontainer:
    prompt = st.chat_input("Say something")
    upload_files = []
    upload_files = st.file_uploader("上传文件", type=["py", "js", "java", "cpp", "c", "rb"], accept_multiple_files=True)

# -------------发送消息--------------------------------------
if prompt is not None:

    def add_filename(uploaded_files):
        all_filename = ""
        for upload_file in uploaded_files:
            filename = upload_file.name
            all_filename = all_filename + "\n" + upload_file.name
        return all_filename


    def add_file_content(uploaded_files):
        all_content = ""
        for upload_file in uploaded_files:
            file_content = upload_file.read().decode("utf-8")
            all_content = all_content + "filename:" + upload_file.name + file_content
        return all_content


    if st.session_state.selected_action is not "":
        print(st.session_state.selected_action)
        prompt = apply_prompt_decorator(prompt, st.session_state.selected_action)

    prompt = prompt + add_filename(upload_files)
    print(f"User prompt: {prompt}")
    # Display user message in chat message container
    with chathistory:
        with st.chat_message("user"):
            st.markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        #  如果用户在聊天输入框中输入了消息，则显示用户消息并将其添加到消息记录中。

    # 普通方式输出
    if upload_files is not None:
        prompt = prompt + add_file_content(upload_files)
    generated_res = ""
    generated_res = app.invoke(
        messages=[HumanMessage(content=prompt)],
        config={"configurable": {"thread_id": "20"}}
    )

    output = next((msg.content for msg in reversed(generated_res['messages']) if isinstance(msg, AIMessage)), None)
    print("Using GPT model for response...")
    print(f"Generated response: {output}")

    with chathistory:
        with st.chat_message("assistant"):
            st.markdown(output)
        st.session_state.messages.append({"role": "assistant", "content": output})
