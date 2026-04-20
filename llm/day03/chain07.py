from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain.chat_models import init_chat_model

prompt = PromptTemplate.from_template("""请对以下内容进行总结:
{output_text}
总结:
""")

llm = init_chat_model(model="deepseek-chat", base_url="https://api.deepseek.com/v1")

def transform(x):
  text = x["text"]
  return { "output_text": "\n\n".join(text.split("\n\n")[:3]) }

transform_chain = RunnableLambda(transform)

chain =  transform_chain | prompt | llm


text = """
记忆，是昨天留下的余温。有时，它就藏在某处，等待一个被触碰的瞬间。

　　回安徽合肥老家打扫旧厨房时，25岁的解皓明看到一块有年头的石头，一眼就认出来，那就是奶奶生前用来压锅盖的石头。捡起石头那一瞬，他脑海中浮现出奶奶围着灶台做饭的样子，“有点像隔着时间又见了一面”。这段视频发到网上后，引来万千网友共情。

　　一个平平无奇的物件，如此令人动容，是因为它凝固了一起走过的日子，承载着难以割舍的亲情。这样的“压锅石”，或许每个人心中都有一块。爷爷用过的老花镜，姥姥留下的针线包……想起来就心头一热、充满暖意。

　　这些无声的物件、难忘的场景，是时间的容器，将亲人的气息、家庭的温暖、过往的岁月都紧紧包裹在一起，让人迅速找到精神的锚点，意识到自己的来处。
"""

result = chain.invoke({ "text": text })
print(result.content)
