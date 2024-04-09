import os
from dataclasses import dataclass
from datetime import datetime

import streamlit as st
import psycopg2
from dotenv import load_dotenv

load_dotenv()

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
    id: int = None
    title: str
    prompt: str
    is_favorite: bool = False
    created_at: datetime = None
    updated_at: datetime = None # make this datetimt type ()

def prompt_form(prompt=Prompt()):
    """
    Add validation to the form, so that the title and prompt are required.
    """
    with st.form(key="prompt_form", clear_on_submit=True):
        title = st.text_input("Title", value=prompt.title, required=True)
        prompt_content = st.text_area("Prompt", height=200, value=prompt.prompt, required=True)
        is_favorite = st.checkbox("Favorite", value=prompt.is_favorite)
        submitted = st.form_submit_button("Submit")
        if submitted:
            return Prompt(title=title, prompt=prompt_content, is_favorite=is_favorite)


st.title("Promptbase")
st.subheader("A simple app to store and retrieve prompts")

prompt = prompt_form()
if prompt:
    cur.execute("INSERT INTO prompts (title, prompt, is_favorite) VALUES (%s, %s, %s)", (prompt.title, prompt.prompt, prompt.is_favorite))
    con.commit() # 类似 git commit
    st.success("Prompt added successfully!")

cur.execute("SELECT * FROM prompts")
prompts = cur.fetchall()

"""
保存的prompts长啥样
prompts = [
    (1, "title1", "prompt1", True,), -> p[0] -> id, p[1] -> "title1", p[2] -> True
    (2, "title2", "prompt2", True,),
    (3, "title3", "prompt3", True,),
]
"""

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
