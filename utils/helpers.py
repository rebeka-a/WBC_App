import pandas as pd
from datetime import datetime
import pytz

def ch_now(rounding='s'):
    """
    Returns current Swiss time as pandas timestamp without timezone suffix
    Args:
        rounding (str): Time unit to floor to (e.g. 'min', 'H', 's'). Default is 's' (second)
    """
    swiss_tz = pytz.timezone('Europe/Zurich')
    current_time = datetime.now(swiss_tz)
    ts = pd.Timestamp(current_time.replace(tzinfo=None))
    
    return ts.floor(rounding) if rounding else ts
