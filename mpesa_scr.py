import streamlit as st
import time
import pandas as pd

st.set_page_config(
    page_title="Summary of transactions ",
    page_icon="👋",
)


st.sidebar.image('mpesa.png')

import tabula

def custom_to_float(value):
    """
    Converts a given value to a float.

    Args:
    value: The value to be converted to a float.

    Returns:
    float: The converted float value if successful, otherwise returns the original value.
    """
    if isinstance(value, str):
        try:
            return float(value.replace(',', ''))
        except ValueError:
            return value
    return value
st.write("Upload your Mpesa statement pdf")

uploaded_file = st.file_uploader("Encrypted Pdf File",)

st.selectbox('How long does your statement run?',
             ("1 month","2+ Months"))

if uploaded_file is not None:

    passwo = st.text_input("Enter password for the encrypted File")


    if passwo is not None:
        tables = tabula.read_pdf(uploaded_file, pages='all', multiple_tables=True,password = passwo)

        selected_dfs = []

        for i, df in enumerate(tables[2:]):
            if i % 2 == 0:
                selected_dfs.append(df)

        resulting_dataframe = pd.concat(selected_dfs, ignore_index=True)

        resulting_dataframe.drop(['Unnamed: 0'],axis=1,inplace=True)

        resulting_dataframe['Completion Time'] = pd.to_datetime(resulting_dataframe['Completion Time'])

        resulting_dataframe['Month'] = resulting_dataframe['Completion Time'].dt.month

        resulting_dataframe = resulting_dataframe.fillna(0)

        for col in ['Paid In','Withdrawn','Balance']:

            resulting_dataframe[col] = resulting_dataframe[col].apply(custom_to_float)

        total_paid = resulting_dataframe['Withdrawn'].sum()

        total_received = resulting_dataframe['Paid In'].sum()

        
        st.write(resulting_dataframe.head(10))

        st.write(f"You have Spent Kshs.{round(abs(total_paid),0)}")

        st.write("Your top 10 paid transactions are:")


        withdrawals = resulting_dataframe[resulting_dataframe['Withdrawn'] != 0]
        withdrawals.loc[:,'Withdrawn'] =withdrawals.loc[:,'Withdrawn']*-1
        withdrawals.loc[:,'Day of Month'] = withdrawals['Completion Time'].dt.day
        received = resulting_dataframe[resulting_dataframe['Paid In'] != 0]

        received.loc[:,'Day of Month'] = received['Completion Time'].dt.day

        st.write(withdrawals.groupby('Details')['Withdrawn'].sum().sort_values(ascending=False).iloc[0:10])

        if 'Withdrawals' not in st.session_state:
            st.session_state['Withdrawals'] = withdrawals
        
        if 'received' not in st.session_state:
            st.session_state['received'] = received

        st.write(f"You have Received Kshs. {total_received}")
