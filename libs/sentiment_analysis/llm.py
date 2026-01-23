from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from pydantic import BaseModel

from libs.sentiment_analysis.base import SentimentAnalyzer, Sentiment

MODEL = ChatOllama(
    model="llama3.2",
    temperature=0,
)

PROMPT_TEMPLATE = """
You are required to tell me if the article portrays a topic in a good or bad light

Here is the information
Title: {title}
Description: {description}
Summary: {content}

You must analyse with respect to the following topic
Topic: {topic}

Please return on of the following sentiment
- positive
- negative
- neutral
- unknown

Only return a single word
"""


class LLMInput(BaseModel):
    title: str
    description: str
    content: str

class LLMSentimentAnalyzer(SentimentAnalyzer):


    def sentiment_analysis(self, topic: str, context: LLMInput) -> Sentiment:
        prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        args = context.model_dump()
        args['topic'] = topic
        prompt = prompt.invoke(args)

        return_ = MODEL.invoke(prompt).content

        return Sentiment(return_.lower())


def main():
    llm = LLMSentimentAnalyzer()
    answer = llm.sentiment_analysis(
        "Cloud Computing",
        LLMInput(
            title="Digital Translucency: Privacy is Dying And Authenticity is Your Only Defense",
            description="The era of managing an online image is over. We have entered a period of radical, involuntary transparency where the distinction between a private life and a public persona has effectively collapsed. Whether you are an executive steering a corporation or an i…",
            content="The era of managing an online image is over. We have entered a period of radical, involuntary transparency where the distinction between a private life and a public persona has effectively collapsed.… [+4167 chars]",
        ),
    )
    print(answer)

if __name__ == "__main__":
    main()
