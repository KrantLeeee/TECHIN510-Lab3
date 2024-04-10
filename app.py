import os
from dataclasses import dataclass
from datetime import datetime

import streamlit as st
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# 打印环境变量值以进行调试
print("Supabase URL:", os.getenv("supabaseURL"))

con = psycopg2.connect(os.getenv("supabaseURL"))
cur = con.cursor()

cur.execute(
    """
    CREATE TABLE IF NOT EXISTS prompts (
        id SERIAL PRIMARY KEY,
        title TEXT NOT NULL,
        prompt TEXT NOT NULL,
        is_favorite BOOLEAN NOT NULL DEFAULT FALSE,
        created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )
    """
)


# Design the table here ⬇️
@dataclass
class Prompt:
    title: str
    prompt: str
    is_favorite: bool = False
    id: int = None
    created_at: datetime = None
    updated_at: datetime = None


def prompt_form(prompt=None):
    if prompt is None:
        prompt = Prompt(title="", prompt="")

    with st.form(key="prompt_form", clear_on_submit=True):
        title = st.text_input("Title", value=prompt.title)
        prompt_content = st.text_area("Prompt", height=200, value=prompt.prompt)
        is_favorite = st.checkbox("Favorite", value=prompt.is_favorite)
        submitted = st.form_submit_button("Submit")

        # 在这里检查是否有必填字段为空
        if submitted and (not title or not prompt_content):
            st.error("Title and prompt are required.")
            return None  # 提交操作终止，不返回Prompt实例
        elif submitted:
            # 如果所有必填字段都已填写，则返回一个新的Prompt实例
            return Prompt(title=title, prompt=prompt_content, is_favorite=is_favorite)

st.title("Promptbase")
st.subheader("A simple app to store and retrieve prompts")

# Search Feature
search_query = st.text_input("Search prompts", "")
if search_query:
    # 使用 ILIKE 实现不区分大小写的搜索
    cur.execute("SELECT * FROM prompts WHERE title ILIKE %s OR prompt ILIKE %s", (f'%{search_query}%', f'%{search_query}%'))
else:
    cur.execute("SELECT * FROM prompts")
prompts = cur.fetchall()

# Sort Feature
sort_order = st.selectbox("Sort by", ["Newest", "Oldest"])

if search_query:
    if sort_order == "Newest":
        cur.execute("SELECT * FROM prompts WHERE title ILIKE %s OR prompt ILIKE %s ORDER BY created_at DESC", (f'%{search_query}%', f'%{search_query}%'))
    else:  # Oldest
        cur.execute("SELECT * FROM prompts WHERE title ILIKE %s OR prompt ILIKE %s ORDER BY created_at ASC", (f'%{search_query}%', f'%{search_query}%'))
else:
    if sort_order == "Newest":
        cur.execute("SELECT * FROM prompts ORDER BY created_at DESC")
    else:  # Oldest
        cur.execute("SELECT * FROM prompts ORDER BY created_at ASC")

prompts = cur.fetchall()



prompt = prompt_form()
if prompt:
    cur.execute("INSERT INTO prompts (title, prompt, is_favorite) VALUES (%s, %s, %s)", (prompt.title, prompt.prompt, prompt.is_favorite))
    con.commit()
    st.success("Prompt added successfully!")

cur.execute("SELECT * FROM prompts")
prompts = cur.fetchall()

#保存的prompts长啥样
#prompts = [
#    (1, "title1", "prompt1", True,), -> p[0] -> id, p[1] -> "title1", p[2] -> True
#    (2, "title2", "prompt2", True,),
#    (3, "title3", "prompt3", True,),
#]


# TODO: Add a search bar
# TODO: Add a sort by date
# TODO: Add favorite button
for p in prompts:
    with st.expander(p[1]):
        st.code(p[2]) #方便一键复制
        # TODO: Add a edit function
        if st.button("Delete", key=p[0]): #key必须是unique的，所以给了个id
            cur.execute("DELETE FROM prompts WHERE id = %s", (p[0],))
            con.commit()
            st.rerun()
