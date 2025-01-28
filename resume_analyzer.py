from getpass import getpass
import glob

from langchain_community.document_loaders import PyPDFLoader
from langchain.chains.summarize import load_summarize_chain
from langchain_ollama.llms import OllamaLLM
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings


def summarize_resumes(pdf_folder):
    
    summaries = []
    for pdf_file in glob.glob(pdf_folder + "/*.pdf"):
        loader = PyPDFLoader(pdf_file) 
        documents = loader.load()
    
        # Define prompt
        prompt_template = """Write a concise summary of the following resume: Include name, title, years of experience,
        most recent role, past employers, achievements and skills"
         "{text}"
        CONCISE SUMMARY:"""
        prompt = PromptTemplate.from_template(prompt_template)

        # Define LLM chain
        # llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k")
        llm = OllamaLLM(model="gemma2:27b",temperature=0.2)
        llm_chain = LLMChain(llm=llm, prompt=prompt)

        # Define StuffDocumentsChain
        stuff_chain = StuffDocumentsChain(llm_chain=llm_chain, document_variable_name="text")
        summary = stuff_chain.run(documents)
       # print("Summary for: ", pdf_file)
       # print(summary)
       # print("\n")
        summaries.append(summary)
        
    return summaries

def extract_resume(resume):
    resume_loader = PyPDFLoader(resume) 
    desc = resume_loader.load()
    prompt_template = """
        Ты эксперт в области извлечения информации. 
        Извлеки ключевые квалификационные требования из резюме кандидата в формате JSON.
        Ключевыми данными в формате JSON являются: название должности, текущий работодатель, опыт работы, уровень зарплаты, формат работы, обязанности, требования, технические навыки, образование.                     
        "{text}"
        Вывод: """
    prompt = PromptTemplate.from_template(prompt_template)
   
    
    # llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k")
    llm = OllamaLLM(model="gemma2:27b",temperature=0.2)
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    resume_json = llm_chain.invoke(desc)
    print(resume_json)
    return resume_json


def extract_job_req(job_desc):
    job_loader = PyPDFLoader(job_desc) 
    desc = job_loader.load()
    prompt_template = """
        Ты эксперт в области извлечения информации. 
        Извлеки ключевые квалификационные требования из описания вакансии в формате JSON.
        Ключевыми данными в формате JSON являются название должности, опыт работы, уровень зарплаты, формат работы, обязанности, требования, технические навыки, образование.                     
        "{text}"
        Вывод: """
    prompt = PromptTemplate.from_template(prompt_template)
   
    
    # llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k")
    llm = OllamaLLM(model="gemma2:27b",temperature=0.2)
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    job_desc_json = llm_chain.invoke(desc)
    print(job_desc_json)
    return job_desc_json

def match_resumes(pdf_folder, job_desc_json):
    # Define prompt
        prompt_template = """ 
        Ты опытный рекрутер, специализирующийся на анализе вакансий и подборе подходящих резюме. Твоя роль предполагает тщательный процесс оценки резюме в соответствии с конкретными требованиями к работе.

        Тебе предоставляются резюме кандидата: {text}

        Тебе также предоставлено описание вакансии, на которую претендует кандидат: {job_desc_json}

        Ознакомься с описанием вакансии и резюме кандидата. Оцени соответсвие резюме кандидата представленной вакансии по категориям: название должности, опыт работы, уровень зарплаты, формат работы, обязанности, требования, технические навыки, образование.
        Каждая категория оценивается по шкале от 1 до 5, где 1 означает плохое соответствие, а 5 - отличное. Если в какой-либо категории в резюме или вакансии нет данных для оценки, используй значение "нет данных".

        Прежде чем выставлять оценки, подумай об общем профиле кандидата в соответствии с описанием вакансии. Оцени историю работы кандидата на предмет соответствия требованиям к опыту работы, учитывая прошлые должности, отрасли и уровень ответственности.
        Оцени, насколько перечисленные навыки кандидата соответствуют требованиям, предъявляемым к вакансии.
        Составь на один абзац текста обоснование соответсвия резюме кандидата представленной вакансии.

        Суммируй баллы, чтобы получить общее количество баллов, указывающее на соответствие резюме кандидата описанию вакансии.

        Окончательный результат должен быть сгенерирован в формате JSON с указанными ниже полями:
        Если в каком-либо из введенных ключей отсутствует значение, используй значение "нет данных".
                 
         "Наименоваие файла": {file_name}
         "Желаемая должность":
         "Место работы (организация)":
         "Оценка за название должности":
         "Оценка за опыт работы":
         "Оценка за уровень зарплаты":
         "Оценка за формат работы":
         "Оценка за обязанности":
         "Оценка за требования":
         "Оценка за технические навыки":
         "Оценка за образование":
         "Общий балл":
         "Обоснование":
         
         Выведи только JSON с указанными полями. Ничего не выдумывай.
                  """
        prompt = PromptTemplate.from_template(prompt_template)
        responses=[]
        for pdf_file in glob.glob(pdf_folder + "/*.pdf"):
            loader = PyPDFLoader(pdf_file) 
            document = loader.load()
            # resume = extract_resume(pdf_file)
            # print(resume)
            # Define LLM chain
            # llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k")
            llm = OllamaLLM(model="gemma2:27b",temperature=0.2)
            llm_chain = LLMChain(llm=llm, prompt=prompt)
            response = llm_chain.invoke({'text':document, 'job_desc_json':job_desc_json, 'file_name':pdf_file.split('/')[-1]})
            responses.append(response)
        return(responses)

def gen_response(job_posting_name):
    text = extract_job_req('data/'+job_posting_name)
    result = match_resumes('data/resumes', text)
    #print(result)
    return result

