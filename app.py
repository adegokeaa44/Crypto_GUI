#NEW

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import plotly.express as px
import time
import streamlit as st
import datetime
import seaborn as sns
import pickle

tickers_list = ['BTC-USD', 'ETH-USD', 'USDT-USD', 'LTC-USD', 'BCH-USD', 'BNB-USD', 
                'LINK-USD', 'ADA-USD', 'XLM-USD', 'DOGE-USD', 'DOT1-USD', 'UNI3-USD', 'THETA-USD', 
                'VET-USD', 'EOS-USD', 'TRX-USD', 'ATOM1-USD', 'BSV-USD', 'XMR-USD', 'IOTX-USD']

duration_type_list = ["day", "week", "month", "quarter"]
duration_map = {"day": 1, "week": 7, "month": 30, "quarter": 90}
models_list = ["Random Forest"]

st.title("SOLiGence \nLive Cryptocurrency Prices \nDASHBOARD")

currency_filter = st.selectbox("Select the Currency", tickers_list)

# Load the model from the saved file
with open('rfr_model.pkl', 'rb') as f:
    loaded_model = pickle.load(f)


def find_profit(data, times, profit, currency):
    current_value = data[currency]['Close'][-1]
    df_ = pd.DataFrame(columns=["Currency", "Date", "Expected Profit"])
    X_pred = pd.DataFrame({'ds': times})
    y_pred = loaded_model.predict(X_pred)
    for i in range(len(y_pred)):
        if (y_pred[i] - current_value) >= profit:
            df_.loc[len(df_.index)] = [currency, times[i], y_pred[i] - current_value]
    return df_, current_value


def get_prediction_data(data, duration):
    current_date = data.index[-1]
    times = [(current_date.to_pydatetime() + datetime.timedelta(days=x)) for x in range(duration_map[duration])]
    return times


placeholder = st.empty()

# create a container using the placeholder object
with placeholder.container():
    df = yf.download(tickers_list, period="max", interval="1d", group_by='tickers')
    idx = pd.IndexSlice
    df_tmp = df.loc[:, idx[:, 'Close']]

    fig_col1, fig_col2 = st.columns(2)
    with fig_col1:

        st.markdown("### Open")
        # creating the line figure for opening values
        fig = px.line(df[currency_filter], y="Open")
        st.write(fig)
    # set required data in the second column of the first row
    with fig_col2:
        # set title for the second column of the first row
        st.markdown("### Close")
        # creating the line figure for closing values
        fig2 = px.line(df[currency_filter], y="Close")
        st.write(fig2)
    fig_col3, fig_col4 = st.columns(2)
    with fig_col3:
        st.markdown("### High")
        fig3 = px.line(df[currency_filter], y="High")
        st.write(fig3)
    with fig_col4:
        st.markdown("### Low")
        fig4 = px.line(df[currency_filter], y="Low")
        st.write(fig4)
    fig_col5, fig_col6 = st.columns(2)
    with fig_col5:
        st.markdown("### Adjusted Close")
        fig5 = px.line(df[currency_filter], y="Adj Close")
        st.write(fig5)
    with fig_col6:
        st.markdown("### Volume")
        fig6 = px.line(df[currency_filter], y="Volume")
        st.write(fig6)
    # Seventh Chart
    fig_col7, fig_col8 = st.columns(2)
    with fig_col7:
        st.markdown("### Heatmap")
        fig7 = plt.figure()
        sns.heatmap(df_tmp.corr())
        st.write(fig7)
    with fig_col8:
        # Eighth Chart
        st.markdown("### Moving Average")
        df_copy = pd.DataFrame()
        df_copy['Close'] = df[currency_filter]['Close']
        df_copy = df_copy.reset_index()
        df_copy['rolling_mean'] = df_copy['Close'].rolling(7).mean()
        fig8 = plt.figure()
        sns.lineplot(x='Date',
                     y='Close',
                     data=df_copy,
                     label='Close Values')
        sns.lineplot(x='Date',
                     y='rolling_mean',
                     data=df_copy,
                     label='Rolling Close Values')
        st.write(fig8)

    with st.expander("Forcast Profit!"):

        duration_filter = st.selectbox("Select the Duration", duration_type_list)
        profit_filter = int(st.number_input('Insert the required profit'))
        model_filter = st.selectbox("Select the Predictor Model", models_list)

        if st.button('Submit'):

            with st.spinner('In progress...'):

                pred_data = get_prediction_data(df, duration_filter)
                X_pred = pd.DataFrame({'ds': pred_data})
                y_pred = loaded_model.predict(X_pred)
                forecast = np.array(y_pred)
                output, current_value = find_profit(df, pred_data, profit_filter, currency_filter)

                st.write("Output Dataframe is generated!! with current value as " + str(current_value))

                for i in range(len(pred_data)):
                    st.write("" + str(pred_data[i]) + "\t\t" + str(forecast[i]))

                st.dataframe(output)

                if output.shape[0] != 0:
                    fig3 = px.bar(output, x="Date", y="Expected Profit")
                    st.write(fig3)
                else:
                    st.write("No dates found!!")

