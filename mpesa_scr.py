import streamlit as st
import time
import pandas as pd

st.set_page_config(
    page_title="Summary of transactions ",
    page_icon="👋",
)



import hmac
import streamlit as st


def check_password():
    """Returns `True` if the user had a correct password."""

    def login_form():
        """Form with widgets to collect user information"""
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=password_entered)

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] in st.secrets[
            "passwords"
        ] and hmac.compare_digest(
            st.session_state["password"],
            st.secrets.passwords[st.session_state["username"]],
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the username or password.
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show inputs for username + password.
    login_form()
    if "password_correct" in st.session_state:
        st.error("😕 User not known or password incorrect")
    return False


if not check_password():
    st.stop()

# Main Streamlit app starts here
st.write("Here goes your normal Streamlit app...")
st.button("Click me")
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
