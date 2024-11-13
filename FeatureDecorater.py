from abc import ABC, abstractmethod


class FeaturePrompt:
    def __init__(self, content):
        self.content = content

    def execute(self):
        return self.content  # 主逻辑：直接返回内容


class FeatureDecorator(ABC):
    def __init__(self, wrapped):
        self._wrapped = wrapped

    @abstractmethod
    def execute(self):
        pass


class GenerateCommentDecorator(FeatureDecorator):
    def execute(self):
        return "为以下代码增加注释：\n" + self._wrapped.execute()


class OptimizeCodeDecorator(FeatureDecorator):
    def execute(self):
        return "优化以下代码：\n" + self._wrapped.execute()


class CompleteCodeDecorator(FeatureDecorator):
    def execute(self):
        return "补全以下代码：\n" + self._wrapped.execute()


class TranslateCodeDecorator(FeatureDecorator):
    def __init__(self, wrapped, target_language):
        super().__init__(wrapped)
        self.target_language = target_language

    def execute(self):
        return f"将以下代码转换为{self.target_language}：\n" + self._wrapped.execute()
