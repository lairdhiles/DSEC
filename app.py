import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Title for your app
st.title('IR Derivatives Analytics Dashboard')


# Initialize session state to store messages if it doesn't exist
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Function to display messages
def display_messages():
    for message in st.session_state.messages:
        with st.chat_message(message['user']):
            st.write(message['text'])
            if message['type'] == 'chart':
                st.line_chart(np.random.randn(10, 2))

# Chat input
prompt = st.chat_input("Say something")
if prompt:
    # Here you would process the prompt and determine the response
    # For the sake of the example, we assume that every prompt is added as a user message
    st.session_state.messages.append({"user": "user", "text": prompt, "type": "text"})
    # Display updated messages
    display_messages()
    # You might want to clear the prompt here, or handle the state differently
    prompt = ""

# Display chat messages
for username, message in reversed(st.session_state.messages):
    with st.chat_message(username):
        st.write(message)

# Creating a sample dataframe for the table
data = pd.DataFrame({
    'bucket': ['1D', '1IMM', '2IMM', '3IMM'],
    'risk': np.random.randn(4),
    'moves': np.random.randn(4),
    'P&L': np.random.randint(1000, size=4)
})

# Display the table
st.table(data)

# Create a sample forward rates plot
forward_rates = pd.DataFrame({
    'Date': pd.date_range(start='2024', periods=5, freq='Y'),
    'Forward Rates': np.random.rand(5)
})

fig = px.line(forward_rates, x='Date', y='Forward Rates', title='Daily Forward Rates from the Yield Curve')
st.plotly_chart(fig)

# Input forms
with st.form(key='my_form'):
    notional = st.number_input(label='Enter Notional', value=1000000)
    effective_date = st.date_input(label='Effective Date')
    maturity_date = st.date_input(label='Maturity Date')
    coupon = st.number_input(label='Coupon', value=5.0)
    submit_button = st.form_submit_button(label='Book')

# You can add callbacks or database interactions on button click
if submit_button:
    st.write('Transaction booked.')