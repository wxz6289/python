import streamlit as st

st.title("AI 智能伴侣")

st.write("hello world!")

st.image("resources/xh.png", width=200)
st.divider()

data = {
  "姓名": ["King", "zhao"],
  "学号": ["001", "002"],
  "语文": [89, 68],
  "数学": [98, 100]
}

st.table(data)

st.audio("resources/飞雪玉花.mp3")
st.video("https://www.w3schools.com/html/mov_bbb.mp4")
st.logo("resources/喜庆新春.png")

name = st.text_input("请输入你的名字")
st.write(f"你好，{name}!")
st.text_area("请输入你的地址")
st.number_input("请输入你的年龄")
st.date_input("请输入你的生日")
st.time_input("请输入你的时间")
st.selectbox("请选择你的性别", ["男", "女"], index=0)
st.multiselect("请选择你的爱好", ["篮球", "足球", "乒乓球"])
st.checkbox("请选择你的爱好", ["篮球", "足球", "乒乓球"])
st.radio("请选择你的爱好", ["篮球", "足球", "乒乓球"])
st.file_uploader("请上传你的文件")
st.color_picker("请选择你的颜色")

st.set_page_config(page_title="AI 智能伴侣",
                   page_icon="resources/喜庆新春.png",
                   layout="wide",
                   initial_sidebar_state="expanded",
                   menu_items={
                    "Get Help": "https://www.baidu.com",
                    "Report a bug": "https://www.baidu.com",
                    "About": "https://www.baidu.com",
                   })
