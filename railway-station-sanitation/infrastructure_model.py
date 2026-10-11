from dataclasses import dataclass
from math import ceil

@dataclass
class Inputs:
    trains_day:int=20
    passengers_train:int=1000
    station_use:float=.25
    urinal_share:float=.375
    urinal_l:float=2.0
    wc_l:float=6.0
    handwash_l:float=1.5
    cleaning_kl:float=3.0
    sewage_fraction:float=.90
    demand_growth:float=.20
    storage_days:float=1.25
    glr_share:float=.73
    pumping_hours:int=8
    pump_head_m:int=25
    stp_utilization:float=.8
    reuse_fraction:float=.6
    pump_efficiency:float=.6
    capex_civil_lakh:float=90
    capex_fixtures_lakh:float=23
    capex_plumbing_lakh:float=18
    capex_electrical_lakh:float=9
    capex_misc_lakh:float=20
    capex_tanks_lakh:float=12
    capex_pumps_lakh:float=5
    capex_stp_lakh:float=65
    capex_stp_civil_lakh:float=12
    capex_controls_lakh:float=11
    cleaners:int=18
    supervisors:int=4
    cleaner_monthly:float=30000
    supervisor_monthly:float=40000
    annual_other_opex_lakh:float=36
    electricity_rate:float=9.0

def calculate(x:Inputs):
    visits=x.trains_day*x.passengers_train*x.station_use
    urinal=visits*x.urinal_share
    wc=visits-urinal
    water_kl=(urinal*x.urinal_l+wc*x.wc_l+visits*x.handwash_l)/1000+x.cleaning_kl
    sewage_kl=water_kl*x.sewage_fraction
    design_water=water_kl*(1+x.demand_growth)
    storage=design_water*x.storage_days
    glr=storage*x.glr_share
    oht=storage-glr
    pump_m3_hour=design_water/max(x.pumping_hours,1)
    pump_kw=(1000*9.81*(pump_m3_hour/3600)*x.pump_head_m)/(1000*max(x.pump_efficiency,.1))
    stp_kld=sewage_kl*(1+x.demand_growth)/max(x.stp_utilization,.1)
    equalization_kl=sewage_kl*0.4
    reuse_kl=sewage_kl*x.reuse_fraction
    capex_lakh=sum((x.capex_civil_lakh,x.capex_fixtures_lakh,x.capex_plumbing_lakh,x.capex_electrical_lakh,x.capex_misc_lakh,x.capex_tanks_lakh,x.capex_pumps_lakh,x.capex_stp_lakh,x.capex_stp_civil_lakh,x.capex_controls_lakh))
    staff_annual_lakh=12*(x.cleaners*x.cleaner_monthly+x.supervisors*x.supervisor_monthly)/100000
    pump_electric_annual_lakh=pump_kw*x.pumping_hours*365*x.electricity_rate/100000
    annual_opex_lakh=staff_annual_lakh+x.annual_other_opex_lakh+pump_electric_annual_lakh
    return {
        'Toilet visits/day':round(visits),
        'Water requirement kL/day':round(water_kl,2),
        'Sewage kL/day':round(sewage_kl,2),
        'Design water incl reserve kL/day':round(design_water,2),
        'Combined water storage kL':round(storage,2),
        'GLR kL':round(glr,2),
        'OHT kL':round(oht,2),
        'Pump capacity m3/hour':round(pump_m3_hour,2),
        'Hydraulic pump power kW':round(pump_kw,2),
        'STP rated capacity KLD':ceil(stp_kld),
        'Equalization tank kL':round(equalization_kl,2),
        'Potential reclaimed water kL/day':round(reuse_kl,2),
        'Total capital expenditure lakh INR':round(capex_lakh,2),
        'Annual operational expenditure lakh INR':round(annual_opex_lakh,2),
        'Cleaners':x.cleaners,
        'Supervisors':x.supervisors,
    }
