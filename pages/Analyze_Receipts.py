import streamlit as st
import pandas as pd
import plotly.express as px

# Configure page
st.set_page_config(
    page_title="Income Analysis",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Income Analysis")
st.markdown("Analyze your income sources and track money received over time.")

# Check if data is available
if 'received' not in st.session_state:
    st.error("❌ No income data found!")
    st.info("Please upload and process your M-Pesa statement on the main page first.")
    st.stop()

try:
    received = st.session_state['received'].copy()
    
    if received.empty:
        st.warning("⚠️ No income transactions found in your statement.")
        st.stop()

    # Display summary metrics
    st.header("📊 Income Summary")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_income = received['Paid In'].sum()
        st.metric(
            label="💰 Total Income", 
            value=f"Ksh {total_income:,.0f}"
        )
    
    with col2:
        avg_income = received['Paid In'].mean()
        st.metric(
            label="📊 Average Transaction", 
            value=f"Ksh {avg_income:,.0f}"
        )
    
    with col3:
        num_transactions = len(received)
        st.metric(
            label="🔢 Total Transactions", 
            value=f"{num_transactions:,}"
        )

    # Daily income chart
    st.subheader("📈 Daily Income Pattern")
    if 'Day of Month' in received.columns:
        daily_income = pd.DataFrame(received.groupby('Day of Month')['Paid In'].sum()).reset_index()
        
        if not daily_income.empty:
            st.line_chart(data=daily_income, x='Day of Month', y='Paid In', use_container_width=True)
        else:
            st.info("No daily income data available.")

    # Top income sources
    st.subheader("🎯 Top Income Sources")
    details_data = pd.DataFrame(received.groupby('Details')['Paid In'].sum().sort_values(ascending=False)).iloc[0:15].reset_index()

    if not details_data.empty:
        details_data = details_data.sort_values(by='Paid In', ascending=False)

        # Bar chart
        fig = px.bar(
            details_data, 
            x='Details', 
            y='Paid In', 
            title='Top 15 Income Sources',
            labels={'Paid In': 'Amount Received (Ksh)', 'Details': 'Income Sources'},
            color='Paid In',
            color_continuous_scale='Greens'
        )

        fig.update_layout(width=900, height=500, showlegend=False)
        fig.update_xaxes(showticklabels=False)
        st.plotly_chart(fig, use_container_width=True)

        # Pie chart for income distribution
        pie_fig = px.pie(
            details_data, 
            values='Paid In', 
            names="Details",
            title="Income Source Distribution"
        )
        pie_fig.update_layout(width=900, height=500, showlegend=False)
        st.plotly_chart(pie_fig, use_container_width=True)
    else:
        st.info("No income sources to display.")

    # Search specific income sources
    st.header("🔍 Income Source Search")
    
    received_from = st.text_input(
        'Search income from specific source:', 
        value="",
        help="Enter keywords to search for specific income sources"
    )
    
    if received_from and len(received_from.strip()) > 0:
        try:
            matching_transactions = received[received['Details'].str.contains(received_from, na=False, case=False)]
            
            if not matching_transactions.empty:
                total_received_from = matching_transactions['Paid In'].sum()
                # Get the most common source name for display
                source_name = matching_transactions['Details'].iloc[0] if len(matching_transactions) > 0 else received_from
                
                st.success(f"💰 Total received from sources containing '{received_from}': **Ksh {total_received_from:,.0f}**")
                st.dataframe(matching_transactions, use_container_width=True, hide_index=True)
            else:
                st.info(f"No income transactions found containing '{received_from}'")
                
        except Exception as e:
            st.error(f"Error searching income sources: {str(e)}")

    # Recent transactions table
    st.subheader("📋 Recent Income Transactions")
    if not received.empty:
        # Sort by completion time if available
        if 'Completion Time' in received.columns:
            recent_transactions = received.sort_values('Completion Time', ascending=False).head(20)
        else:
            recent_transactions = received.head(20)
        
        st.dataframe(
            recent_transactions[['Completion Time', 'Details', 'Paid In']].rename(columns={
                'Completion Time': 'Date & Time',
                'Details': 'Source',
                'Paid In': 'Amount (Ksh)'
            }) if 'Completion Time' in recent_transactions.columns else recent_transactions[['Details', 'Paid In']].rename(columns={
                'Details': 'Source',
                'Paid In': 'Amount (Ksh)'
            }),
            use_container_width=True,
            hide_index=True
        )

except Exception as e:
    st.error(f"❌ An error occurred while processing income data: {str(e)}")
    st.error("Please try refreshing the page or re-uploading your statement.")
