import streamlit as st
import pandas as pd
import plotly.express as px
received = st.session_state['received']

daily_income = pd.DataFrame(received.groupby('Day of Month')['Paid In'].sum()).reset_index()

st.line_chart(data=daily_income,x='Day of Month',y='Paid In')

# Sample data
details_data = pd.DataFrame(received.groupby('Details')['Paid In'].sum().sort_values(ascending=False)).iloc[0:15].reset_index()

details_data = details_data.sort_values(by='Paid In', ascending=False)

# st.bar_chart(data= details_data,x='Details',y='Withdrawn')


fig = px.bar(details_data, x='Details', y='Paid In', title='Top 10 Income Received',
             labels={'Paid In': 'Income', 'Details': 'Received From'})

fig.update_layout(width=900, height=500)
fig.update_xaxes(showticklabels=False)

# Display the chart in Streamlit
st.plotly_chart(fig,use_container_width=True)


received_from =st.text_input('View transactions for money received From :',value=None)
if received_from is not None:

    st.write(f"You have received a total of {received[received['Details'].str.contains(received_from)].sum()['Paid In']} on {received[received['Details'].str.contains(received_from)]['Details'].iloc[0]}")
    st.write(received[received['Details'].str.contains(received_from)])
