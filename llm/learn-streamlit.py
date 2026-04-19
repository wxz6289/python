import streamlit as st

st.title("AI 智能伴侣")

st.write("hello world!")

st.image("xh.png", width=200)
st.divider()

data = {
  "姓名": ["King", "zhao"],
  "学号": ["001", "002"],
  "语文": [89, 68],
  "数学": [98, 100]
}

st.table(data)

# st.audio()
# st.video()
# st.logo()
