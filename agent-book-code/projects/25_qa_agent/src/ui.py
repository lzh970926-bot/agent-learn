"""
Streamlit 前端（待实现）
"""
# TODO(作者)：实现流式聊天界面
# import streamlit as st
#
# st.title("工具增强问答 Agent")
# if "messages" not in st.session_state:
#     st.session_state.messages = []
#
# for msg in st.session_state.messages:
#     with st.chat_message(msg["role"]):
#         st.markdown(msg["content"])
#
# if prompt := st.chat_input():
#     st.session_state.messages.append({"role": "user", "content": prompt})
#     with st.chat_message("user"):
#         st.markdown(prompt)
#     with st.chat_message("assistant"):
#         response = agent.invoke({"messages": [...]})
#         st.markdown(response["messages"][-1].content)
