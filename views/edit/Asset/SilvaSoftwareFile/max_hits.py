## Script (Python) "stats_by_month"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=statslist
##title=
##
max = 0
for id, hits in statslist:
    if hits > max:
        max = hits
return max
