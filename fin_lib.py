import pandas as pd
import QuantLib as ql
import plotly.express as px

index_conventions = {}
index_conventions['Sofr'] = {
    'calendar' : ql.UnitedStates(ql.UnitedStates.NYSE),
    'business_convention' : ql.Unadjusted,
    'day_count' : ql.Actual360(),
    'fixing_days' : 0,
    'settlement_days' : 2
}

index_conventions['Sonia'] = {
    'calendar' : ql.UnitedKingdom(),
    'business_convention' : ql.Unadjusted,
    'day_count' : ql.Actual365Fixed(),
    'fixing_days' : 0,
    'settlement_days' : 0
}

basis_point = 0.0001

day_count = ql.Actual360()

def get_index(index:str):
    if index == "Sonia":
        return ql.Sonia(ql.YieldTermStructureHandle())
    else:
        return ql.Sofr(ql.YieldTermStructureHandle())


def create_rate_helpers(deposits, futures, swaps, index):
    
    quotes = {}  # To store quotes with their buckets as keys
    
    fixing_days = index_conventions[index.__class__.__name__]["fixing_days"]
    calendar = index_conventions[index.__class__.__name__]["calendar"]
    business_convention = index_conventions[index.__class__.__name__]["business_convention"]
    settlement_days = index_conventions[index.__class__.__name__]["settlement_days"]
    
    # Create deposit rate helpers
    deposit_helpers = []
    for tenor, rate in deposits.items():
        bucket = str(ql.Period(tenor))
        quotes[bucket] = ql.SimpleQuote(rate)  # Use the bucket as the key
        deposit_helpers.append(ql.DepositRateHelper(ql.QuoteHandle(quotes[bucket]),
                                                    ql.Period(tenor),
                                                    fixing_days,
                                                    calendar,
                                                    business_convention,
                                                    False,
                                                    day_count))

    # Create futures rate helpers
    futures_helpers = []
    for i, (future_code, price) in enumerate(futures.items()):
        bucket = f'{i+1}IMM'  # IMM index as the bucket key
        quotes[bucket] = ql.SimpleQuote(price)  # Use the bucket as the key
        futures_helpers.append(ql.OvernightIndexFutureRateHelper(ql.QuoteHandle(quotes[bucket]),
                                                                 ql.IMM.date(future_code) ,
                                                                 ql.IMM.nextDate(future_code),
                                                                 index))

    # Create swap rate helpers
    swap_helpers = []
    for tenor, rate in swaps.items():
        bucket = str(ql.Period(tenor))
        quotes[bucket] = ql.SimpleQuote(rate)
        swap_helpers.append(ql.OISRateHelper(settlement_days,
                                             ql.Period(tenor),
                                             ql.QuoteHandle(quotes[bucket]),
                                             index))

    # Combine all rate helpers
    rate_helpers = deposit_helpers + futures_helpers + swap_helpers

    return rate_helpers, quotes

def build_rate_model(calc_date, deposits, futures, swaps, index, risk=False):
    
    calc_date = ql.Date(calc_date.day, calc_date.month, calc_date.year)
    
    if isinstance(index, str):
        index = get_index(index)
        
    ql.Settings.instance().evaluationDate = calc_date
    
    rate_helpers, quotes = create_rate_helpers(deposits, futures, swaps, index)
    if not risk:
        curve = ql.PiecewiseNaturalCubicZero(calc_date, rate_helpers, day_count)
        curve.enableExtrapolation()
        return curve
    else:
        curve = ql.PiecewiseLogLinearDiscount(calc_date, rate_helpers, day_count) if risk else ql.PiecewiseNaturalCubicZero(calc_date, rate_helpers, day_count)
        curve.enableExtrapolation()
        return curve, quotes

def delta_ladder(trades: dict(), curve: ql.YieldTermStructure, quotes: dict()):
    
    pricing_engine = ql.DiscountingSwapEngine(ql.YieldTermStructureHandle(curve))
    
    if not isinstance(trades, dict):
        if isinstance(trades,ql.Instrument):
            trades = {"instrument":trades}
        else:
            raise Exception("trades should be an instrument or a dictionary of instruments.")
    
    for trade in trades.values():
        trade.setPricingEngine(pricing_engine)
    
    delta_ladder_df = pd.DataFrame(
         {trade_label: -trade.NPV() for trade_label, trade in trades.items()},
        index=quotes.keys()
    )
    
    for tenor, quote in quotes.items():
        # Bump the helper rate by 1 basis point
        rate_value = quote.value()
        
        quote.setValue(rate_value + basis_point)
        
        # Recalculate the swap price
        for trade_label, trade in trades.items():
            new_price = trade.NPV()
        
            # The change in price is the delta for this tenor
            delta_ladder_df[trade_label][tenor] += new_price
        
        # Reset the rate
        quote.setValue(rate_value)
    
    return delta_ladder_df


def pv_trades(trades: dict(), curve: ql.YieldTermStructure):
    
    pricing_engine = ql.DiscountingSwapEngine(ql.YieldTermStructureHandle(curve))
    
    if not isinstance(trades, dict):
        if isinstance(trades,ql.Instrument):
            trades = {"instrument":trades}
        else:
            raise Exception("trades should be an instrument or a dictionary of instruments.")
    
    for trade in trades.values():
        trade.setPricingEngine(pricing_engine)
    
    pv_trades_df = pd.DataFrame(
        [{trade_label: trade.NPV() for trade_label, trade in trades.items()}]
        )
    
    return pv_trades_df



def plot_curve(curve: ql.YieldTermStructure, period: ql.Period, calendar: ql.Calendar = ql.NullCalendar(), basis = 100):
    calc_date = curve.referenceDate()
    end_date = calc_date + ql.Period(period)
    dates = [calc_date + i for i in range((end_date - calc_date) + 1)]
    forward_rates = []

    for date in dates:
        fwd_rate = curve.forwardRate(date, calendar.advance(date, 1, ql.Days), day_count, ql.Simple).rate()
        forward_rates.append(fwd_rate*basis)
        
    dates_datetime = [date.to_date() for date in dates]
    forwards_df =  pd.DataFrame({
        'Maturity': dates_datetime,
        'Forward Rates': forward_rates
    })
    return px.line(forwards_df, x='Maturity', y='Forward Rates', title='Central Bank Forward Rates')
    
    