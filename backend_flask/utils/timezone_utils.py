from datetime import datetime
import pytz

PST = pytz.timezone('Asia/Manila')

def get_pst_now():
    """Get current time in Philippine Standard Time."""
    return datetime.now(pytz.utc).astimezone(PST)

def format_pst(dt):
    """Format a datetime object to a naive string in Philippine Standard Time."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        # If naive, assume it's already in the target timezone (PST)
        # and just format it without adding/subtracting hours.
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    # If aware, convert to PST first
    return dt.astimezone(PST).strftime("%Y-%m-%d %H:%M:%S")

def to_pst(dt):
    """Convert a datetime object to Philippine Standard Time."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    return dt.astimezone(PST)
