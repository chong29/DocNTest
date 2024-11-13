from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from model_factory import ModelFactory


class AppBuilder:
    _instance = None

    @classmethod
    def get_instance(cls, model):
        if cls._instance is None:
            cls._instance = cls(model)
        return cls._instance

    def __init__(self, model_name):
        if not hasattr(self, "initialized"):
            self.model = ModelFactory.create_model(model_name=model_name)
            self.workflow = StateGraph(state_schema=MessagesState)
            self.memory = MemorySaver()
            self.initialized = True
            self.app = None  # 用于存储编译后的应用

    def call_model(self, state: MessagesState):
        """
        调用模型，根据对话状态生成响应
        :param state: MessagesState对象，包含当前对话信息
        :return: 包含模型响应的字典
        """
        system_prompt = (
            "You are a helpful assistant. "
            "Answer all questions to the best of your ability."
        )
        messages = [SystemMessage(content=system_prompt)] + state["messages"]
        response = self.model.invoke(messages)
        return {"messages": response}

    def add_model_node(self, node_name="model"):
        """
        添加模型节点到工作流中
        :param node_name: 节点名称，默认设置为 'model'
        """
        if node_name not in self.workflow.nodes:
            self.workflow.add_node(node_name, self.call_model)
            self.workflow.add_edge(START, node_name)
        else:
            print(f"Node `{node_name}` already exists. Skipping addition.")

    def build(self):
        """
        构建并返回工作流应用
        :return: 已编译的工作流应用
        """
        self.app = self.workflow.compile(checkpointer=self.memory)
        return self.app

    def invoke(self, messages, config=None):
        """
        外部调用接口，用于传入消息并获取模型响应。
        :param messages: dict类型，包含消息的内容。
        :param config: dict类型，可选的配置参数。
        :return: 应用返回的响应结果。
        """
        if self.app is None:
            raise ValueError("App is not built. Call 'build()' method before invoking.")

        # 使用编译好的应用来调用传入的消息和配置
        return self.app.invoke({"messages": messages}, config=config)





