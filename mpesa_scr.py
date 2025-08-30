import streamlit as st
import time
import pandas as pd

st.set_page_config(
    page_title="M-Pesa Analytics Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
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
st.title("🏦 M-Pesa Analytics Dashboard")
st.markdown("Welcome to your personal M-Pesa transaction analyzer! Upload your statement to get detailed insights about your spending patterns and income sources.")

# Create sidebar with app info
st.sidebar.title("📊 M-Pesa Analytics")
st.sidebar.image('mpesa.png', width=200)
st.sidebar.markdown("---")
st.sidebar.markdown("**Features:**")
st.sidebar.markdown("• 📈 Transaction Analysis")
st.sidebar.markdown("• 💸 Expense Tracking") 
st.sidebar.markdown("• 💰 Income Analysis")
st.sidebar.markdown("• 📊 Visual Reports")

import tabula

# File upload section
st.header("📄 Upload Your M-Pesa Statement")
st.markdown("Please upload your encrypted PDF statement to begin the analysis.")

col1, col2 = st.columns([2, 1])

with col1:
    uploaded_file = st.file_uploader(
        "Choose your M-Pesa PDF statement", 
        type=['pdf'],
        help="Select the encrypted PDF statement downloaded from M-Pesa"
    )

with col2:
    statement_duration = st.selectbox(
        'Statement Duration',
        ("1 month", "2+ Months"),
        help="How long does your statement cover?"
    )

if uploaded_file is not None:
    st.success("✅ File uploaded successfully!")
    
    # Password input with validation
    with st.container():
        st.subheader("🔐 File Decryption")
        passwo = st.text_input(
            "Enter the password for your encrypted statement", 
            type="password",
            help="This is the password you set when downloading the statement from M-Pesa"
        )
        
        if passwo and len(passwo.strip()) > 0:
            with st.spinner("🔄 Processing your statement... This may take a few moments."):
                try:
                    tables = tabula.read_pdf(uploaded_file, pages='all', multiple_tables=True, password=passwo)
                    
                    if not tables or len(tables) < 3:
                        st.error("❌ Unable to extract data from the PDF. Please check if the password is correct or if the file format is supported.")
                        st.stop()
                    
                    selected_dfs = []
                    
                    for i, df in enumerate(tables[2:]):
                        if i % 2 == 0:
                            selected_dfs.append(df)
                    
                    if not selected_dfs:
                        st.error("❌ No transaction data found in the statement.")
                        st.stop()
                    
                    resulting_dataframe = pd.concat(selected_dfs, ignore_index=True)
                    
                    # Clean and process data
                    if 'Unnamed: 0' in resulting_dataframe.columns:
                        resulting_dataframe.drop(['Unnamed: 0'], axis=1, inplace=True)
                    
                    if 'Completion Time' in resulting_dataframe.columns:
                        resulting_dataframe['Completion Time'] = pd.to_datetime(resulting_dataframe['Completion Time'], errors='coerce')
                        resulting_dataframe['Month'] = resulting_dataframe['Completion Time'].dt.month
                    else:
                        st.error("❌ Required 'Completion Time' column not found in the statement.")
                        st.stop()
                    
                    resulting_dataframe = resulting_dataframe.fillna(0)
                    
                    # Apply custom float conversion with error handling
                    for col in ['Paid In', 'Withdrawn', 'Balance']:
                        if col in resulting_dataframe.columns:
                            resulting_dataframe[col] = resulting_dataframe[col].apply(custom_to_float)
                    
                    total_paid = abs(resulting_dataframe['Withdrawn'].sum()) if 'Withdrawn' in resulting_dataframe.columns else 0
                    total_received = resulting_dataframe['Paid In'].sum() if 'Paid In' in resulting_dataframe.columns else 0
                    
                    # Display summary with nice formatting
                    st.success("🎉 Statement processed successfully!")
                    
                    # Summary metrics
                    st.header("📊 Transaction Summary")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric(
                            label="💸 Total Spent", 
                            value=f"Ksh {total_paid:,.0f}",
                            help="Total amount withdrawn/spent"
                        )
                    
                    with col2:
                        st.metric(
                            label="💰 Total Received", 
                            value=f"Ksh {total_received:,.0f}",
                            help="Total amount received"
                        )
                    
                    with col3:
                        net_balance = total_received - total_paid
                        st.metric(
                            label="📈 Net Balance", 
                            value=f"Ksh {net_balance:,.0f}",
                            delta=f"{'Surplus' if net_balance > 0 else 'Deficit'}",
                            help="Net difference between received and spent"
                        )
                    
                    # Recent transactions preview
                    st.subheader("🔍 Recent Transactions Preview")
                    if not resulting_dataframe.empty:
                        st.dataframe(
                            resulting_dataframe.head(10), 
                            use_container_width=True,
                            hide_index=True
                        )
                    
                    # Process withdrawal and receipt data
                    withdrawals = resulting_dataframe[resulting_dataframe['Withdrawn'] != 0].copy() if 'Withdrawn' in resulting_dataframe.columns else pd.DataFrame()
                    received = resulting_dataframe[resulting_dataframe['Paid In'] != 0].copy() if 'Paid In' in resulting_dataframe.columns else pd.DataFrame()
                    
                    if not withdrawals.empty:
                        withdrawals.loc[:, 'Withdrawn'] = withdrawals.loc[:, 'Withdrawn'] * -1
                        withdrawals.loc[:, 'Day of Month'] = withdrawals['Completion Time'].dt.day
                        
                        st.subheader("💸 Top Spending Categories")
                        top_expenses = withdrawals.groupby('Details')['Withdrawn'].sum().sort_values(ascending=False).head(10)
                        
                        if not top_expenses.empty:
                            for i, (category, amount) in enumerate(top_expenses.items(), 1):
                                st.write(f"{i}. **{category}**: Ksh {amount:,.0f}")
                    
                    if not received.empty:
                        received.loc[:, 'Day of Month'] = received['Completion Time'].dt.day
                    
                    # Store data in session state for analysis pages
                    if not withdrawals.empty:
                        st.session_state['Withdrawals'] = withdrawals
                    if not received.empty:
                        st.session_state['received'] = received
                    
                    st.info("📈 Use the sidebar to navigate to 'Analyze Expenses' or 'Analyze Receipts' for detailed analysis!")
                    
                except Exception as e:
                    st.error(f"❌ Error processing the PDF: {str(e)}")
                    st.error("This could be due to:")
                    st.error("• Incorrect password")
                    st.error("• Corrupted or unsupported PDF format")
                    st.error("• Network connectivity issues")
                    st.error("Please check your file and password, then try again.")
        
        elif passwo is not None and len(passwo.strip()) == 0:
            st.warning("⚠️ Please enter a password to decrypt your statement.")
    
else:
    st.info("👆 Please upload your M-Pesa PDF statement to begin analysis.")


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
