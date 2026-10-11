import streamlit as st
import pandas as pd
from infrastructure_model import Inputs, calculate
from services.funding import Funding, evaluate as fund
from services.story import CHAPTERS

st.set_page_config(page_title="AI Policy Laboratory | Railway Sanitation",layout="wide")
st.title("Should the railway ticket include a clean toilet?")
st.caption("Senior-management teaching simulator. Planning costs and demand responses are assumptions, not calibrated evidence.")
with st.sidebar:
    st.header("Scenario")
    t=st.slider("Trains/day",5,100,20)
    p=st.slider("Boarding passengers/train",250,2500,1000,50)
    use=st.slider("Potential station toilet use %",5,60,25)
    wc=st.slider("WC user charge Rs",0,20,5)
    response=st.slider("Tariff demand response", -1.5,0.0,-.25,.05)
    fare_existing=st.slider("Existing fare allocation per boarding Rs",0.,10.,2.2,.1)
    fare_extra=st.slider("Proposed additional fare Rs",0.,10.,0.,.1)
    other=st.slider("Annual other funding lakh Rs",0.,200.,0.,5.)
    autonomy=st.slider("Water storage days",.5,3.,1.25,.25)
    cleaners=st.slider("Number of cleaners",6,40,18)
x=Inputs(trains_day=t,passengers_train=p,station_use=use/100,storage_days=autonomy,cleaners=cleaners)
r=calculate(x)
f=fund(Funding(annual_boardings=t*p*365,existing_fare_allocation_rs=fare_existing,incremental_fare_rs=fare_extra,annual_nonfare_lakh=other),x)
tabs=st.tabs(["Lecture story","Fare entitlement","Fee versus use","Water, STP and CAPEX","Operating manpower"])
with tabs[0]:
    i=st.slider("Story chapter",1,len(CHAPTERS),1)
    st.header(CHAPTERS[i-1][0]);st.write(CHAPTERS[i-1][1])
    st.progress(i/len(CHAPTERS))
    st.info("Policy question → model → assumptions → sensitivity → field experiment → decision.")
with tabs[1]:
    a,b,c=st.columns(3)
    a.metric("Annual economic cost Rs lakh",f["annual_cost_lakh"])
    b.metric("Cost per boarding Rs",f["unit_cost_rs_per_boarding"])
    c.metric("Available budget less cost Rs lakh",f["budget_surplus_lakh"])
    st.dataframe(pd.DataFrame([{"Metric":k,"Value":v} for k,v in f.items()]),hide_index=True,use_container_width=True)
    st.info("Existing fare allocation is NOT a proposed fare increase. A surcharge is a distinct policy requiring approval.")
with tabs[2]:
    visits=t*p*use/100
    wc_potential=visits*(1-x.urinal_share)
    realized=wc_potential*(1+wc/5)**response
    lost=wc_potential-realized
    receipts=realized*wc*.90*365/100000
    st.metric("Discouraged station WC visits/day",round(lost))
    st.metric("Illustrative gross charge receipts lakh/year",round(receipts,2))
    st.metric("Assumed extra onboard visits/day if 30% diversion",round(lost*.3))
    rows=[]
    for charge in (0,2,5,10,15,20):
        q=wc_potential*(1+charge/5)**response
        rows.append({"Tariff Rs":str(charge),"WC visits/day":round(q),"Gross receipts lakh/year":round(q*charge*.90*365/100000,2)})
    st.dataframe(pd.DataFrame(rows),hide_index=True,use_container_width=True)
    st.warning("Payments are transfers, not social gains. The behavioral response here is not field calibrated.")
with tabs[3]:
    st.dataframe(pd.DataFrame([{"Measure":k,"Estimate":round(v,2) if isinstance(v,(float,int)) else v} for k,v in r.items()]),hide_index=True,use_container_width=True)
    st.caption("GLR, OHT, STP, power and wastewater sizes are planning proxies. Obtain engineering BOQs.")
with tabs[4]:
    st.metric("Cleaner posts",cleaners)
    st.metric("Annual OPEX lakh/year",r["opex_lakh_year"])
    st.write("Provide 24-hour shift coverage, weekly-off relief, peak-event reinforcement and cleanliness checks.")
st.download_button("Download scenario CSV",pd.DataFrame([r|f]).to_csv(index=False).encode(),file_name="scenario.csv")
