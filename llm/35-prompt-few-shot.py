import os

from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
from langchain_core.example_selectors import (
    LengthBasedExampleSelector,
    MaxMarginalRelevanceExampleSelector,
    SemanticSimilarityExampleSelector,
)
from langchain_community.vectorstores import FAISS, Chroma
from langchain_community.embeddings import FakeEmbeddings
from langchain_openai import OpenAIEmbeddings

examples = [
    {"input": "Happy", "output": "Sad"},
    {"input": "tall", "output": "Short"},
    {"input": "sunny", "output": "gloomy"},
    {"input": "好", "output": "坏"},
]

example_prompt = PromptTemplate(
    input_variables=["input", "output"],
    template="原词：{input}\n反义词：{output}",
)


def build_example_selector():
    """Build selector with graceful fallback when OpenAI quota/key is unavailable."""
    # 1) Prefer OpenAI embeddings when key exists.
    # 2) Fall back to local FakeEmbeddings to keep script runnable offline.
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key:
        try:
            return MaxMarginalRelevanceExampleSelector.from_examples(
                examples,
                OpenAIEmbeddings(
                    model="text-embedding-3-small",
                    # openai_proxy="https://api.deepseek.com/v1"
                ),
                # FAISS,
                Chroma,
                k=2,
            )
        except Exception:
            pass
    print("Fake")
    # Local fallback: no API calls, always works.
    return MaxMarginalRelevanceExampleSelector.from_examples(
        examples,
        FakeEmbeddings(size=256),
        # FAISS,
        Chroma,
        k=2,
    )


example_selector = build_example_selector()

mmr_prompt = FewShotPromptTemplate(
    example_selector=example_selector,
    example_prompt=example_prompt,
    prefix="给出每个输入词的反义词",
    suffix="原词：{adjective}\n反义词：",
    input_variables=["adjective"],
)

adjective = "small big and tall good fresh"
print(mmr_prompt.format(adjective=adjective))
