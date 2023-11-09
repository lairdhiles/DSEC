import pandas as pd
import numpy as np

from fin_lib import build_rate_model

def load_sod_data(index):
    return pd.read_csv(f"{index.lower()}_data.csv",index_col=0)

def load_live_data(index):
    live_data = pd.read_csv(f"{index.lower()}_data.csv",index_col=0)
    futures = live_data[live_data["type"]=="future"]["rate"]
    swaps = live_data[live_data["type"]=="swap"]["rate"]
    futures_moves = np.random.normal(loc=0.0, scale=1.0, size=futures.shape[0])*1.5*np.sqrt(1/360)/10000
    swap_moves = np.random.normal(loc=0.0, scale=1.0, size=swaps.shape[0])*1.2*np.sqrt(1/360)/10000
    live_data.loc[live_data["type"]=="future", "rate"] = futures+futures_moves
    live_data.loc[live_data["type"]=="swap", "rate"] = swaps+swap_moves
    return live_data

def mkt_moves(live_data,sod_data):
    return (live_data["rate"]-sod_data["rate"])*10000
    
def load_curve_from_data(calc_date, data, index, risk=False):
    deposits = data[data["type"]=="deposit"]["rate"]
    futures = data[data["type"]=="future"]["rate"]
    swaps = data[data["type"]=="swap"]["rate"]
    return build_rate_model(calc_date, deposits, futures, swaps, index, risk)
    
    
    