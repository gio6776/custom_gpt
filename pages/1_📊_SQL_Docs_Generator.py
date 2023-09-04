from langchain.chat_models import ChatOpenAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.schema import(
    SystemMessage,
    HumanMessage,
    AIMessage
)
import streamlit as st
from streamlit_chat import message
from langchain import PromptTemplate
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)

st.set_page_config(
    page_title='DE SQL Code Documentation Assistant',
    page_icon='🤖'
)

st.subheader('SQL Code Documentation Assistant 🤖')
st.markdown('##### Simpy Copy and Paste you SQL Code')

chat = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0.5, streaming=True, callbacks=[StreamingStdOutCallbackHandler()])

# setting the behaviour of the system message (role)
system_message = '''You are a professional Developer specialized in writing documentation of SQL code in Google Big Query Syntax. Your answers should have three main headings: 
    \n 1. Model Overview: An one-paragraph written in an objective and concise way describing the model and its usage. It must contain two sentences separated by a dot 
    \n 2. CTEs: A description for each CTE in the SQL Code. Each CTE should be in a different line with the following format (CTE: description)
    \n 3. Fields Description: A description of each field produced by the final SELECT statement. ChatGPT, follow the rules below:'''


prompt_template = PromptTemplate.from_template(
    ''' Write a Documentation for the following SQL Code: 
        \n{sql_code}'''
)  

# creating the messages (chat history) in the Streamlit session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append(
            SystemMessage(content=system_message)
            )

# st.write(st.session_state.messages)

# if the user entered a question, append it to the session state

if prompt := st.chat_input("Paste SQL Code here!"):
    if len(st.session_state.messages) == 1:
        prompt = prompt_template.format(sql_code=prompt)
    else:
        prompt = prompt

    st.session_state.messages.append(
        HumanMessage(content=prompt)
    )
    with st.spinner('Working on your request ...'):
        # creating the ChatGPT response
        response = chat(st.session_state.messages)

    # adding the response's content to the session state
    st.session_state.messages.append(AIMessage(content=response.content))

# st.session_state.messages
# message('this is chatgpt', is_user=False)
# message('this is the user', is_user=True)

# displaying the messages (chat history)
for i, msg in enumerate(st.session_state.messages[1:]):
    if i % 2 == 0:
        with st.chat_message("user"):
            st.markdown(prompt)
    else:
        with st.chat_message("assistant"):
            st.markdown(msg.content)


# run the app: streamlit run front_end_customGPT.py
