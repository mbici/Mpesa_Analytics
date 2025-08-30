import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date

# Configure page
st.set_page_config(
    page_title="Income Analysis",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Income Analysis")
st.markdown("Analyze your income sources and track money received over time.")

# Initialize session state variables for filters
def init_session_state():
    """Initialize session state variables for persistent filters"""
    if 'revenue_search_term' not in st.session_state:
        st.session_state.revenue_search_term = ""
    if 'revenue_chart_type' not in st.session_state:
        st.session_state.revenue_chart_type = "Bar Chart"
    if 'revenue_date_filter' not in st.session_state:
        st.session_state.revenue_date_filter = None
    if 'revenue_min_amount' not in st.session_state:
        st.session_state.revenue_min_amount = 0.0
    if 'revenue_max_amount' not in st.session_state:
        st.session_state.revenue_max_amount = 1000000.0
    if 'revenue_selected_sources' not in st.session_state:
        st.session_state.revenue_selected_sources = []
    if 'revenue_show_top_n' not in st.session_state:
        st.session_state.revenue_show_top_n = 15

init_session_state()

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

    # Add date column safely for filtering
    if 'Completion Time' in received.columns:
        received['date'] = received['Completion Time'].dt.date
    
    # Dynamic Filter Controls in Sidebar
    st.sidebar.header("🎛️ Dynamic Chart Controls")
    
    # Chart type selector
    chart_types = ["Bar Chart", "Pie Chart", "Line Chart", "Scatter Plot"]
    st.session_state.revenue_chart_type = st.sidebar.selectbox(
        "📊 Select Chart Type:",
        chart_types,
        index=chart_types.index(st.session_state.revenue_chart_type),
        key="chart_type_selector"
    )
    
    # Date range filter
    if 'date' in received.columns:
        min_date = received['date'].min()
        max_date = received['date'].max()
        
        st.sidebar.subheader("📅 Date Range Filter")
        date_range = st.sidebar.date_input(
            "Select date range:",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            key="date_range_selector"
        )
        
        # Apply date filter
        if len(date_range) == 2:
            start_date, end_date = date_range
            received = received[(received['date'] >= start_date) & (received['date'] <= end_date)]
    
    # Amount range filter
    if 'Paid In' in received.columns:
        min_amount = float(received['Paid In'].min())
        max_amount = float(received['Paid In'].max())
        
        st.sidebar.subheader("💰 Amount Range Filter")
        amount_range = st.sidebar.slider(
            "Select amount range (Ksh):",
            min_value=min_amount,
            max_value=max_amount,
            value=(min_amount, max_amount),
            step=100.0,
            key="amount_range_selector"
        )
        
        # Apply amount filter
        received = received[(received['Paid In'] >= amount_range[0]) & 
                          (received['Paid In'] <= amount_range[1])]
    
    # Income source filter
    if 'Details' in received.columns and not received.empty:
        available_sources = received['Details'].unique().tolist()
        st.sidebar.subheader("🏷️ Income Source Filter")
        selected_sources = st.sidebar.multiselect(
            "Select specific income sources:",
            options=available_sources,
            default=st.session_state.revenue_selected_sources if st.session_state.revenue_selected_sources else available_sources[:10],
            key="source_selector"
        )
        
        if selected_sources:
            received = received[received['Details'].isin(selected_sources)]
            st.session_state.revenue_selected_sources = selected_sources
    
    # Top N results filter
    st.session_state.revenue_show_top_n = st.sidebar.slider(
        "📈 Number of top results to show:",
        min_value=5,
        max_value=50,
        value=st.session_state.revenue_show_top_n,
        step=5,
        key="top_n_selector"
    )

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

    # Dynamic Charts Section
    st.subheader("🎯 Dynamic Income Analysis")
    
    if not received.empty:
        # Prepare data based on current filters
        details_data = pd.DataFrame(
            received.groupby('Details')['Paid In'].sum().sort_values(ascending=False)
        ).iloc[0:st.session_state.revenue_show_top_n].reset_index()
        
        if not details_data.empty:
            details_data = details_data.sort_values(by='Paid In', ascending=False)
            
            # Create dynamic chart based on selected type
            if st.session_state.revenue_chart_type == "Bar Chart":
                fig = px.bar(
                    details_data, 
                    x='Details', 
                    y='Paid In', 
                    title=f'Top {st.session_state.revenue_show_top_n} Income Sources - Bar Chart',
                    labels={'Paid In': 'Amount Received (Ksh)', 'Details': 'Income Sources'},
                    color='Paid In',
                    color_continuous_scale='Greens'
                )
                fig.update_xaxes(showticklabels=False)
                
            elif st.session_state.revenue_chart_type == "Pie Chart":
                fig = px.pie(
                    details_data, 
                    values='Paid In', 
                    names="Details",
                    title=f"Income Source Distribution - Top {st.session_state.revenue_show_top_n}"
                )
                
            elif st.session_state.revenue_chart_type == "Line Chart":
                # For line chart, use daily income data
                if 'date' in received.columns:
                    daily_data = received.groupby('date')['Paid In'].sum().reset_index()
                    daily_data = daily_data.sort_values('date')
                    fig = px.line(
                        daily_data,
                        x='date',
                        y='Paid In',
                        title='Daily Income Trend',
                        labels={'Paid In': 'Amount Received (Ksh)', 'date': 'Date'}
                    )
                else:
                    # Fallback to source-based line chart
                    fig = px.line(
                        details_data.reset_index(), 
                        x='index', 
                        y='Paid In',
                        title=f'Income Sources Trend - Top {st.session_state.revenue_show_top_n}',
                        labels={'Paid In': 'Amount Received (Ksh)', 'index': 'Rank'}
                    )
                    
            elif st.session_state.revenue_chart_type == "Scatter Plot":
                # Create scatter plot with amount vs frequency
                source_stats = received.groupby('Details').agg({
                    'Paid In': ['sum', 'count', 'mean']
                }).round(2)
                source_stats.columns = ['Total_Amount', 'Frequency', 'Average_Amount']
                source_stats = source_stats.reset_index()
                source_stats = source_stats.head(st.session_state.revenue_show_top_n)
                
                fig = px.scatter(
                    source_stats,
                    x='Frequency',
                    y='Total_Amount',
                    size='Average_Amount',
                    hover_data=['Details'],
                    title=f'Income Sources Analysis: Frequency vs Total Amount - Top {st.session_state.revenue_show_top_n}',
                    labels={
                        'Frequency': 'Number of Transactions',
                        'Total_Amount': 'Total Amount Received (Ksh)',
                        'Average_Amount': 'Average Amount (Ksh)'
                    }
                )
            
            # Update layout and display chart
            fig.update_layout(width=900, height=500, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            
            # Display filtered data summary
            col1, col2, col3 = st.columns(3)
            with col1:
                filtered_total = received['Paid In'].sum()
                st.metric("💰 Filtered Total Income", f"Ksh {filtered_total:,.0f}")
            with col2:
                filtered_count = len(received)
                st.metric("🔢 Filtered Transactions", f"{filtered_count:,}")
            with col3:
                filtered_avg = received['Paid In'].mean() if not received.empty else 0
                st.metric("📊 Filtered Average", f"Ksh {filtered_avg:,.0f}")
        else:
            st.info("No data available for the selected filters.")
    else:
        st.warning("No income data available after applying filters.")

    # Original static daily income chart (kept for comparison)
    st.subheader("📈 Daily Income Pattern")
    if 'Day of Month' in received.columns:
        daily_income = pd.DataFrame(received.groupby('Day of Month')['Paid In'].sum()).reset_index()
        
        if not daily_income.empty:
            st.line_chart(data=daily_income, x='Day of Month', y='Paid In', use_container_width=True)
        else:
            st.info("No daily income data available.")

    # Top income sources (kept as additional view)
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

    # Search specific income sources (with session state)
    st.header("🔍 Income Source Search")
    
    # Use session state for search term
    received_from = st.text_input(
        'Search income from specific source:', 
        value=st.session_state.revenue_search_term,
        help="Enter keywords to search for specific income sources",
        key="search_input"
    )
    
    # Update session state when input changes
    if received_from != st.session_state.revenue_search_term:
        st.session_state.revenue_search_term = received_from
    
    if received_from and len(received_from.strip()) > 0:
        try:
            # Use the original received data for search (not filtered data)
            original_received = st.session_state['received'].copy()
            matching_transactions = original_received[original_received['Details'].str.contains(received_from, na=False, case=False)]
            
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
