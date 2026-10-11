"""Axisymmetric thin-plate thermal model; exploratory, not burner certification."""
from dataclasses import dataclass, asdict
import numpy as np
MATERIALS={'Aluminium':(205.,2700.,900.),'Cast iron':(52.,7200.,460.),'Carbon steel':(48.,7850.,490.),'Stainless steel':(16.,8000.,500.),'Copper':(390.,8960.,385.)}
@dataclass
class Params:
    radius_cm:float=11
    thickness_mm:float=4
    material:str='Aluminium'
    burner_radius_cm:float=6
    burner_width_cm:float=3
    burner_power_W:float=1500
    coupling_efficiency:float=.42
    top_h_W_m2K:float=35
    bottom_h_W_m2K:float=10
    edge_h_W_m2K:float=15
    ambient_C:float=25
    oil_depth_mm:float=.6
    oil_fraction:float=1.0
    cooking_load_W_m2:float=1500
    emissivity:float=.45
    duration_s:float=240
    segments:int=100

def simulate(p:Params):
    if p.radius_cm<=0 or p.thickness_mm<=0 or p.burner_power_W<0 or not 0<=p.coupling_efficiency<=1: raise ValueError('Invalid geometry or power')
    k,rho,cp=MATERIALS[p.material]; R=p.radius_cm/100;t=p.thickness_mm/1000;N=int(p.segments); dr=R/N
    r=(np.arange(N)+.5)*dr
    area=np.pi*((np.arange(1,N+1)*dr)**2-(np.arange(N)*dr)**2)
    cap=area*t*rho*cp
    band=np.exp(-.5*((r-p.burner_radius_cm/100)/max(.001,p.burner_width_cm/100/2.355))**2)
    source=p.burner_power_W*p.coupling_efficiency*band/np.sum(band*area)*area
    sigma=5.670374419e-8
    T=np.full(N,p.ambient_C,dtype=float)
    frames=[];frames_t=[]
    dt=min(.15,.3*rho*cp*dr**2/max(k,1e-9))
    total=max(0,p.duration_s);steps=max(1,int(np.ceil(total/dt)));dt=total/steps if total else 0
    snapshots=set(np.unique(np.linspace(0,steps,6,dtype=int)))
    if 0 in snapshots:frames.append(T.copy());frames_t.append(0.)
    for s in range(1,steps+1):
        flux=np.zeros(N+1)
        interface_r=np.arange(1,N)*dr
        flux[1:N]=k*t*2*np.pi*interface_r*(T[1:]-T[:-1])/dr
        conv=(p.top_h_W_m2K+p.bottom_h_W_m2K)*area*(T-p.ambient_C)
        rad=p.emissivity*sigma*area*((T+273.15)**4-(p.ambient_C+273.15)**4)
        load=p.cooking_load_W_m2*area*(T>p.ambient_C+2)
        edge=np.zeros(N);edge[-1]=p.edge_h_W_m2K*2*np.pi*R*t*(T[-1]-p.ambient_C)
        T+=dt*(source+flux[1:]-flux[:-1]-conv-rad-load-edge)/cap
        if s in snapshots:frames.append(T.copy());frames_t.append(s*dt)
    oil_ml=np.pi*R**2*p.oil_depth_mm/1000*1e6*p.oil_fraction
    return {'r_cm':r*100,'T_C':T,'profiles_C':np.array(frames),'profiles_t_s':np.array(frames_t),'oil_ml':oil_ml,'gas_energy_kJ':p.burner_power_W*total/1000,'coupled_energy_kJ':p.burner_power_W*p.coupling_efficiency*total/1000,'temperature_spread_C':float(T.max()-T.min()),'mean_temperature_C':float(np.sum(T*area)/sum(area)),'peak_temperature_C':float(T.max()),'params':asdict(p)}
