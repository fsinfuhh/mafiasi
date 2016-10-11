from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

def validate_ascii(value):
    try:
        value.encode('ascii')
    except UnicodeEncodeError, UnicodeDecodeError:
        raise ValidationError(
                _("'%(value)s' contains invalid characters. Only ASCII characters are allowed."),
                params={'value': value},
                )


class AsciiValidator(object):
    """
    Validate whether the password contains only ASCII chars.
    """
    def __init__(self, min_length=8):
        self.min_length = min_length

    def validate(self, password, user=None):
        try:
            validate_ascii(password)
        except ValidationError:
            raise ValidationError(
                    _("Your password contains invalid characters. Only ASCII characters are allowed.")
                    )

    def get_help_text(self):
        return _("Your password may only contain the following characters: %(chars)s") % \
                    " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
