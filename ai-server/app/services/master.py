from langchain.chat_models import init_chat_model
from langchain_community.chat_message_histories.redis import RedisChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

from app.config import Settings

SYSTEM_PROMPT = """
你是一位专业、沉稳、有古风气质的命理分析师，名为“鬼谷子”。

角色设定：
你熟悉阴阳五行、周易八卦、紫微斗数、八字命理、姓名学、风水学和八字合婚。
你会用温和、克制、可信的中文表达进行分析，不夸大、不恐吓、不做绝对化断言。
你可以适度使用古风表达，例如“天机不可泄露”“一命二运三风水，四积阴德五读书”，但不要堆砌口头禅。

对话流程：
如果用户没有提供出生信息，你应先询问必要信息，例如出生年月日、出生时间、出生地、性别，以及用户关心的问题。
如果用户已经提供出生信息，你应围绕用户问题给出条理清晰的分析。
如果信息不足，你应明确说明缺少哪些信息，并给出可以先行判断的部分。
不得泄露或复述用户隐私信息，除非是为了确认用户刚刚提供的内容。

输出要求：
只输出面向用户的自然语言纯文本。
不要输出 JSON、Markdown、代码块、列表符号、表格、XML、HTML 或 YAML。
不要给整段回答加引号。
不要输出反斜杠转义内容，例如 \\n、\\t、\\"。
需要分段时，直接使用真实换行。
回答必须使用中文。
""".strip()


class Master:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.chat_model = init_chat_model(
            model="deepseek-chat",
            temperature=0,
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
        )
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT),
                MessagesPlaceholder(variable_name="history"),
                ("user", "{input}"),
            ]
        )
        self.chain = self.prompt | self.chat_model | StrOutputParser()
        self.agent = RunnableWithMessageHistory(
            self.chain,
            get_session_history=self.get_session_history,
            input_messages_key="input",
            history_messages_key="history",
        )

    def get_session_history(self, session_id: str) -> RedisChatMessageHistory:
        return RedisChatMessageHistory(
            session_id=session_id,
            url=self.settings.redis_url,
            key_prefix="ai-server:chat:",
            ttl=self.settings.redis_ttl_seconds,
        )

    def chat(self, query: str, session_id: str) -> str:
        result = self.agent.invoke(
            {"input": query},
            config={"configurable": {"session_id": session_id}},
        )
        return result.strip()
