from Products.Formulator.StandardFields import StringField
from Products.Formulator.Validator import StringBaseValidator
import re

_version_reg = re.compile('^[0-9]+(\.[0-9]+)*(\.[0-9]+)?((a|b|rc)[0-9]*)?$')
def test_version_string(version):
    """test whether the version conforms to the required format"""
    if not _version_reg.search(version):
        raise TypeError, 'Version string has incorrect format!'

class VersionValidator(StringBaseValidator):
    message_names = StringBaseValidator.message_names + ['version_format_incorrect']
    version_format_incorrect = 'Version string has an unrecognized format!'
    def validate(self, field, key, REQUEST):
        value = StringBaseValidator.validate(self, field, key, REQUEST)
        try:
            test_version_string(value)
        except TypeError, e:
            self.raise_error('version_format_incorrect', field)
        return value

VersionValidatorInstance = VersionValidator()

class VersionField(StringField):
    meta_type = 'VersionField'
    validator = VersionValidatorInstance
