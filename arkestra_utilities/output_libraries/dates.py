from django.contrib.humanize.templatetags.humanize import naturalday

def nice_date(date, date_format = None):
    """
    For date values that are tomorrow, today or yesterday compared to
    present day returns representing string. Otherwise, returns a string
    formatted according to settings.DATE_FORMAT.
    """
    datestring = naturalday(date, date_format)
    return datestring and datestring[0].upper() + datestring[1:]
