from abc import ABC, abstractmethod
from DocumentationGenerator import DocumentationGenerator
import code_gen
from config import settings
from openai import OpenAI
from testcasemaker import generate_test_cases, save_test_cases_to_excel


# 抽象策略接口
class FeatureStrategy(ABC):
    @abstractmethod
    def execute(self, **kwargs):
        pass


# 具体策略类：文档生成
class GenerateDocumentStrategy(FeatureStrategy):
    def execute(self, repo_link: str, target_dir: str, **kwargs):
        doc_gen = DocumentationGenerator(repo_link, target_dir)
        doc_gen.clone_and_generate_docs()


class GenerateProjectCode(FeatureStrategy):
    def execute(self, descriptions: str, generate_txt_path: str, generate_project_path: str, **kwargs):
        prompt = (
            f"Generate a Python project structure and code based on the following requirements:\n\n"
            f"{descriptions}\n\n"
            f"Make sure the code is well-organized, uses appropriate libraries, "
            f"and follows best coding practices."
        )
        print(prompt)
        result = code_gen.generate_code_and_structure(prompt)
        if result:
            # 打印生成的内容
            print("\nGenerated Content:\n")
            print(result)

            # 保存内容到 .txt 文件
            if generate_txt_path:
                code_gen.save_code_and_structure(generate_txt_path, result)
                code_gen.parse_structure_and_create_files(generate_txt_path, generate_project_path)
        else:
            print("Failed to generate content. Please try again.")


class GenerateTestCase(FeatureStrategy):
    def execute(self, code: str, save_file_path: str, **kwargs):
        test_cases = generate_test_cases(code)
        save_test_cases_to_excel(test_cases, save_file_path)
        print("测试用例已生成")


class FeatureContext:
    def __init__(self, strategy: FeatureStrategy):
        self.strategy = strategy

    def execute_feature(self, **kwargs):
        self.strategy.execute(**kwargs)
