## to run, type in command line: $ streamlit run main.py
import os
import resume_analyzer as ra
import streamlit as st
import json
from pathlib import Path
from streamlit import session_state as ss
from streamlit_pdf_viewer import pdf_viewer

def delete_files_in_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f'Ошибка при удалении файла {file_path}. {e}')

delete_files_in_folder('data/')
delete_files_in_folder('data/resumes/')

st.set_page_config(layout="wide")
# with st.columns(3)[1]:
#      st.image("orig.jpeg", caption="DUC Technologies 2025", width=200)
st.markdown("<img src='https://i.postimg.cc/TPRkqqnY/orig.jpg' width='200' style='display: block; margin: 0 auto;'>" , unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center;'>Автоподбор кандидатов</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'> Это приложение проанализирует отправленные резюме в соответствии с вашим объявлением о приеме на работу и порекомендует лучших кандидатов на открытую вакансию.", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

# def gen_response():
#     text = extract_job_req(job_posting)
#     result = match_resumes('data/resumes', text)
#     return result    
        #how do we place these files locally in the pdf folder?

#JOB POSTING SUBMISSION
with col1:
    st.markdown("Пожалуйста, загрузите описание вакансии.")
    job_posting = st.file_uploader("Загрузить описание вакансии", accept_multiple_files=False, type=('pdf'), key='pdf')
    if job_posting:
    #     st.markdown("Загруженный файл")
    #display info for file uploaded
        # bytes_data = job_posting.read()
        st.write("Загруженный файл:", job_posting.name)
        with st.expander("Нажмите для получения дополнительной информации"): 
            # st.write(bytes_data)
            if ss.pdf:
                ss.pdf_ref = ss.pdf  # backup
            if ss.pdf_ref:
                binary_data = ss.pdf_ref.getvalue()
                pdf_viewer(input=binary_data, width=700)


    #save file locally
        save_folder = './data'
        save_path = Path(save_folder,job_posting.name)
        with open(save_path, "wb") as f:
            f.write(job_posting.getbuffer())
        if save_path:
            st.success(f'Файл {job_posting.name} успешно сохранен!')
 
#RESUME SUBMISSION"
with col2:
    st.markdown("Пожалуйста, загрузите файлы резюме кандидатов для автоподбора.")

    resume_uploaded_files = st.file_uploader("Загрузить файл(ы) резюме", accept_multiple_files=True, type=('pdf'), key='pdf_resume')
    # if resume_uploaded_files:
    #     st.markdown("Загруженный файл")

    #display info for file uploaded
    for idx,uploaded_file in enumerate(resume_uploaded_files):
        # bytes_data = uploaded_file.read()
        st.write("Загруженный файл:", uploaded_file.name)
        with st.expander("Нажмите для получения дополнительной информации"): 
            # st.write(bytes_data)
            if ss.pdf_resume:
                ss.pdf_ref = ss.pdf_resume[idx]  # backup
            if ss.pdf_ref:
                binary_data = ss.pdf_ref.getvalue()
                pdf_viewer(input=binary_data, width=700)
            

    #save file locally
        save_folder = './data/resumes'
        save_path = Path(save_folder,uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        if save_path:
            st.success(f'Файл {uploaded_file.name} успешно сохранен!')
        
        #how do we place these files locally in the pdf folder?


#OUTPUT and recommendations
with col3:
    if st.button("Подобрать кандидатов", use_container_width=True):
        analysis_result = ra.gen_response(job_posting.name)
        new_result = []

        for i in analysis_result:
            s = i['text'].replace("`",'"')
            index_start = s.find('"""json')
            index_end = s.rfind('"""')
            if index_start != -1 and index_end != -1:
                s = s[index_start+7:index_end]
            new_result.append(s)
            print(s, "-----------")
        result = [json.loads(idx.replace("'",'"')) for idx in new_result]
        print(f"\n\n\n Выбранные кандидаты: \n {result}")

        sorted_result = sorted(result, key=lambda x:x['Общий балл'], reverse=True)
        for i in sorted_result:
            st.write(i)
    # if st.button('Clear uploaded file'):
    #     del st.session_state['uploaded_file']
# #