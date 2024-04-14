import os
import time
from dataclasses import dataclass
from datetime import datetime

import streamlit as st
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# 打印环境变量值以进行调试
print("Supabase URL:", os.getenv("supabaseURL"))

@dataclass
class Prompt:
    title: str
    prompt: str
    is_favorite: bool = False
    id: int = None
    created_at: datetime = None
    updated_at: datetime = None

def setup_database():
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
    con.commit()
    return con

def prompt_form(cur):
    prompt = Prompt(title="", prompt="")
    with st.form(key="prompt_form", clear_on_submit=True):
        title = st.text_input("Title", value=prompt.title)
        prompt_content = st.text_area("Prompt", height=200, value=prompt.prompt)
        is_favorite = st.checkbox("Favorite", value=prompt.is_favorite)
        submitted = st.form_submit_button("Submit")
        if submitted:
            if not title or not prompt_content:
                st.error("Title and prompt are required.")
                return None
            else:
                return Prompt(title=title, prompt=prompt_content, is_favorite=is_favorite)

def display_prompts(cur, search_query, sort_order):
    with cur.connection:
        if search_query:
            cur.execute("SELECT * FROM prompts WHERE title ILIKE %s OR prompt ILIKE %s ORDER BY created_at DESC" 
                        if sort_order == "Newest" 
                        else "SELECT * FROM prompts WHERE title ILIKE %s OR prompt ILIKE %s ORDER BY created_at ASC", 
                        (f'%{search_query}%', f'%{search_query}%'))
        else:
            cur.execute("SELECT * FROM prompts ORDER BY created_at DESC" 
                        if sort_order == "Newest" 
                        else "SELECT * FROM prompts ORDER BY created_at ASC")
        prompts = cur.fetchall()
    return prompts

def fetch_favorites(cur):
    cur.execute("SELECT * FROM prompts WHERE is_favorite = TRUE ORDER BY created_at DESC")
    return cur.fetchall()

if __name__ == "__main__":
    st.title("Promptbase 🧠🗝️")
    st.subheader("A simple app to store and retrieve prompts")
    con = setup_database()
    cur = con.cursor()

    search_query = st.text_input("Search prompts", "")
    sort_order = st.selectbox("Sort by", ["Newest", "Oldest"])
    prompts = display_prompts(cur, search_query, sort_order)

    prompt = prompt_form(cur)
    if prompt:
        with cur.connection:
            cur.execute("INSERT INTO prompts (title, prompt, is_favorite) VALUES (%s, %s, %s)", 
                        (prompt.title, prompt.prompt, prompt.is_favorite))
            cur.connection.commit()
            st.success("Prompt added successfully!")
            time.sleep(2)
            st.experimental_rerun()

    for p in prompts:
        with st.expander(f"{p[1]}"):
            st.markdown(
                f"<span style='color: lightgray;'>Created on: {p[4].strftime('%Y-%m-%d %H')}</span>", 
                unsafe_allow_html=True
            )
            st.code(p[2])
            if st.button("Delete", key=p[0]):
                with cur.connection:
                    cur.execute("DELETE FROM prompts WHERE id = %s", (p[0],))
                    cur.connection.commit()
                st.experimental_rerun()

    # Fetching and displaying favorite prompts
    st.subheader("Favorite Prompts")
    favorite_prompts = fetch_favorites(cur)
    for p in favorite_prompts:
        with st.expander(f"{p[1]}"):
            st.markdown(
                f"<span style='color: lightgray;'>Created on: {p[4].strftime('%Y-%m-%d %H')}</span>", 
                unsafe_allow_html=True
            )
            st.write(p[2])


    cur.close()
    con.close()
