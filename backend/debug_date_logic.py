
import dateparser
from datetime import datetime

def test_dates():
    # Simulate "Today" as Wednesday, Jan 29, 2026
    base_date = datetime(2026, 1, 29) 
    
    phrases = [
        "next saturday",          # Control: Expect Jan 31
        "saturday next week",     # Hypothesis: Expect Feb 7
        "next week saturday"      # Raw input
    ]

    print(f"Base Date: {base_date.strftime('%Y-%m-%d (%A)')}")
    print("-" * 40)
    
    # Simple check
    print(f"today: {dateparser.parse('today', settings={'RELATIVE_BASE': base_date})}")

    new_phrases = [
        "next week Saturday",
        "before end of this month",
        "end of next month",
        "end of weekend"
    ]
    
    from datetime import timedelta
    
    for phrase in new_phrases:
        print(f"Testing manual logic for '{phrase}':")
        lower = phrase.lower()
        if "next week" in lower:
             clean = lower.replace("next week", "").strip()
             base = dateparser.parse(clean, settings={'RELATIVE_BASE': base_date, 'PREFER_DATES_FROM': 'future'})
             if base:
                 final = base + timedelta(days=7)
                 print(f"  -> Base '{clean}': {base.strftime('%Y-%m-%d')} + 7 days = {final.strftime('%Y-%m-%d (%A)')}")
             else:
                 print("  -> Base parse failed")
        elif "end of this month" in lower:
             # Last day of current month
             # (replace day with 28, add 4 days, sub day number to find start of next month... or just use logic)
             # Easier: (replace day=1) + 1 month - 1 day
             # Or: month inputs
             import calendar
             last_day = calendar.monthrange(base_date.year, base_date.month)[1]
             final = base_date.replace(day=last_day)
             print(f"  -> End of This Month: {final.strftime('%Y-%m-%d (%A)')}")
        elif "end of next month" in lower:
             import calendar
             # Move to next month
             if base_date.month == 12:
                 next_month_year = base_date.year + 1
                 next_month = 1
             else:
                 next_month_year = base_date.year
                 next_month = base_date.month + 1
             
             last_day = calendar.monthrange(next_month_year, next_month)[1]
             final = base_date.replace(year=next_month_year, month=next_month, day=last_day)
             print(f"  -> End of Next Month: {final.strftime('%Y-%m-%d (%A)')}")
        elif "end of weekend" in lower:
             # Next Sunday
             # Weekday: Mon=0, Sun=6. 
             # Days until Sunday = 6 - weekday
             days_ahead = 6 - base_date.weekday()
             if days_ahead <= 0: # Today is Sunday
                  days_ahead += 7
             final = base_date + timedelta(days=days_ahead)
             print(f"  -> End of Weekend (Sunday): {final.strftime('%Y-%m-%d (%A)')}")
        else:
             # Standard fallback
             # Standard fallback
             dt = dateparser.parse(phrase, settings={'RELATIVE_BASE': base_date, 'PREFER_DATES_FROM': 'future'})
             if dt:
                 print(f"  -> {dt.strftime('%Y-%m-%d (%A)')}")
             else:
                 print(f"  -> None")

if __name__ == "__main__":
    test_dates()
