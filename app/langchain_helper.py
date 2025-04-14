import chromadb
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.exceptions import OutputParserException
import pandas as pd
import uuid
import chromadb
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()
class Chain:
    def __init__(self):
        self.llm = ChatGroq(temperature=0, groq_api_key=os.getenv("GROQ_API_KEY"), model_name="llama3-70b-8192")
        
    def extract_jobs(self,cleaned_text):
        prompt_extract = PromptTemplate.from_template(
                """
                ### SCRAPED TEXT FROM WEBSITE:
                {page_data}
                ### INSTRUCTION:
                The scraped text is from the career's page of a website.
                Your job is to extract the job postings and return them in JSON format containing the 
                following keys: `company`, `role`, `location` and `date`.skills is the require parameter.Do not write by yourself .retrive from the official link.                Only return the valid JSON.
                ### VALID JSON (NO PREAMBLE):    
                """
        )
        
        
        chain = prompt_extract | self.llm
        res= chain.invoke(input={'page_data': cleaned_text})
        try:
            json_parser = JsonOutputParser()
            res = json_parser.parse(res.content)
        except OutputParserException:
            raise OutputParserException("Context too big. Unable to parse jobs.")
        return res if isinstance(res, list) else [res]
    
    def write_email(self,job,links):
        prompt_email = PromptTemplate.from_template(
            """
            ### JOB DESCRIPTION:
            {job_description}
            
            ### INSTRUCTION:
            You are Mohan, a business development executive at AtliQ. AtliQ is an AI & Software Consulting company dedicated to facilitating
            the seamless integration of business processes through automated tools. 
            Over our experience, we have empowered numerous enterprises with tailored solutions, fostering scalability, 
            process optimization, cost reduction, and heightened overall efficiency. 
            Your job is to write a cold email to the client regarding the job mentioned above describing the capability of AtliQ 
            in fulfilling their needs.
            Also add the most relevant ones from the following links to showcase Atliq's portfolio: {link_list}
            Remember you are Mohan, BDE at AtliQ. 
            Do not provide a preamble.
            ### EMAIL (NO PREAMBLE):
            
            """
        )
        if links and isinstance(links, list):
            link_list = [m['links'] for m in links[0] if 'links' in m]
        else:
            link_list = []

        chain_email = prompt_email | self.llm
        res_email = chain_email.invoke({
            "job_description": f"Company: {job[0]['company']}, Role: {job[0]['role']}, Location: {job[0]['location']}, Date: {job[0]['date']}",
            "link_list": link_list
        })       
        return res_email.content
    
