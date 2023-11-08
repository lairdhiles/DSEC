import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Title for your app
st.title('IR Derivatives Analytics Dashboard')


import streamlit as st
import openai
import os

st.title("ChatGPT-like clone")

# Set OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Set a default model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

client = openai.OpenAI()

completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
    {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
  ]
)
# for response in client.chat.completions.create(
#         model=st.session_state["openai_model"],
#         messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
#         stream=True,
#     ):
#         full_response += response['choices'][0]['delta'].get("content", "")
#         message_placeholder.markdown(full_response + "▌")

full_response = client.chat.completions.create(
        model=st.session_state["openai_model"],
        messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]).choices[0].message.content.strip()

st.session_state.messages.append({"role": "assistant", "content": full_response})

# Display chat messages
for username, message in reversed(st.session_state.messages):
    with st.chat_message(username):
        st.write(message)

print("hello")
# # Creating a sample dataframe for the table
# data = pd.DataFrame({
#     'bucket': ['1D', '1IMM', '2IMM', '3IMM'],
#     'risk': np.random.randn(4),
#     'moves': np.random.randn(4),
#     'P&L': np.random.randint(1000, size=4)
# })

# # Display the table
# st.table(data)

# # Create a sample forward rates plot
# forward_rates = pd.DataFrame({
#     'Date': pd.date_range(start='2024', periods=5, freq='Y'),
#     'Forward Rates': np.random.rand(5)
# })

# fig = px.line(forward_rates, x='Date', y='Forward Rates', title='Daily Forward Rates from the Yield Curve')
# st.plotly_chart(fig)

# # Input forms
# with st.form(key='my_form'):
#     notional = st.number_input(label='Enter Notional', value=1000000)
#     effective_date = st.date_input(label='Effective Date')
#     maturity_date = st.date_input(label='Maturity Date')
#     coupon = st.number_input(label='Coupon', value=5.0)
#     submit_button = st.form_submit_button(label='Book')

# # You can add callbacks or database interactions on button click
# if submit_button:
#     st.write('Transaction booked.')
