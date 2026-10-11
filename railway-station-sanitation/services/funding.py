from dataclasses import dataclass
from .infrastructure import Inputs, calculate

@dataclass
class Funding:
    annual_boardings: int = 7300000
    existing_fare_allocation_rs: float = 0
    incremental_fare_rs: float = 0
    annual_nonfare_lakh: float = 0
    support_grant_lakh: float = 0
    discount: float = .08
    years: int = 15

def evaluate(f: Funding, infrastructure: Inputs):
    c=calculate(infrastructure)
    crf=f.discount/(1-(1+f.discount)**(-f.years)) if f.discount else 1/f.years
    annual_capital=c['capex_lakh']*crf
    annual_cost=c['opex_lakh_year']+annual_capital
    existing=f.annual_boardings*f.existing_fare_allocation_rs/100000
    surcharge=f.annual_boardings*f.incremental_fare_rs/100000
    funds=existing+surcharge+f.annual_nonfare_lakh+f.support_grant_lakh
    return dict(annualized_capex_lakh=round(annual_capital,2),
        annual_cost_lakh=round(annual_cost,2),
        unit_cost_rs_per_boarding=round(annual_cost*100000/max(1,f.annual_boardings),2),
        existing_fare_allocation_lakh=round(existing,2),
        incremental_fare_lakh=round(surcharge,2),
        total_allocated_funds_lakh=round(funds,2),
        budget_surplus_lakh=round(funds-annual_cost,2))
