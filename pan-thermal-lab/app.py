import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from simulator import Params,MATERIALS,simulate
st.set_page_config(page_title="Pan Thermal Design Lab",layout="wide")
st.title("Pan thermal design laboratory")
st.caption("Illustrative axisymmetric finite-volume simulation, not a validated gas-appliance design.")
with st.sidebar:
    st.header("Pan")
    radius=st.slider("Cooking base radius (cm)",6.,18.,11.,.5)
    thickness=st.slider("Base thickness (mm)",1.,10.,4.,.5)
    material=st.selectbox("Material",list(MATERIALS))
    oil=st.slider("Oil film thickness (mm)",.1,3.,.6,.1)
    wet=st.slider("Oil-covered fraction",.1,1.,1.,.05)
    st.header("Burner and environment")
    power=st.slider("Gas input (W)",300,4000,1500,100)
    coupling=st.slider("Assumed gas-to-pan coupling",.1,.85,.42,.01)
    ring=st.slider("Ring radius (cm)",0.,15.,6.,.5)
    width=st.slider("Heat footprint FWHM (cm)",1.,12.,3.,.5)
    top=st.slider("Top convection (W/m²K)",5.,100.,35.,5.)
    bottom=st.slider("Bottom convection (W/m²K)",0.,60.,10.,2.)
    edge=st.slider("Edge convection (W/m²K)",0.,60.,15.,2.)
    load=st.slider("Cooking sink (W/m²)",0,7000,1500,250)
    emis=st.slider("Emissivity",.05,.95,.45,.05)
    ambient=st.slider("Ambient temperature (°C)",10,45,25)
    duration=st.slider("Heating duration (s)",30,900,240,30)
p=Params(radius_cm=radius,thickness_mm=thickness,material=material,burner_radius_cm=ring,burner_width_cm=width,burner_power_W=power,coupling_efficiency=coupling,top_h_W_m2K=top,bottom_h_W_m2K=bottom,edge_h_W_m2K=edge,cooking_load_W_m2=load,emissivity=emis,ambient_C=ambient,oil_depth_mm=oil,oil_fraction=wet,duration_s=duration)
x=simulate(p)
a,b,c,d=st.columns(4)
a.metric("Oil-volume proxy",f"{x['oil_ml']:.1f} mL")
b.metric("Peak pan temperature",f"{x['peak_temperature_C']:.1f} °C")
c.metric("Radial temperature spread",f"{x['temperature_spread_C']:.1f} °C")
d.metric("Gas energy input",f"{x['gas_energy_kJ']:.0f} kJ")
left,right=st.columns(2)
with left:
    fig=go.Figure()
    for tt,vals in zip(x["profiles_t_s"],x["profiles_C"]):
        fig.add_trace(go.Scatter(x=x["r_cm"],y=vals,name=f"{tt:.0f}s"))
    fig.update_layout(title="Temperature gradient over time",xaxis_title="Radius (cm)",yaxis_title="Temperature (°C)")
    st.plotly_chart(fig,use_container_width=True)
with right:
    grid=np.linspace(-radius,radius,151)
    xx,yy=np.meshgrid(grid,grid)
    rr=np.sqrt(xx**2+yy**2)
    zz=np.interp(rr,x["r_cm"],x["T_C"])
    zz[rr>radius]=np.nan
    fig=go.Figure(data=go.Heatmap(x=grid,y=grid,z=zz,colorscale="Inferno",colorbar={"title":"°C"}))
    fig.update_layout(title="Axisymmetric plan-view temperature field",xaxis_title="x (cm)",yaxis_title="y (cm)",yaxis_scaleanchor="x")
    st.plotly_chart(fig,use_container_width=True)
st.subheader("Sweep: burner-ring radius")
rows=[]
for v in np.linspace(0,min(radius,ring+5),13):
    pp=Params(**{**p.__dict__,"burner_radius_cm":float(v)})
    out=simulate(pp)
    rows.append({"Ring radius (cm)":v,"Temperature spread (°C)":out["temperature_spread_C"],"Mean temperature (°C)":out["mean_temperature_C"]})
df=pd.DataFrame(rows)
st.line_chart(df.set_index("Ring radius (cm)"))
st.download_button("Download sweep CSV",df.to_csv(index=False),"pan_burner_sweep.csv","text/csv")
st.info("Heat coupling is specified, not predicted. The model omits combustion CFD, pan curvature, oil hydrodynamics and detailed food contact.")
