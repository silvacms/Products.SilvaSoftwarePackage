## Script (Python) "records_for_files"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=paths
##title=
##
records = []
for path in paths:
    record = context.service_software.stats_by_path(path)
    records.append((path, record))

records.sort(lambda a, b: cmp(b[0], a[0]))

return records
