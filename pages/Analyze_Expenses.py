import streamlit as st
import pandas as pd

import matplotlib.pyplot as plt
import plotly.express as px


# Function to format values for autopct
def func(pct, allvalues):
    absolute = round(pct/100.*sum(allvalues), 2)
    return f"{absolute}\n({pct:.1f}%)"



if 'Withdrawals' in st.session_state:
    
    
    withdrawals = st.session_state['Withdrawals']

    daily_expense= pd.DataFrame(withdrawals.groupby('Day of Month')['Withdrawn'].sum()).reset_index()

    st.line_chart(data=daily_expense,x='Day of Month',y='Withdrawn')

    # Sample data
    details_data = pd.DataFrame(withdrawals.groupby('Details')['Withdrawn'].sum().sort_values(ascending=False)).iloc[0:15].reset_index()

    details_data = details_data.sort_values(by='Withdrawn', ascending=False)

    # st.bar_chart(data= details_data,x='Details',y='Withdrawn')


    fig = px.bar(details_data, x='Details', y='Withdrawn', title='Top 10 Withdrawal Categories',
                labels={'Withdrawn': 'Amount Withdrawn', 'Details': 'Withdrawal Categories'})

    fig.update_layout(width=900, height=500)
    fig.update_xaxes(showticklabels=False)

    # Display the chart in Streamlit
    st.plotly_chart(fig,use_container_width=True)


    spent_on =st.text_input('View transactions for :',value=None)
    if spent_on is not None:
        st.write(f"You have spent a total of {withdrawals[withdrawals['Details'].str.contains(spent_on)].sum()['Withdrawn']} on {withdrawals[withdrawals['Details'].str.contains(spent_on)]['Details'].iloc[0]}")
        st.write(withdrawals[withdrawals['Details'].str.contains(spent_on)])

    date_filter = st.text_input('View transactions for date :',value=None)
    if date_filter is not None:
        date = f"{date_filter}/{withdrawals['Completion Time'].iloc[0].month}/{withdrawals['Completion Time'].iloc[0].year}"
        st.write(f"You spent a total of {withdrawals[withdrawals['Day of Month'] == int(date_filter)].sum()['Withdrawn']} on {date}")
        st.write(withdrawals[withdrawals['Day of Month'] == int(date_filter)])