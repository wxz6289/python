from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel

full_prompt = PromptTemplate.from_template(
"""
{character}
{behavior}
{prohibit}
""".strip()
)

character_prompt = PromptTemplate.from_template("你是{name}，你具有{skill}技能。")
behavior_prompt = PromptTemplate.from_template(
"""
你遵从以下行为:
{behavior_list}
""".strip()
)
prohibit_prompt = PromptTemplate.from_template(
"""
你不允许有以下行为:
{prohibit_list}
""".strip()
)

# LCEL modern composition: run sub-prompts in parallel, then merge into full prompt.
chain = (
    RunnableParallel(
        character=character_prompt,
        behavior=behavior_prompt,
        prohibit=prohibit_prompt,
    )
    | full_prompt
)

if __name__ == "__main__":
    result = chain.invoke(
        {
            "name": "AI 助手",
            "skill": "Python",
            "behavior_list": "1. 输出清晰步骤\n2. 给出可运行示例",
            "prohibit_list": "1. 编造不存在的 API\n2. 输出危险破坏命令",
        }
    )
    print(result)
