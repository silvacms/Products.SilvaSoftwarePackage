from Products.Silva import mangle
from Products.Silva.interfaces import IAsset

model = context.REQUEST.model
view = context
REQUEST = context.REQUEST

# if we cancelled, then go back to edit tab
if REQUEST.has_key('add_cancel'):
    return view.tab_edit()

# validate form
from Products.Formulator.Errors import ValidationError, FormValidationError
try:
    result = view.form.validate_all(REQUEST)
except FormValidationError, e:
    # in case of errors go back to add page and re-render form
    return view.add_form(message_type="error",
        message=view.render_form_errors(e))

id = mangle.Id(model, result['object_id'], file=result['file'], 
    interface=IAsset)
file = result['file']

# do some additional validation
if not file or not getattr(file, 'filename', None):
    return view.add_form(message_type="error",
        message="Empty or invalid file.")

# if we don't have the right id, reject adding
id_check = id.cook().validate()
if id_check != id.OK:
    return view.add_form(message_type="error",
        message=view.get_id_status_text(id))
id = str(id)

# try to cope with absence of title in form
if result.has_key('object_title'):
    title = result['object_title']
    del result['object_title']
else:
    title = ""

# process data in result and add using validation result
view = context

try:
    model.manage_addProduct['SilvaSoftwarePackage'].manage_addSilvaSoftwareFile(id, title, file=file)
except IOError, e:
    return view.add_form(message_type="error", message=e)
object = getattr(model, id)

# update last author info in new object
object.sec_update_last_author_info()

# now go to tab_edit in case of add and edit, back to container if not.
if REQUEST.has_key('add_edit_submit'):
    REQUEST.RESPONSE.redirect(object.absolute_url() + '/edit/tab_edit')
else:
    return view.tab_edit(
        message_type="feedback",
        message="Added %s %s." % (object.meta_type, view.quotify(id)))

