from langchain_ollama import ChatOllama

MODEL = ChatOllama(
    model="llama3.2",
    temperature=0,
)


def sentiment_analysis(query):
    pass