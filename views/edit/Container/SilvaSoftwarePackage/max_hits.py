## Script (Python) "stats_by_month"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=recordlist
##title=
##
max = 0
for path, record in recordlist:
    hits = record.get('total', 0)
    if hits > max:
        max = hits
return max
