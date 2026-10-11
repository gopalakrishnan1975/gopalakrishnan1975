"""Scenario-oriented simulation wrapper for the infrastructure model."""
from infrastructure_model import Inputs, calculate

def run_scenarios(station_use_rates=(.15,.25,.40),trains_day=20,passengers_train=1000):
    scenarios=[]
    for rate in station_use_rates:
        x=Inputs(trains_day=trains_day,passengers_train=passengers_train,station_use=rate)
        scenarios.append({'station_use_rate':rate,**calculate(x)})
    return scenarios

if __name__=='__main__':
    import json
    print(json.dumps(run_scenarios(),indent=2))
