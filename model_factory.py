import os
from langchain_openai import ChatOpenAI


class ModelFactory:
    @staticmethod
    def create_model(model_name: str, temperature: float = 1):
        if model_name == 'GPT-3.5':
            return ChatOpenAI(model="gpt-3.5-turbo", temperature=temperature)
        elif model_name == 'GPT-4':
            return ChatOpenAI(model="gpt-4", temperature=temperature)
        elif model_name == 'Custom-Model':
            return ChatOpenAI(model="custom-model", temperature=temperature)
        else:
            raise ValueError(f"Model {model_name} is not supported.")

