## Script (Python) "stats_by_month"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=record
##title=
##
from DateTime import DateTime

months = []
lastyearmonth = None
for time in record.get('times', []):
    dt = DateTime(time)
    yearmonth = dt.strftime('%Y/%m')
    if yearmonth != lastyearmonth:
        lastyearmonth = yearmonth
        months.append([yearmonth, 1])
    else:
        months[-1][1] = months[-1][1] + 1
return months
