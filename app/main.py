import streamlit as st
from langchain_community.document_loaders import WebBaseLoader

from langchain_helper import Chain
from portfolio import Portfolio
from utils import clean_text



def create_streamlit_app(llm, portfolio, clean_text):
    st.title("📧 Cold Mail Generator")
    url_input = st.text_input("Enter a URL:", value="https://jobs.nike.com/job/R-33460")
    submit_button = st.button("Submit")

    if submit_button:
        try:
            loader = WebBaseLoader([url_input])
            data = clean_text(loader.load().pop().page_content)
            portfolio.load_portfolio()
            jobs = llm.extract_jobs(data)
            if jobs:
                first_job = jobs[0]
                role = first_job.get("role", "")
                links = portfolio.query_links(role)
                email = llm.write_email([first_job], links)
                st.code(email, language='markdown')
            else:
                st.warning("No jobs were extracted from the page.")
        except Exception as e:
            st.error(f"An Error Occurred: {e}")


if __name__ == "__main__":
    chain = Chain()
    portfolio = Portfolio()
    st.set_page_config(layout="wide", page_title="Cold Email Generator", page_icon="📧")
    create_streamlit_app(chain, portfolio, clean_text)