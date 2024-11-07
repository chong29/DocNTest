import config
from runner import Runner
from config import settings
from runner import clone_repo


class DocumentationGenerator:
    def __init__(self, github_url, local_path):
        self.github_url = github_url
        self.local_path = local_path
        print(f"repo={github_url} local={local_path}")

    def clone_and_generate_docs(self):
        # 克隆GitHub仓库
        clone_repo(self.github_url, self.local_path)

        # 配置项目路径
        settings.repo_path = self.local_path

        runner = Runner()
        runner.generate_hierachy()

        # 生成文档
        runner.first_generate()

