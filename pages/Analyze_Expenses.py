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
    withdrawals['date'] = withdrawals['Completion Time'].dt.date

    condition_to_remove = withdrawals['Details'].str.contains("MALI", case=False, na=False)
    remove= st.checkbox("Remove some transactions?")
    if remove:
        removed_transactions = st.multiselect("Remove transactions from?",options=["MALI","LEONARD"])

        pattern = '|'.join(removed_transactions)

        condition_to_remove = withdrawals['Details'].str.contains(pattern, case=False, na=False)
        withdrawals = withdrawals[~condition_to_remove]



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

    pie_fig = px.pie(details_data,values='Withdrawn',names="Details")
    pie_fig.update_layout(width=900, height=500,showlegend=False)

    st.plotly_chart(pie_fig,use_container_width=True)


    spent_on =st.text_input('View transactions for :',value=None)
    if spent_on is not None:
        st.write(f"You have spent a total of {withdrawals[withdrawals['Details'].str.contains(spent_on,na =False,case=False)]['Withdrawn'].sum()} on {withdrawals[withdrawals['Details'].str.contains(spent_on,na=False,case=False)]['Details'].iloc[0]}")
        st.write(withdrawals[withdrawals['Details'].str.contains(spent_on,na=False,case=False)])

    date_filter = st.date_input('View transactions for date :')
    if date_filter is not None:
        st.write(f"You spent a total of {withdrawals[withdrawals['date'] == date_filter]['Withdrawn'].sum()} on {date_filter}")
        st.write(withdrawals[withdrawals['date'] == date_filter])