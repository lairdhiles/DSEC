import pandas as pd
import numbers
import QuantLib as ql
from fin_lib import delta_ladder

from mkt_data import mkt_moves

def load_risk(index):
    return pd.read_csv(f"{index.lower()}_risk.csv",index_col=0)

def pnl(live_data, sod_data, risk):
    return mkt_moves(live_data,sod_data).values*risk.values.flatten()

def update_risk(instrument, curve, quotes, index):
    risk_ladder = delta_ladder(instrument, curve, quotes)
    current_risk = load_risk(index)+risk_ladder
    current_risk.to_csv(f"{index}_data.csv")    
    

def book_swap(index, notional, direction, start_date,end_date,curve,quotes,fixed_rate,floating_leg_tenor,fixed_leg_tenor,float_leg_daycount,fixed_leg_daycount,calendar):
    
    # notional = 10000000000
    fixed_schedule = ql.Schedule(start_date, end_date, fixed_leg_tenor, calendar,
                                ql.ModifiedFollowing, ql.ModifiedFollowing, ql.DateGeneration.Forward, False)
    # float_schedule = ql.Schedule(start_date, end_date, floating_leg_tenor, calendar,
    #                             ql.ModifiedFollowing, ql.ModifiedFollowing, ql.DateGeneration.Forward, False)
    
    # length_in_years = 1
    # floating_leg_tenor = ql.Period(3, ql.Months)
    # fixed_leg_tenor = ql.Period(6, ql.Months)
    # float_leg_daycount = ql.Actual360()
    # fixed_leg_daycount = ql.Actual360()

    # start_in_year = 2
    # Define the swap
    # calendar = ql.UnitedStates(ql.UnitedStates.NYSE)
    # start_date = calendar.advance(calc_date, start_in_year, ql.Years)
    # end_date = calendar.advance(swap_start_date, length_in_years, ql.Years)

    # Instantiate the swap
    swap = ql.OvernightIndexedSwap(
        ql.OvernightIndexedSwap.Receiver,  # Pay/Receive type
        notional,  # Notional amount
        fixed_schedule,  # Fixed leg schedule
        fixed_rate if isinstance(fixed_rate, numbers.Number) else 0,  # Fixed rate
        fixed_leg_daycount,  # Fixed leg day count
        index)
    
    # direction = ql.OvernightIndexedSwap.Receiver
    
    if not isinstance(fixed_rate, numbers.Number):
        fixed_rate = swap.fairRate()
        swap = ql.OvernightIndexedSwap(
        direction,  # Pay/Receive type
        notional,  # Notional amount
        fixed_schedule,  # Fixed leg schedule
        fixed_rate,  # Fixed rate
        fixed_leg_daycount,  # Fixed leg day count
        index)
    
    
    update_risk(swap, curve, quotes, index)
    
    
def book_swap(index, notional, direction, start_date,end_date,curve,quotes,fixed_rate,floating_leg_tenor,fixed_leg_tenor,float_leg_daycount,fixed_leg_daycount,calendar):
    
    #fra = ql.ForwardRateAgreement(valueDate, maturityDate, position, strikeForward, notional, iborIndex, discountCurve=ql.YieldTermStructureHandle())
       
    # update risk
    pass