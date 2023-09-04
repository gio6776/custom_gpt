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

# setting the behaviour of the system message (role)
sys_message_general_dev = '''When assisting me in creating SQL queries, you should provide answers using Google Big Query  SQL Syntax.
When assisting me in crafting and correcting any pieces of text ensure to not use too many filer words and keep the language simple and straight to the point. 
- Your coding answers should be concise and straight to the point.
- You should think step by step when providing a coding answer
I am a Data Analyst based in Copenhagen who works for sports clothing brand called Danish Endurance. The tech stack I use is Google Big Query, hence, I do a lot of data modeling with SQL. Moreover, I also develop dashboards on Metabase which are also done in SQL.'''

sys_message_pythorn_dev = '''You are a professional Python Developer. Think Step by Step when giving your answers'''

if 'temp_disabler' not in st.session_state:
    st.session_state.temp_disabler = False

if 'sysrole_disabler' not in st.session_state:
    st.session_state.sysrole_disabler = False

if 'option_disabler' not in st.session_state:
    st.session_state.option_disabler = False

def define_parameters():
    # define the model parameters
    st.session_state.temp_disabler = True
    st.session_state.sysrole_disabler = True
    st.session_state.option_disabler = True


def change_system_state(): 
    if st.session_state.sysrole_button == 'General Dev':
        st.session_state.system_message = sys_message_general_dev
    elif st.session_state.sysrole_button == 'Python Specialist':
        st.session_state.system_message = sys_message_pythorn_dev
    st.session_state.messages[0] = SystemMessage(content=st.session_state.system_message)


st.subheader('Custom GPT 🤖')


with st.sidebar:
    temperature = st.slider('Temperature', 0.0, 1.0, 0.7, 0.1, disabled=st.session_state.temp_disabler)
    # Drop dowm menu for the system message
    option = st.selectbox(
        '#### Choose a System a Role',
        (' ','General Dev', 'Python Specialist'),
        key='sysrole_button',
        on_change=change_system_state
        , disabled=st.session_state.option_disabler)
    if option == ' ':
        st.session_state.system_message = ''
    if option == 'General Dev':
        st.session_state.system_message = sys_message_general_dev
    elif option == 'Python Specialist':
        st.session_state.system_message = sys_message_pythorn_dev
    st.text_area('#### System Role:',st.session_state.system_message, height=200, disabled=st.session_state.sysrole_disabler)
    st.button('Define Model Parameters', on_click=define_parameters)

chat = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=temperature, streaming=True, callbacks=[StreamingStdOutCallbackHandler()])

prompt_template = PromptTemplate.from_template(
    '''{prompt}'''
)  

# creating the messages (chat history) in the Streamlit session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append(
            SystemMessage(content=st.session_state.system_message)
            )

# if the user entered a question, append it to the session state
if prompt := st.chat_input("Ask a Quesiton"):
    if len(st.session_state.messages) == 1:
        prompt = prompt_template.format(prompt=prompt)
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

# displaying the messages (chat history)
for i, msg in enumerate(st.session_state.messages[1:]):
    if i % 2 == 0:
        with st.chat_message("user"):
            st.markdown(prompt)
    else:
        with st.chat_message("assistant"):
            st.markdown(msg.content)

# st.session_state.messages
# st.session_state.system_message
# run the app: streamlit run front_end_customGPT.py
