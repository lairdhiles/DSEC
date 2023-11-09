import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import date
import numbers
from st_aggrid import GridOptionsBuilder, AgGrid

from booking_risk import book_swap, load_risk, pnl
from fin_lib import plot_curve
from mkt_data import load_curve_from_data, load_live_data, load_sod_data, mkt_moves

# Set page configuration to wide mode
st.set_page_config(page_title="Trading Copilot",layout="wide",initial_sidebar_state="expanded")

# # Title for your app
st.title('Trading Copilot')

# Creating a layout with 2 columns: the main content and the chat column
# main_col, chat_col = st.columns([3, 1])  # Adjust the ratio as needed
col1, col2 = st.columns([2, 1])# Use the main column for the fixed content: table and graph
index = "Sonia"
risk = load_risk(index)
live_data = load_live_data(index)
sod_data = load_sod_data(index)
market_moves = mkt_moves(live_data,sod_data)
pnl_explain = pnl(live_data,sod_data,risk)


calc_date = date.today()
curve = load_curve_from_data(calc_date, sod_data, index)
curve_risk, quotes = load_curve_from_data(calc_date, sod_data, index, risk=True)

with col1:
    # Creating a sample dataframe for the table
    
    # Create a sample forward rates plot
    forward_rates = pd.DataFrame({
        'Date': pd.date_range(start='2024', periods=5, freq='Y'),
        'Forward Rates': np.random.rand(5)
    })

    fig = plot_curve(curve,"30Y")
    st.plotly_chart(fig)
    
with st.sidebar:
    
    data = pd.DataFrame({
    'risk': risk.values.flatten(),
    'moves': market_moves.values,
    'P&L': pnl_explain
    }, index=risk.index)
    
    data.loc['Total'] = data.sum(axis=0)
    
    # data.set_index('bucket', inplace=True)
    # data = data.style.hide(axis=0)

    # Display the table
    # st.table(data)
    
    def style_negative_positive(val):
        if isinstance(val, numbers.Number):
            color = 'red' if val < 0 else 'green' if val > 0 else ''
            return f'color: {color};'
        else:
            return f'color: white;'
    
    styled_data = data.style.applymap(style_negative_positive)#, subset=['risk', 'moves', 'P&L', 'Total'])
    st.table(styled_data.format(precision=4))
    

with col2:
    tab1, tab2, tab3 = st.tabs(["Swap", "Bond", "Fra/Future"])
    # Input forms
    with tab1:
        with st.form(key='my_form_swap'):
            notional = st.number_input(label='Enter Notional', value=1000000)
            start_date = st.date_input(label='Effective Date')
            maturity_date = st.date_input(label='Maturity Date')
            coupon = st.number_input(label='Fixed rate', value=5.0)
            pay_rcv = st.selectbox('Fixed pay/rcv',
                        ('Pay', 'Receive'))
            submit_button = st.form_submit_button(label='Book')
    
    with tab2:
        with st.form(key='my_form_bond'):
            notional = st.number_input(label='Enter Notional', value=1000000)
            start_date = st.date_input(label='Effective Date')
            maturity_date = st.date_input(label='Maturity Date')
            coupon = st.number_input(label='Fixed rate', value=5.0)/100
            pay_rcv = st.selectbox('Fixed pay/rcv',
                        ('Pay', 'Receive'))
            submit_button = st.form_submit_button(label='Book')
    
    with tab3:
        with st.form(key='my_form_fra'):
            notional = st.number_input(label='Enter Notional', value=1000000)
            start_date = st.date_input(label='Effective Date')
            maturity_date = st.date_input(label='Maturity Date')
            coupon = st.number_input(label='Fixed rate', value=5.0)
            pay_rcv = st.selectbox('Fixed pay/rcv',
                        ('Pay', 'Receive'))
            submit_button = st.form_submit_button(label='Book')

    # You can add callbacks or database interactions on button click
    if submit_button:
        print("hello")
        book_swap(index, notional, direction=pay_rcv, start_date=start_date, maturity_date=maturity_date,fixed_rate=coupon,curve=curve_risk,quotes=quotes)
        st.success('Transaction booked.')
        


from langchain.chains import LLMChain
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import StreamlitChatMessageHistory
from langchain.prompts import PromptTemplate

# Use the chat column for the scrollable chat

# st.header("Copilot")
# Set up memory
msgs = StreamlitChatMessageHistory(key="langchain_messages")
memory = ConversationBufferMemory(chat_memory=msgs)
if len(msgs.messages) == 0:
    msgs.add_ai_message("How can I help you?")

view_messages = st.expander("View the message contents in session state")

openai_api_key = st.secrets["OPENAI_API_KEY"]


template = """You are an AI chatbot having a conversation with a human.

{history}
Human: {human_input}
AI: """
prompt = PromptTemplate(input_variables=["history", "human_input"], template=template)
llm_chain = LLMChain(llm=OpenAI(openai_api_key=openai_api_key), prompt=prompt, memory=memory)

# Render current messages from StreamlitChatMessageHistory
for msg in msgs.messages:
    st.chat_message(msg.type).write(msg.content)

# If user inputs a new prompt, generate and draw a new response
if prompt := st.chat_input():
    st.chat_message("human").write(prompt)
    # Note: new messages are saved to history automatically by Langchain during run
    response = llm_chain.run(prompt)
    st.chat_message("ai").write(response)

# Draw the messages at the end, so newly generated ones show up immediately
with view_messages:
    """
    Memory initialized with:
    ```python
    msgs = StreamlitChatMessageHistory(key="langchain_messages")
    memory = ConversationBufferMemory(chat_memory=msgs)
    ```

    Contents of `st.session_state.langchain_messages`:
    """
    view_messages.json(st.session_state.langchain_messages)
