import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# Configure page
st.set_page_config(
    page_title="Expense Analysis",
    page_icon="💸",
    layout="wide"
)

st.title("💸 Expense Analysis")
st.markdown("Analyze your spending patterns and identify your top expense categories.")

# Function to format values for autopct
def func(pct, allvalues):
    absolute = round(pct/100.*sum(allvalues), 2)
    return f"{absolute}\n({pct:.1f}%)"

# Check if data is available
if 'Withdrawals' not in st.session_state:
    st.error("❌ No expense data found!")
    st.info("Please upload and process your M-Pesa statement on the main page first.")
    st.stop()

try:
    withdrawals = st.session_state['Withdrawals'].copy()
    
    if withdrawals.empty:
        st.warning("⚠️ No withdrawal transactions found in your statement.")
        st.stop()
    
    # Add date column safely
    if 'Completion Time' in withdrawals.columns:
        withdrawals['date'] = withdrawals['Completion Time'].dt.date
    else:
        st.error("❌ Date information missing from transaction data.")
        st.stop()

    # Transaction filtering options
    st.sidebar.header("🔧 Filter Options")
    
    # Remove specific transactions
    remove = st.sidebar.checkbox("Remove specific transactions")
    if remove:
        available_options = ["MALI", "LEONARD","NCBA"]
        # Find available patterns in the data
        for pattern in available_options:
            if withdrawals['Details'].str.contains(pattern, case=False, na=False).any():
                continue
        
        removed_transactions = st.sidebar.multiselect(
            "Select transaction types to remove:",
            options=available_options,
            help="Remove specific transaction types from analysis"
        )

        if removed_transactions:
            pattern = '|'.join(removed_transactions)
            condition_to_remove = withdrawals['Details'].str.contains(pattern, case=False, na=False)
            withdrawals = withdrawals[~condition_to_remove]
            
            if withdrawals.empty:
                st.warning("⚠️ All transactions have been filtered out. Please adjust your filters.")
                st.stop()

    # Display summary metrics
    st.header("📊 Expense Summary")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_expenses = withdrawals['Withdrawn'].sum()
        st.metric(
            label="💸 Total Expenses", 
            value=f"Ksh {total_expenses:,.0f}"
        )
    
    with col2:
        avg_transaction = withdrawals['Withdrawn'].mean()
        st.metric(
            label="📊 Average Transaction", 
            value=f"Ksh {avg_transaction:,.0f}"
        )
    
    with col3:
        num_transactions = len(withdrawals)
        st.metric(
            label="🔢 Total Transactions", 
            value=f"{num_transactions:,}"
        )

    # Daily expense chart
    st.subheader("📈 Daily Spending Pattern")
    if 'Day of Month' in withdrawals.columns:
        daily_expense = pd.DataFrame(withdrawals.groupby('Day of Month')['Withdrawn'].sum()).reset_index()
        
        if not daily_expense.empty:
            st.line_chart(data=daily_expense, x='Day of Month', y='Withdrawn', use_container_width=True)
        else:
            st.info("No daily expense data available.")
    
    # Top expense categories
    st.subheader("🎯 Top Expense Categories")
    details_data = pd.DataFrame(withdrawals.groupby('Details')['Withdrawn'].sum().sort_values(ascending=False)).iloc[0:15].reset_index()

    if not details_data.empty:
        details_data = details_data.sort_values(by='Withdrawn', ascending=False)

        # Bar chart
        fig = px.bar(
            details_data, 
            x='Details', 
            y='Withdrawn', 
            title='Top 15 Expense Categories',
            labels={'Withdrawn': 'Amount Spent (Ksh)', 'Details': 'Expense Categories'},
            color='Withdrawn',
            color_continuous_scale='Reds'
        )

        fig.update_layout(width=900, height=500, showlegend=False)
        fig.update_xaxes(showticklabels=False)
        st.plotly_chart(fig, use_container_width=True)

        # Pie chart
        pie_fig = px.pie(
            details_data, 
            values='Withdrawn', 
            names="Details",
            title="Expense Distribution"
        )
        pie_fig.update_layout(width=900, height=500, showlegend=False)
        st.plotly_chart(pie_fig, use_container_width=True)
    else:
        st.info("No expense categories to display.")

    # Search and filter transactions
    st.header("🔍 Transaction Search & Filter")
    
    col1, col2 = st.columns(2)
    
    with col1:
        spent_on = st.text_input(
            'Search transactions containing:', 
            value="",
            help="Enter keywords to search in transaction details"
        )
        
        if spent_on and len(spent_on.strip()) > 0:
            try:
                matching_transactions = withdrawals[withdrawals['Details'].str.contains(spent_on, na=False, case=False)]
                
                if not matching_transactions.empty:
                    total_spent = matching_transactions['Withdrawn'].sum()
                    st.success(f"💰 Total spent on '{spent_on}': **Ksh {total_spent:,.0f}**")
                    st.dataframe(matching_transactions, use_container_width=True, hide_index=True)
                else:
                    st.info(f"No transactions found containing '{spent_on}'")
                    
            except Exception as e:
                st.error(f"Error searching transactions: {str(e)}")
    
    with col2:
        date_filter = st.date_input(
            'View transactions for specific date:',
            help="Select a date to view all transactions for that day"
        )
        
        if date_filter is not None:
            try:
                date_transactions = withdrawals[withdrawals['date'] == date_filter]
                
                if not date_transactions.empty:
                    daily_total = date_transactions['Withdrawn'].sum()
                    st.success(f"💸 Total spent on {date_filter}: **Ksh {daily_total:,.0f}**")
                    st.dataframe(date_transactions, use_container_width=True, hide_index=True)
                else:
                    st.info(f"No transactions found for {date_filter}")
                    
            except Exception as e:
                st.error(f"Error filtering by date: {str(e)}")

except Exception as e:
    st.error(f"❌ An error occurred while processing expense data: {str(e)}")
    st.error("Please try refreshing the page or re-uploading your statement.")
