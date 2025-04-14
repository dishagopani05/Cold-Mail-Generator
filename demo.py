from model import llm
import chromadb
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.exceptions import OutputParserException
import pandas as pd
import uuid
import chromadb
# response = llm.invoke("who is  pm of india")
# client=chromadb.Client()
# collection = client.create_collection(name="my_collection")

# collection.add(
#     documents=[
#         "this document is about new york",
#         "this document is about delhi"
#     ],
#     ids=["id1","id2"]
# )
# all_docs=collection.get()
# # print(all_docs)

# r=collection.query(
#     query_texts=["query about ice"],
#     n_results=1
# )


loader = WebBaseLoader("https://jobs.best-jobs-online.com/jobs?q=JOB&locphysical=155388&qrn_source=google&qrn_medium=cpc&qrn_campaign=439154329&msclkid=de55b6aa24b51c7e7c15d156f652dfb9&utm_source=bing&utm_medium=cpc&utm_campaign=IN%7CPositionKWs&utm_term=JOB%20vacancies&utm_content=JOB")
page_data=loader.load().pop().page_content
# print(page_data)
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

chain = prompt_extract | llm
res= chain.invoke(input={'page_data': page_data})
# import pdb; pdb.set_trace()
print(type(res.content))

json_parser = JsonOutputParser()
json_res =json_parser.parse(res.content)
print(type(json_res)) 

df=pd.read_csv("my_portfolio.csv")
# print(df)

client = chromadb.PersistentClient('vectorstore')
collection = client.get_or_create_collection(name="portfolio") 

if not collection.count():
    for _, row in df.iterrows():
        collection.add(documents=row["Techstack"],
                       metadatas={"links": row["Links"]},
                       ids=[str(uuid.uuid4())])
links = collection.query(query_texts=["expertise in python"],n_results=2)
# print(links)

job=json_res
role =job[0]["role"]
print(role)

links = collection.query(query_texts=role,n_results=2)
print(links)

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
link_list = [m['links'] for m in links['metadatas'][0]]
chain_email = prompt_email | llm
res_email = chain_email.invoke({
    "job_description": f"Company: {job[0]['company']}, Role: {job[0]['role']}, Location: {job[0]['location']}, Date: {job[0]['date']}",
    "link_list": link_list
})
print(res_email)