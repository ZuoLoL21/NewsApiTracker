import logging

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from pydantic import BaseModel, ValidationError

from libs.sentiment_analysis.base import SentimentAnalyzer, Sentiment

logger = logging.getLogger(__name__)

MODEL = ChatOllama(
    model="llama3.2",
    temperature=0,
)

PROMPT_TEMPLATE = """
You are required to tell me if the article portrays a topic in a good or bad light

Here is the information
Title: {title}
Description: {description}
Initial Words: {content}

You must analyse with respect to the following topic
Topic: {topic}

Please return on of the following sentiment
- positive -> the article is biased for the topic
- negative -> the article is biased against the topic
- neutral -> the article portrays the topic in an neutral way (objective and comprehensive)
- unknown -> irrelevant or not enough information to judge

Only return a single word
"""

class LLMSentimentAnalyzer(SentimentAnalyzer):
    class Input(BaseModel):
        title: str
        description: str
        content: str

    def sentiment_analysis(self, context:dict) -> Sentiment:
        try:
            validated_input = self.Input.model_validate(context)
        except ValidationError as e:
            logger.error(f"{context}\n{e}")
            return Sentiment.INVALID
        return self._sentiment_analysis(self.topic, validated_input)

    def _sentiment_analysis(self, topic: str, context: Input) -> Sentiment:
        prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        args = context.model_dump()
        args['topic'] = topic
        prompt = prompt.invoke(args)

        return_ = MODEL.invoke(prompt).content

        logger.debug(f"{prompt}\n {return_}")

        return Sentiment(return_.lower())


def main():
    llm = LLMSentimentAnalyzer("Cloud Computing")
    answer = llm.sentiment_analysis(
        {
            "title": "Digital Translucency: Privacy is Dying And Authenticity is Your Only Defense",
            "description": "The era of managing an online image is over. We have entered a period of radical, involuntary transparency where the distinction between a private life and a public persona has effectively collapsed. Whether you are an executive steering a corporation or an i…",
            "content": "The era of managing an online image is over. We have entered a period of radical, involuntary transparency where the distinction between a private life and a public persona has effectively collapsed.… [+4167 chars]",
        },
    )
    print(answer)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(levelname)s - %(name)s - %(message)s"
    )

    main()
