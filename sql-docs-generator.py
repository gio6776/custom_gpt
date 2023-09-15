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

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'button_disabler' not in st.session_state:
    st.session_state.button_disabler = True

if 'prompt' not in st.session_state:
    st.session_state.prompt = ''

## Sql code and primary keys input start Enabled
if 'sql_code_input_disabler' not in st.session_state:
    st.session_state.sql_code_input_disabler = False

if 'primary_keys_input_disabler' not in st.session_state:
    st.session_state.primary_keys_input_disabler = False

# button starts visible
if 'button_visibility' not in st.session_state:
    st.session_state.button_visibility = True

# chat starts invisible
if 'chat_input_visibility' not in st.session_state:
    st.session_state.chat_input_visibility = False

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

# Orchestrates the initialization of session_states
def clear_session_states():
    st.session_state.messages = []
    st.session_state.button_disabler = True
    st.session_state.sql_code = ''
    st.session_state.primary_keys = ''
    st.session_state.prompt = ''
    st.session_state.sql_code_input_disabler = False
    st.session_state.primary_keys_input_disabler = False
    st.session_state.button_visibility = True
    del st.session_state.generate_doc


def disable_inputs():
    st.session_state.sql_code_input_disabler = True
    st.session_state.primary_keys_input_disabler = True
    st.session_state.button_visibility = False

with st.sidebar:
    '''This section uses LangChain\'s Prompt Tempalte to generate a Documentation in a stardardized format.
    \n The Documentation generate will have three main headings:
    \n 1. Model Overview: 
    \n 2. Primary Keys:
    \n 3. CTEs:
    \n 4. Fields Description:'''
    st.divider()



# setting the behaviour of the system message (role)
system_message = '''You are a professional Developer specialized in writing documentation of SQL code in Google Big Query Syntax. Your answers should have three main headings: 
    \n Model Overview: An one-paragraph written in an objective and concise way describing the model and its usage. It must contain two sentences separated by a dot 
    \n Primary Keys: A description of the primary keys of the table. Each primary key should be in a different line. The user will provide the primary keys in the prompt.
    \n CTEs: A description for each CTE in the SQL Code. Each CTE should be in a different line with the following format (CTE: description)
    \n Fields Description: A description of each field produced by the final SELECT statement. 
    \n - Each field should be in a different line with the following format (field: description). 
    \n - if the field is a metric, it should be followed by the unit of measurement in parenthesis.
    \n - if the field refers to Product Information you should group them in a single line with the following format'''


# instantiating the ChatGPT model
chat = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0.5, streaming=True, callbacks=[StreamingStdOutCallbackHandler()])

# if check_password():
st.subheader('SQL Code Documentation Assistant 🤖')


st.markdown('##### Enter the Information below to Generate a Documentation for your SQL Code')

# only visible when there's not human answer in st.session_state.messages
if st.session_state.sql_code_input_disabler == False and st.session_state.sql_code_input_disabler == False:
    st.text_input('Enter the SQL Code', key = 'sql_code')
    st.text_input('Enter the Primary Keys of the Table', key = 'primary_keys')

# Enable button if sql_code and primary_keys are not empty
if st.session_state.sql_code and st.session_state.primary_keys:
    st.session_state.button_disabler = False

if st.session_state.button_visibility == True:
    st.button('Generate SQL Doc', key='generate_doc', disabled=st.session_state.button_disabler, on_click=disable_inputs)


# check if there's a instance of SystemMessage class in the session state
if not any(isinstance(msg, SystemMessage) for msg in st.session_state.messages):
    # if not, add the system message to the session state
    st.session_state.messages.append(
            SystemMessage(content=system_message)
            )

prompt_template = PromptTemplate.from_template(

    '''
    Write a Documentation for the following SQL Code: 
    ### SQL CODE ###
        \n{sql_code}
    ######
        
    ### PRIMARY KEYS ###
        \n{primary_keys}
    ######
        '''
)  

# creating the messages (chat history) in the Streamlit session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append(
            SystemMessage(content=system_message)
            )

# if Button is clicked and chat input is not visible
if st.session_state.generate_doc and st.session_state.chat_input_visibility == False:
    # if this is the first message, add the prompt template
    if len(st.session_state.messages) == 1:
        st.session_state.prompt = prompt_template.format(
                sql_code=st.session_state.sql_code,
                primary_keys=st.session_state.primary_keys)
    else:
        st.session_state.prompt = st.session_state.sql_code

    st.session_state.messages.append(
        HumanMessage(content=st.session_state.prompt)
    )
    # disable sql_code and primary_keys input
    st.session_state.sql_code_input_disabler = True
    st.session_state.primary_keys_input_disabler = True

    with st.spinner('Working on your request ...'):
    # creating the ChatGPT response
        response = chat(st.session_state.messages)
    # adding the response's content to the session state
    st.session_state.messages.append(AIMessage(content=response.content))
    st.session_state.chat_input_visibility = True


# displaying the messages (chat history)
for i, msg in enumerate(st.session_state.messages[1:]):
    # if it's odd, it's a user message
    if i % 2 == 0:
        with st.chat_message("user"):
            st.markdown(st.session_state.prompt)
    # if it's even, it's a AI message
    else:
        with st.chat_message("assistant"):
            st.markdown(msg.content)

#     st.session_state.messages.append(AIMessage(content=response.content))
