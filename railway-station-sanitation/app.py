import streamlit as st
import pandas as pd
from infrastructure_model import Inputs, calculate
st.set_page_config(page_title='Railway Station Sanitation | Integrated Utilities', layout='wide')
st.title('Railway Station Sanitation: Toilets, Water, Pumps, STP and Costs')
st.caption('Planning-level sensitivity model; not a tender estimate.')
x=Inputs()
with st.sidebar:
    st.header('Passenger demand')
    x.trains_day=st.slider('Trains/day',5,80,x.trains_day)
    x.passengers_train=st.slider('Boarding passengers/train',250,2500,x.passengers_train,50)
    x.station_use=st.slider('Station toilet use (%)',5,60,int(x.station_use*100))/100
    x.urinal_share=st.slider('Urinal share (%)',10,60,int(x.urinal_share*100))/100
    st.header('Water and sewage')
    x.urinal_l=st.number_input('Urinal flush L',0.,10.,float(x.urinal_l))
    x.wc_l=st.number_input('WC flush L',1.,15.,float(x.wc_l))
    x.handwash_l=st.number_input('Handwash L',0.,10.,float(x.handwash_l))
    x.cleaning_kl=st.number_input('Cleaning kL/day',0.,20.,float(x.cleaning_kl))
    x.demand_growth=st.slider('Reserve (%)',0,60,int(x.demand_growth*100))/100
    x.storage_days=st.slider('Storage autonomy days',.5,3.,float(x.storage_days),.25)
    x.glr_share=st.slider('GLR storage fraction (%)',30,100,int(x.glr_share*100))/100
    x.pumping_hours=st.slider('Pumping hours/day',2,24,int(x.pumping_hours))
    x.pump_head_m=st.slider('Total pump head m',10,60,int(x.pump_head_m))
    x.stp_utilization=st.slider('STP target use (%)',50,100,int(x.stp_utilization*100))/100
    x.reuse_fraction=st.slider('Treated effluent recovery (%)',0,90,int(x.reuse_fraction*100))/100
r=calculate(x)
st.subheader('Infrastructure sizing and cost')
st.dataframe(pd.DataFrame([{'Metric':k,'Value':v} for k,v in r.items()]),hide_index=True,use_container_width=True)
st.info('Validate demand, hydraulic head, equalization volume, STP technology, labour obligations and costs against local railway specifications.')
