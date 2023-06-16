# import library
import pandas as pd #data manipulate
import streamlit as st #web abb (Dashboard (DB))
import numpy as np # function (math,arrays)
from datetime import datetime # handle with time
import datetime
import altair as alt # visualized (DB)
from openpyxl import load_workbook # excel
import matplotlib.pyplot as plt # visualized
import seaborn as sns # visualized
import plotly.express as px # ***visualized
import plotly.graph_objs as go # visualized
import re # set of strings that matches
import seaborn as sns # visualized
import warnings  
warnings.filterwarnings('ignore') # ignore warning
import calendar #datetime
from sklearn.linear_model import LinearRegression

# text layout
st.set_page_config(
    page_title="LAST RN",
    layout = 'wide',
)
st.markdown('**LAST 20 RN (AMBER 85)**')
# read file , astype to float64
all = pd.read_csv('reservations_summary_report (5).csv',thousands=',')
# convert roomtype
def convert_room_type(room_type):
  if re.search(r'\bGRAND DELUXE ROOM\b|\bGRAND DELUXE\b|\bGRAND DELUXE DOUBLE ROOM\b|\bGRAND DELUXE ROOM ONLY\b|\bGRAND DOUBLE OR TWIN ROOM\b|\bDOUBLE GRAND DELUXE DOUBLE ROOM\b', room_type):
    return 'GRAND DELUXE'
  elif re.search(r'\bDELUXE DOUBLE ROOM\b|\bDELUXE DOUBLE OR TWIN ROOM WITH CITY VIEW\b|\bDELUXE ROOM CITY VIEW\b|\bDELUXE ROOM ONLY\b|\bDELUXE DOUBLE OR TWIN ROOM\b|\bNEW DELUXE DOUBLE\b|\bDELUXE ROOM\b', room_type):
    return 'NEW DELUXE'
  elif re.search(r'\bNEW DELUXE TWIN\b|\bDELUXE TWIN ROOM\b|\bDOUBLE OR TWIN NEW DELUXE DOUBLE OR TWIN\b|\bDELUXE TWIN ROOM ONLY\b|\bTWIN NEW DELUXE TWIN ROOM\b', room_type):
    return 'NEW DELUXE TWIN'
  elif re.search(r'\bGRAND CORNER SUITES\b|\bGRAND DELUXE\b|\bSUITE WITH BALCONY\b|\bGRAND CORNER SUITES ROOM ONLY\b|\bSUITE SUITE GRAND CORNER\b|\bGRAND STUDIO SUITE\b|\bGRAND CORNER SUITE\b', room_type):
    return 'GRAND CORNER SUITES'
  elif re.search(r'\bMIXED ROOM\b', room_type):
    return 'MIXED'
  else: 
    return 'UNKNOWN'
# dis count adr
def apply_discount(channel, adr):
    if channel == 'Booking.com':
      return adr * 0.82
    elif channel == 'Expedia':
      return adr * 0.80
    else:
      return adr
# if multi room convert to MIXED ROOM
def clean_room_type(room_type):
    if ' X '  in room_type:
        room_type = 'MIXED ROOM'
    return room_type

# discount ABF
def calculate_adr_per_rn_abf(row):
    if row['RO/ABF'] == 'ABF':
      return row['ADR'] - 260
    else:
      return row['ADR']
# To find NRF/F
def convert_RF(room_type):
      if re.search(r'\bNON REFUNDABLE\b|\bไม่สามารถคืนเงินจอง\b|\bNON REFUND\b|\bNON-REFUNDABLE\b|\bNRF\b', room_type):
            return 'NRF'
      elif re.search(r'\bUNKNOWN ROOM\b', room_type):
            return 'UNKNOWN'
      elif  room_type == "1 X " or room_type == "2 X " or room_type == "3 X " or room_type == "4 X ":
            return 'UNKNOWN'
      else:
            return 'Flexible'
# To find ABF/RO
def convert_ABF(room_type):
      if re.search(r'\bBREAKFAST\b|\bWITH BREAKFAST\b|\bBREAKFAST INCLUDED\b', room_type):
            return 'ABF'
      elif re.search(r'\bUNKNOWN ROOM\b', room_type):
            return 'UNKNOWN'
      elif  room_type == "1 X " or room_type == "2 X " or room_type == "3 X " or room_type == "4 X ":
            return 'UNKNOWN'
      elif re.search(r'\bRO\b|\bROOM ONLY\b', room_type):
            return 'RO'
      else:
            return 'RO'

def perform(all): 
    all1 = all[['Booking reference'
                ,'Guest names'
                ,'Check-in'
                ,'Check-out'
                ,'Channel'
                ,'Room'
                ,'Booked-on date'
                ,'Total price']] # focus on columns (Col) that we choose
    all1 = all1.dropna()  # drop empty values

    all1["Check-in"] = pd.to_datetime(all1["Check-in"]) # astype to datetime
    all1['Booked-on date'] = pd.to_datetime(all1['Booked-on date']) 
    all1['Booked'] = all1['Booked-on date'].dt.strftime('%m/%d/%Y') # extract just mm/dd/yyyy ( sting (str) type)
    all1['Booked'] = pd.to_datetime(all1['Booked'])
    all1["Check-out"] = pd.to_datetime(all1["Check-out"])
    all1["Length of stay"] = (all1["Check-out"] - all1["Check-in"]).dt.days # cal LOS
    all1["Lead time"] = (all1["Check-in"] - all1["Booked"]).dt.days # cal LT
    LT1 = [-1, 0, 1, 2, 3, 4, 5, 6, 7,8, 14, 30, 90, 120] #grouping data
    LT2 = ['-one', 'zero', 'one', 'two', 'three', 'four', 'five', 'six','seven', '8-14', '14-30', '31-90', '90-120', '120+']
    LT11 = [-1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,31,90, 120, float('inf')]
    LT22 = ['.-1.', '.0.', '.1.', '.2.', '.3.', '.4.', '.5.', '.6.', '.7.', '.8.', '.9.', '.10.', '.11.', '.12.', '.13.', '.14.', '.15.', '.16.', '.17.', '.18.', '.19.', '.20.', '.21.', '.22.', '23.', '.24.', '25.', '.26.', '.27.', '.28.', '.29.', '.30.', '31-90.', '91-120', '120.+']
    value_ranges1 = [1,2,3,4,5,6,7,8,9,10,14,30,45,60]
    labels1 = ['one', 'two', 'three', 'four', 'five', 'six','seven','eight', 'nine', 'ten', '14-30', '30-45','45-60', '60+']
    all1['Lead time range'] = pd.cut(all1['Lead time'], bins=LT1 + [float('inf')], labels=LT2, right=False)
    all1['Lead time range1'] = pd.cut(all1['Lead time'], bins=LT11, labels=LT22, right=False)
    all1['LOS range'] = pd.cut(all1['Length of stay'], bins=value_ranges1 + [float('inf')], labels=labels1, right=False)

    all1['Room'] = all1['Room'].str.upper() #convert to uppercase
    all1['Booking reference'] = all1['Booking reference'].astype('str') # astype (datatype)
    all1['Total price'] = all['Total price'].str.strip('THB') # 'THB 1500' to '1500'
    all1['Total price'] = all1['Total price'].astype('float64') # astype
    all1['Quantity'] = all1['Room'].str.extract('^(\d+)', expand=False).astype(int) # {'Room':'1 X deluxe'} to {'Room':'deluxe','Quantity':1}
    all1['Room Type'] = all1['Room'].str.replace('-.*', '', regex=True) # '3 X DElUXE-NRF' to '3 X DELUXE'
    all1['Room Type'] = all1['Room Type'].apply(lambda x: re.sub(r'^\d+\sX\s', '', x)) #'3 X DElUXE' to 'DELUXE'
    all1['Room Type'] = all1['Room Type'].apply(clean_room_type) #apply with func
    all1['Room Type'] = all1['Room Type'].apply(lambda x: convert_room_type(x))
    all1['F/NRF'] = all1['Room'].apply(lambda x: convert_RF(x))
    all1['RO/ABF'] = all1['Room'].apply(lambda x: convert_ABF(x))
    all1['ADR'] = (all1['Total price']/all1['Length of stay'])/all1['Quantity'] # cal ADR
    all1['ADR'] = all1.apply(lambda row: apply_discount(row['Channel'], row['ADR']), axis=1) #apply function by row
    all1['RN'] = all1['Length of stay']*all1['Quantity']
    all1['ADR'] = all1.apply(calculate_adr_per_rn_abf, axis=1)

    all2 = all1[['Booking reference'
                ,'Guest names'
                ,'Check-in'
                ,'Check-out'
                ,'Channel'
                ,'Booked'
                ,'Total price'
                ,'ADR'
                ,'Length of stay'
                ,'Lead time'
                ,'RN'
                ,'Quantity'
                ,'Room'
                ,'Room Type'
                ,'RO/ABF'
                ,'F/NRF'
                ,'Lead time range'
                ,'Lead time range1'
                ,'LOS range']]
    return all2

# perform data
all3 =  perform(all)
filtered_df = all3
# To find Stay
filtered_df['Stay'] = filtered_df.apply(lambda row: pd.date_range(row['Check-in'], row['Check-out']- pd.Timedelta(days=1)), axis=1)
filtered_df = filtered_df.explode('Stay').reset_index(drop=True)
filtered_df = filtered_df[['Stay','Check-in','Check-out','Booked-on date','Channel','ADR','Length of stay','Lead time','Lead time range','RN','Quantity','Room Type','Room']]

# Sorted Booked like LAST BOOKING
filtered_df =  filtered_df.sort_values(by='Booked-on date')
filtered_df['ADR'] = filtered_df['ADR'].apply('{:.2f}'.format)
filtered_df['ADR'] = filtered_df['ADR'].astype('float')

# find last 40 booking and identify RN
stay_last20_dict = {}

for stay, group in filtered_df.groupby('Stay'):
    last20 = group.tail(40).reset_index(drop=True)
    num_rows = len(last20)
    if num_rows < 40:
        last20['LAST RN'] = list(range(1, num_rows + 1))
    else:
        last20['LAST RN'] = list(range(1, 41))

    last20_bookings = last20[['Stay','Booked-on date', 'ADR', 'Room Type', 'LAST RN']].values.tolist()

    stay_last20_dict[stay] = last20_bookings
# convert to DataFrame
df_stay_last20 = pd.concat([pd.DataFrame(bookings, columns=['Stay','Booked-on date', 'ADR', 'Room Type', 'LAST RN']) for bookings in stay_last20_dict.values()], ignore_index=True)

# Grouping Roomtype
ALL = df_stay_last20
ALL['LAST RN'] = ALL['LAST RN'].astype(int)
ALL['Month'] = pd.to_datetime(ALL['Stay']).dt.month
ALL = ALL.drop(ALL[ALL['Month'] == 5].index)
ALL['Stay'] = ALL['Stay'].astype(str)
mean_by_month_and_rn = ALL.groupby(['Month', 'LAST RN'])['ADR'].mean().reset_index()
mean_by_month_and_rn['ADR'] = mean_by_month_and_rn['ADR'].apply('{:.2f}'.format)
mean_by_month_and_rn['ADR'] = mean_by_month_and_rn['ADR'].astype('float')

ND = df_stay_last20[df_stay_last20['Room Type']== 'NEW DELUXE']
ND['LAST RN'] = ND['LAST RN'].astype(int)
ND['Month'] = pd.to_datetime(ND['Stay']).dt.month
ND = ND.drop(ND[ND['Month'] == 5].index)
ND['Stay'] = ND['Stay'].astype(str)
mean_by_month_and_rn0 = ND.groupby(['Month', 'LAST RN'])['ADR'].mean().reset_index()
mean_by_month_and_rn0['ADR'] = mean_by_month_and_rn0['ADR'].apply('{:.2f}'.format)
mean_by_month_and_rn0['ADR'] = mean_by_month_and_rn0['ADR'].astype('float')


GD = df_stay_last20[df_stay_last20['Room Type']== 'GRAND DELUXE']
GD['LAST RN'] = GD['LAST RN'].astype(int)
GD['Month'] = pd.to_datetime(GD['Stay']).dt.month
GD = GD.drop(GD[GD['Month'] == 5].index)
GD['Stay'] = GD['Stay'].astype(str)
mean_by_month_and_rn1 = GD.groupby(['Month', 'LAST RN'])['ADR'].mean().reset_index()
mean_by_month_and_rn1['ADR'] = mean_by_month_and_rn1['ADR'].apply('{:.2f}'.format)
mean_by_month_and_rn1['ADR'] = mean_by_month_and_rn1['ADR'].astype('float')


NDT = df_stay_last20[df_stay_last20['Room Type']== 'NEW DELUXE TWIN']
NDT['LAST RN'] = NDT['LAST RN'].astype(int)
NDT['Month'] = pd.to_datetime(NDT['Stay']).dt.month
NDT = NDT.drop(NDT[NDT['Month'] == 5].index)
NDT['Stay'] = NDT['Stay'].astype(str)
mean_by_month_and_rn2 = NDT.groupby(['Month', 'LAST RN'])['ADR'].mean().reset_index()
mean_by_month_and_rn2['ADR'] = mean_by_month_and_rn2['ADR'].apply('{:.2f}'.format)
mean_by_month_and_rn2['ADR'] = mean_by_month_and_rn2['ADR'].astype('float')

GC = df_stay_last20[df_stay_last20['Room Type']== 'GRAND CORNER SUITES']
GC['LAST RN'] = GC['LAST RN'].astype(int)
GC['Month'] = pd.to_datetime(GC['Stay']).dt.month
GC = GC.drop(GC[GC['Month'] == 5].index)
GC['Stay'] = GC['Stay'].astype(str)
mean_by_month_and_rn3 = GC.groupby(['Month', 'LAST RN'])['ADR'].mean().reset_index()
mean_by_month_and_rn3['ADR'] = mean_by_month_and_rn3['ADR'].apply('{:.2f}'.format)
mean_by_month_and_rn3['ADR'] = mean_by_month_and_rn3['ADR'].astype('float')

UK = df_stay_last20[df_stay_last20['Room Type']== 'UNKNOWN']
UK['LAST RN'] = UK['LAST RN'].astype(int)
UK['Month'] = pd.to_datetime(UK['Stay']).dt.month
UK = UK.drop(UK[UK['Month'] == 5].index)
UK['Stay'] = UK['Stay'].astype(str)
mean_by_month_and_rn4 = UK.groupby(['Month', 'LAST RN'])['ADR'].mean().reset_index()
mean_by_month_and_rn4['ADR'] = mean_by_month_and_rn4['ADR'].apply('{:.2f}'.format)
mean_by_month_and_rn4['ADR'] = mean_by_month_and_rn4['ADR'].astype('float')

MIXED = df_stay_last20[df_stay_last20['Room Type']== 'MIXED']
MIXED['LAST RN'] = MIXED['LAST RN'].astype(int)
MIXED['Month'] = pd.to_datetime(MIXED['Stay']).dt.month
MIXED = MIXED.drop(MIXED[MIXED['Month'] == 5].index)
MIXED['Stay'] = MIXED['Stay'].astype(str)
mean_by_month_and_rn5 = MIXED.groupby(['Month', 'LAST RN'])['ADR'].mean().reset_index()
mean_by_month_and_rn5['ADR'] = mean_by_month_and_rn5['ADR'].apply('{:.2f}'.format)
mean_by_month_and_rn5['ADR'] = mean_by_month_and_rn5['ADR'].astype('float')

# line plot trend
t1,t2,t3 = st.tabs(['line plot (Acual)','fitted line(40 RN)','fitted line(20 RN)'])
with t1:
  fig = px.line(mean_by_month_and_rn, x='LAST RN', y='ADR',color='Month',text='ADR')
  fig.update_traces(textposition='top center')
  fig.update_layout(title='Plot of ADR by LAST RN  (ALL ROOM TYPE)')
  st.plotly_chart(fig,use_container_width=True)

  C1,C2 = st.columns(2)
  with C1:
    fig1 = px.line(mean_by_month_and_rn0, x='LAST RN', y='ADR',color='Month',text='ADR')
    fig1.update_traces(textposition='top center')
    fig1.update_layout(title='Plot of ADR by LAST RN(NEW DELUXE)')
    st.plotly_chart(fig1,use_container_width=True)
  with C2:
    fig2 = px.line(mean_by_month_and_rn2, x='LAST RN', y='ADR',color='Month',text='ADR')
    fig2.update_traces(textposition='top center')
    fig2.update_layout(title='Plot of ADR by LAST RN(NEW DELUXE TWIN)')
    st.plotly_chart(fig2,use_container_width=True)

  C1,C2 = st.columns(2)
  with C1:
    fig1 = px.line(mean_by_month_and_rn1, x='LAST RN', y='ADR',color='Month',text='ADR')
    fig1.update_traces(textposition='top center')
    fig1.update_layout(title='Plot of ADR by LAST RN(GRAND DELUXE)')
    st.plotly_chart(fig1,use_container_width=True)
  with C2:
    fig2 = px.line(mean_by_month_and_rn3, x='LAST RN', y='ADR',color='Month',text='ADR')
    fig2.update_traces(textposition='top center')
    fig2.update_layout(title='Plot of ADR by LAST RN(GRAND CORNER SUITES)')
    st.plotly_chart(fig2,use_container_width=True)

  C1,C2 = st.columns(2)
  with C1:
    fig1 = px.line(mean_by_month_and_rn4, x='LAST RN', y='ADR',color='Month',text='ADR')
    fig1.update_traces(textposition='top center')
    fig1.update_layout(title='Plot of ADR by LAST RN(UNKNOWN)')
    st.plotly_chart(fig1,use_container_width=True)
  with C2:
    fig2 = px.line(mean_by_month_and_rn5, x='LAST RN', y='ADR',color='Month',text='ADR')
    fig2.update_traces(textposition='top center')
    fig2.update_layout(title='Plot of ADR by LAST RN(MIXED)')
    st.plotly_chart(fig2,use_container_width=True)

with t2:
    NDT = df_stay_last20
    NDT['LAST RN'] = NDT['LAST RN'].astype(int)
    NDT['Month'] = NDT['Stay'].dt.month
    NDT = NDT.drop(NDT[NDT['Month'] == 5].index)
    NDT['Stay'] = NDT['Stay'].astype(str)
    mean_by_month_and_rn = NDT.groupby(['Month', 'LAST RN'])['ADR'].mean().reset_index()
    fig = go.Figure()
    for month in range(1, 5):
        month_data = mean_by_month_and_rn[mean_by_month_and_rn['Month'] == month]
        X = month_data[['LAST RN']]
        y = month_data['ADR']
        model = LinearRegression()
        model.fit(X, y)
        y_pred = model.predict(X)
        fig.add_trace(go.Scatter(x=X['LAST RN'], y=y, mode='markers', name='Month {}'.format(month)))
        fig.add_trace(go.Scatter(x=X['LAST RN'], y=y_pred, mode='lines', name='Best-fit Line (Month {})'.format(month)))
    fig.update_layout(title='Linear Regression (All Room type)', xaxis_title='LAST RN', yaxis_title='ADR')
    st.plotly_chart(fig,use_container_width=True)
    C1,C2 = st.columns(2)
    with C1:
      NDT = df_stay_last20[df_stay_last20['Room Type']== 'NEW DELUXE']
      NDT['LAST RN'] = NDT['LAST RN'].astype(int)
      NDT['Month'] = NDT['Stay'].dt.month
      NDT = NDT.drop(NDT[NDT['Month'] == 5].index)
      NDT['Stay'] = NDT['Stay'].astype(str)
      mean_by_month_and_rn = NDT.groupby(['Month', 'LAST RN'])['ADR'].mean().reset_index()
      fig = go.Figure()
      for month in range(1, 5):
          month_data = mean_by_month_and_rn[mean_by_month_and_rn['Month'] == month]
          X = month_data[['LAST RN']]
          y = month_data['ADR']
          model = LinearRegression()
          model.fit(X, y)
          y_pred = model.predict(X)
          fig.add_trace(go.Scatter(x=X['LAST RN'], y=y, mode='markers', name='Month {}'.format(month)))
          fig.add_trace(go.Scatter(x=X['LAST RN'], y=y_pred, mode='lines', name='Best-fit Line (Month {})'.format(month)))
      fig.update_layout(title='Linear Regression (NEW DELUXE)', xaxis_title='LAST RN', yaxis_title='ADR')
      st.plotly_chart(fig,use_container_width=True)
    with C2:
      NDT = df_stay_last20[df_stay_last20['Room Type']== 'NEW DELUXE TWIN']
      NDT['LAST RN'] = NDT['LAST RN'].astype(int)
      NDT['Month'] = NDT['Stay'].dt.month
      NDT = NDT.drop(NDT[NDT['Month'] == 5].index)
      NDT['Stay'] = NDT['Stay'].astype(str)
      mean_by_month_and_rn = NDT.groupby(['Month', 'LAST RN'])['ADR'].mean().reset_index()
      fig = go.Figure()
      for month in range(1, 5):
          month_data = mean_by_month_and_rn[mean_by_month_and_rn['Month'] == month]
          X = month_data[['LAST RN']]
          y = month_data['ADR']
          model = LinearRegression()
          # To find Trend
          model.fit(X, y)
          y_pred = model.predict(X)
          # and Plot
          fig.add_trace(go.Scatter(x=X['LAST RN'], y=y, mode='markers', name='Month {}'.format(month)))
          fig.add_trace(go.Scatter(x=X['LAST RN'], y=y_pred, mode='lines', name='Best-fit Line (Month {})'.format(month)))
      fig.update_layout(title='Linear Regression (NEW DELUXE TWIN)', xaxis_title='LAST RN', yaxis_title='ADR')
      st.plotly_chart(fig,use_container_width=True)

    C1,C2 = st.columns(2)
    with C1:
      NDT = df_stay_last20[df_stay_last20['Room Type']== 'GRAND DELUXE']
      NDT['LAST RN'] = NDT['LAST RN'].astype(int)
      NDT['Month'] = NDT['Stay'].dt.month
      NDT = NDT.drop(NDT[NDT['Month'] == 5].index)
      NDT['Stay'] = NDT['Stay'].astype(str)
      mean_by_month_and_rn = NDT.groupby(['Month', 'LAST RN'])['ADR'].mean().reset_index()
      fig = go.Figure()
      for month in range(1, 5):
          month_data = mean_by_month_and_rn[mean_by_month_and_rn['Month'] == month]
          X = month_data[['LAST RN']]
          y = month_data['ADR']
          model = LinearRegression()
          model.fit(X, y)
          y_pred = model.predict(X)
          fig.add_trace(go.Scatter(x=X['LAST RN'], y=y, mode='markers', name='Month {}'.format(month)))
          fig.add_trace(go.Scatter(x=X['LAST RN'], y=y_pred, mode='lines', name='Best-fit Line (Month {})'.format(month)))
      fig.update_layout(title='Linear Regression (GRAND DELUXE)', xaxis_title='LAST RN', yaxis_title='ADR')
      st.plotly_chart(fig,use_container_width=True)
    with C2:
      NDT = df_stay_last20[df_stay_last20['Room Type']== 'GRAND CORNER SUITES']
      NDT['LAST RN'] = NDT['LAST RN'].astype(int)
      NDT['Month'] = NDT['Stay'].dt.month
      NDT = NDT.drop(NDT[NDT['Month'] == 5].index)
      NDT['Stay'] = NDT['Stay'].astype(str)
      mean_by_month_and_rn = NDT.groupby(['Month', 'LAST RN'])['ADR'].mean().reset_index()
      fig = go.Figure()
      for month in range(1, 5):
          month_data = mean_by_month_and_rn[mean_by_month_and_rn['Month'] == month]
          X = month_data[['LAST RN']]
          y = month_data['ADR']
          model = LinearRegression()
          model.fit(X, y)
          y_pred = model.predict(X)
          fig.add_trace(go.Scatter(x=X['LAST RN'], y=y, mode='markers', name='Month {}'.format(month)))
          fig.add_trace(go.Scatter(x=X['LAST RN'], y=y_pred, mode='lines', name='Best-fit Line (Month {})'.format(month)))
      fig.update_layout(title='Linear Regression (GRAND CORNER SUITES)', xaxis_title='LAST RN', yaxis_title='ADR')
      st.plotly_chart(fig,use_container_width=True)

    C1,C2 = st.columns(2)
    with C1:
      NDT = df_stay_last20[df_stay_last20['Room Type']== 'UNKNOWN']
      NDT['LAST RN'] = NDT['LAST RN'].astype(int)
      NDT['Month'] = NDT['Stay'].dt.month
      NDT = NDT.drop(NDT[NDT['Month'] == 5].index)
      NDT['Stay'] = NDT['Stay'].astype(str)
      mean_by_month_and_rn = NDT.groupby(['Month', 'LAST RN'])['ADR'].mean().reset_index()
      fig = go.Figure()
      for month in range(1, 5):
          month_data = mean_by_month_and_rn[mean_by_month_and_rn['Month'] == month]
          X = month_data[['LAST RN']]
          y = month_data['ADR']
          model = LinearRegression()
          model.fit(X, y)
          y_pred = model.predict(X)
          fig.add_trace(go.Scatter(x=X['LAST RN'], y=y, mode='markers', name='Month {}'.format(month)))
          fig.add_trace(go.Scatter(x=X['LAST RN'], y=y_pred, mode='lines', name='Best-fit Line (Month {})'.format(month)))
      fig.update_layout(title='Linear Regression (UNKNOWN)', xaxis_title='LAST RN', yaxis_title='ADR')
      st.plotly_chart(fig,use_container_width=True)
    with C2:
      NDT = df_stay_last20[df_stay_last20['Room Type']== 'MIXED']
      NDT['LAST RN'] = NDT['LAST RN'].astype(int)
      NDT['Month'] = NDT['Stay'].dt.month
      NDT = NDT.drop(NDT[NDT['Month'] == 5].index)
      NDT['Stay'] = NDT['Stay'].astype(str)
      mean_by_month_and_rn = NDT.groupby(['Month', 'LAST RN'])['ADR'].mean().reset_index()
      fig = go.Figure()
      for month in range(1, 5):
          month_data = mean_by_month_and_rn[mean_by_month_and_rn['Month'] == month]
          X = month_data[['LAST RN']]
          y = month_data['ADR']
          model = LinearRegression()
          model.fit(X, y)
          y_pred = model.predict(X)
          fig.add_trace(go.Scatter(x=X['LAST RN'], y=y, mode='markers', name='Month {}'.format(month)))
          fig.add_trace(go.Scatter(x=X['LAST RN'], y=y_pred, mode='lines', name='Best-fit Line (Month {})'.format(month)))
      fig.update_layout(title='Linear Regression (MIXED)', xaxis_title='LAST RN', yaxis_title='ADR')
      st.plotly_chart(fig,use_container_width=True)

with t3:
    for stay, group in filtered_df.groupby('Stay'):
        last20 = group.tail(20).reset_index(drop=True)
        num_rows = len(last20)
        if num_rows < 20:
            last20['LAST RN'] = list(range(1, num_rows + 1))
        else:
            last20['LAST RN'] = list(range(1, 21))

        last20_bookings = last20[['Stay','Booked-on date', 'ADR', 'Room Type', 'LAST RN']].values.tolist()

        stay_last20_dict[stay] = last20_bookings

    df_stay_last20 = pd.concat([pd.DataFrame(bookings, columns=['Stay','Booked-on date', 'ADR', 'Room Type', 'LAST RN']) for bookings in stay_last20_dict.values()], ignore_index=True)
    NDT = df_stay_last20
    NDT['LAST RN'] = NDT['LAST RN'].astype(int)
    NDT['Month'] = NDT['Stay'].dt.month
    NDT = NDT.drop(NDT[NDT['Month'] == 5].index)
    NDT['Stay'] = NDT['Stay'].astype(str)
    mean_by_month_and_rn = NDT.groupby(['Month', 'LAST RN'])['ADR'].mean().reset_index()
    fig = go.Figure()
    for month in range(1, 5):
        month_data = mean_by_month_and_rn[mean_by_month_and_rn['Month'] == month]
        X = month_data[['LAST RN']]
        y = month_data['ADR']
        model = LinearRegression()
        model.fit(X, y)
        y_pred = model.predict(X)
        fig.add_trace(go.Scatter(x=X['LAST RN'], y=y, mode='markers', name='Month {}'.format(month)))
        fig.add_trace(go.Scatter(x=X['LAST RN'], y=y_pred, mode='lines', name='Best-fit Line (Month {})'.format(month)))
    fig.update_layout(title='Linear Regression (All Room type)', xaxis_title='LAST RN', yaxis_title='ADR')
    st.plotly_chart(fig,use_container_width=True)
    C1,C2 = st.columns(2)
    with C1:
      NDT = df_stay_last20[df_stay_last20['Room Type']== 'NEW DELUXE']
      NDT['LAST RN'] = NDT['LAST RN'].astype(int)
      NDT['Month'] = NDT['Stay'].dt.month
      NDT = NDT.drop(NDT[NDT['Month'] == 5].index)
      NDT['Stay'] = NDT['Stay'].astype(str)
      mean_by_month_and_rn = NDT.groupby(['Month', 'LAST RN'])['ADR'].mean().reset_index()
      fig = go.Figure()
      for month in range(1, 5):
          month_data = mean_by_month_and_rn[mean_by_month_and_rn['Month'] == month]
          X = month_data[['LAST RN']]
          y = month_data['ADR']
          model = LinearRegression()
          model.fit(X, y)
          y_pred = model.predict(X)
          fig.add_trace(go.Scatter(x=X['LAST RN'], y=y, mode='markers', name='Month {}'.format(month)))
          fig.add_trace(go.Scatter(x=X['LAST RN'], y=y_pred, mode='lines', name='Best-fit Line (Month {})'.format(month)))
      fig.update_layout(title='Linear Regression (NEW DELUXE)', xaxis_title='LAST RN', yaxis_title='ADR')
      st.plotly_chart(fig,use_container_width=True)
    with C2:
      NDT = df_stay_last20[df_stay_last20['Room Type']== 'NEW DELUXE TWIN']
      NDT['LAST RN'] = NDT['LAST RN'].astype(int)
      NDT['Month'] = NDT['Stay'].dt.month
      NDT = NDT.drop(NDT[NDT['Month'] == 5].index)
      NDT['Stay'] = NDT['Stay'].astype(str)
      mean_by_month_and_rn = NDT.groupby(['Month', 'LAST RN'])['ADR'].mean().reset_index()
      fig = go.Figure()
      for month in range(1, 5):
          month_data = mean_by_month_and_rn[mean_by_month_and_rn['Month'] == month]
          X = month_data[['LAST RN']]
          y = month_data['ADR']
          model = LinearRegression()
          model.fit(X, y)
          y_pred = model.predict(X)
          fig.add_trace(go.Scatter(x=X['LAST RN'], y=y, mode='markers', name='Month {}'.format(month)))
          fig.add_trace(go.Scatter(x=X['LAST RN'], y=y_pred, mode='lines', name='Best-fit Line (Month {})'.format(month)))
      fig.update_layout(title='Linear Regression (NEW DELUXE TWIN)', xaxis_title='LAST RN', yaxis_title='ADR')
      st.plotly_chart(fig,use_container_width=True)

    C1,C2 = st.columns(2)
    with C1:
      NDT = df_stay_last20[df_stay_last20['Room Type']== 'GRAND DELUXE']
      NDT['LAST RN'] = NDT['LAST RN'].astype(int)
      NDT['Month'] = NDT['Stay'].dt.month
      NDT = NDT.drop(NDT[NDT['Month'] == 5].index)
      NDT['Stay'] = NDT['Stay'].astype(str)
      mean_by_month_and_rn = NDT.groupby(['Month', 'LAST RN'])['ADR'].mean().reset_index()
      fig = go.Figure()
      for month in range(1, 5):
          month_data = mean_by_month_and_rn[mean_by_month_and_rn['Month'] == month]
          X = month_data[['LAST RN']]
          y = month_data['ADR']
          model = LinearRegression()
          model.fit(X, y)
          y_pred = model.predict(X)
          fig.add_trace(go.Scatter(x=X['LAST RN'], y=y, mode='markers', name='Month {}'.format(month)))
          fig.add_trace(go.Scatter(x=X['LAST RN'], y=y_pred, mode='lines', name='Best-fit Line (Month {})'.format(month)))
      fig.update_layout(title='Linear Regression (GRAND DELUXE)', xaxis_title='LAST RN', yaxis_title='ADR')
      st.plotly_chart(fig,use_container_width=True)
    with C2:
      NDT = df_stay_last20[df_stay_last20['Room Type']== 'GRAND CORNER SUITES']
      NDT['LAST RN'] = NDT['LAST RN'].astype(int)
      NDT['Month'] = NDT['Stay'].dt.month
      NDT = NDT.drop(NDT[NDT['Month'] == 5].index)
      NDT['Stay'] = NDT['Stay'].astype(str)
      mean_by_month_and_rn = NDT.groupby(['Month', 'LAST RN'])['ADR'].mean().reset_index()
      fig = go.Figure()
      for month in range(1, 5):
          month_data = mean_by_month_and_rn[mean_by_month_and_rn['Month'] == month]
          X = month_data[['LAST RN']]
          y = month_data['ADR']
          model = LinearRegression()
          model.fit(X, y)
          y_pred = model.predict(X)
          fig.add_trace(go.Scatter(x=X['LAST RN'], y=y, mode='markers', name='Month {}'.format(month)))
          fig.add_trace(go.Scatter(x=X['LAST RN'], y=y_pred, mode='lines', name='Best-fit Line (Month {})'.format(month)))
      fig.update_layout(title='Linear Regression (GRAND CORNER SUITES)', xaxis_title='LAST RN', yaxis_title='ADR')
      st.plotly_chart(fig,use_container_width=True)

    C1,C2 = st.columns(2)
    with C1:
      NDT = df_stay_last20[df_stay_last20['Room Type']== 'UNKNOWN']
      NDT['LAST RN'] = NDT['LAST RN'].astype(int)
      NDT['Month'] = NDT['Stay'].dt.month
      NDT = NDT.drop(NDT[NDT['Month'] == 5].index)
      NDT['Stay'] = NDT['Stay'].astype(str)
      mean_by_month_and_rn = NDT.groupby(['Month', 'LAST RN'])['ADR'].mean().reset_index()
      fig = go.Figure()
      for month in range(1, 5):
          month_data = mean_by_month_and_rn[mean_by_month_and_rn['Month'] == month]
          X = month_data[['LAST RN']]
          y = month_data['ADR']
          model = LinearRegression()
          model.fit(X, y)
          y_pred = model.predict(X)
          fig.add_trace(go.Scatter(x=X['LAST RN'], y=y, mode='markers', name='Month {}'.format(month)))
          fig.add_trace(go.Scatter(x=X['LAST RN'], y=y_pred, mode='lines', name='Best-fit Line (Month {})'.format(month)))
      fig.update_layout(title='Linear Regression (UNKNOWN)', xaxis_title='LAST RN', yaxis_title='ADR')
      st.plotly_chart(fig,use_container_width=True)
    with C2:
        try:
          NDT = df_stay_last20[df_stay_last20['Room Type']== 'MIXED']
          NDT['LAST RN'] = NDT['LAST RN'].astype(int)
          NDT['Month'] = NDT['Stay'].dt.month
          NDT = NDT.drop(NDT[NDT['Month'] == 5].index)
          NDT['Stay'] = NDT['Stay'].astype(str)
          mean_by_month_and_rn = NDT.groupby(['Month', 'LAST RN'])['ADR'].mean().reset_index()
          fig = go.Figure()
          for month in range(1, 5):
              month_data = mean_by_month_and_rn[mean_by_month_and_rn['Month'] == month]
              X = month_data[['LAST RN']]
              y = month_data['ADR']
              model = LinearRegression()
              model.fit(X, y)
              y_pred = model.predict(X)
              fig.add_trace(go.Scatter(x=X['LAST RN'], y=y, mode='markers', name='Month {}'.format(month)))
              fig.add_trace(go.Scatter(x=X['LAST RN'], y=y_pred, mode='lines', name='Best-fit Line (Month {})'.format(month)))
          fig.update_layout(title='Linear Regression (MIXED)', xaxis_title='LAST RN', yaxis_title='ADR')
          st.plotly_chart(fig,use_container_width=True)
        except Exception as none:
              st.write("")
