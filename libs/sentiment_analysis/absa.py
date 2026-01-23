import logging

import torch
from pydantic import BaseModel, ValidationError
from transformers import pipeline

from libs.sentiment_analysis.base import SentimentAnalyzer, Sentiment

logger = logging.getLogger(__name__)

LABEL_TO_SENTIMENT = {
    "Neutral": Sentiment.NEUTRAL,
    "Positive": Sentiment.POSITIVE,
    "Negative": Sentiment.NEGATIVE,
}
RELEVANCE_THRESHOLD = 0.6

class ABSASentimentAnalyzer(SentimentAnalyzer):
    def __init__(self, topic: str):
        super().__init__(topic)
        self.relevance_model = pipeline(
            "text-classification",
            model="cross-encoder/nli-deberta-v3-base",
        )
        self.model = pipeline(
            "text-classification", model="yangheng/deberta-v3-large-absa-v1.1", use_fast=False
        )

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
        prompt = f"Title: {context.title}\nDescription: {context.description}\nInitial Words: {context.content}"

        relevance = self._is_relevant(prompt, topic)
        if not relevance:
            return Sentiment.UNKNOWN

        result = self.model(
            prompt,
            text_pair=topic,
        )

        logger.debug(f"{context.title}\n {result}")

        return LABEL_TO_SENTIMENT[result[0]["label"]]

    def _is_relevant(self, text: str, topic: str, threshold: float = RELEVANCE_THRESHOLD) -> bool:
        class Output(BaseModel):
            label: str
            score: float
        hypothesis = f"The article discusses {topic}."

        output = self.relevance_model({"text": text, "text_pair": hypothesis})
        output = Output.model_validate(output)

        if output.label == "contradiction":
            return False
        if output.label == "neutral" and output.score >= threshold:
            return False
        return True

def main():
    sa = ABSASentimentAnalyzer("Cloud Computing")
    # answer = sa.sentiment_analysis(
    #     {
    #         "title": "Digital Translucency: Privacy is Dying And Authenticity is Your Only Defense",
    #         "description": "The era of managing an online image is over. We have entered a period of radical, involuntary transparency where the distinction between a private life and a public persona has effectively collapsed. Whether you are an executive steering a corporation or an i…",
    #         "content": "The era of managing an online image is over. We have entered a period of radical, involuntary transparency where the distinction between a private life and a public persona has effectively collapsed.… [+4167 chars]",
    #     },
    # )
    answer = sa.sentiment_analysis(
        {
            "title": "A cow moo-ed yesterday",
            "description": "A cow recently moo-ed in the downtown area of London's farms",
            "content": "A cow recently moo-ed in the downtown area of London's farms, spectators state that they were absolutely flabbergasted",
        },
    )
    print(answer)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(levelname)s - %(name)s - %(message)s"
    )

    main()
