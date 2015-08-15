import re

from .checkdigit_mixins import LuhnMixin
from .exceptions import CheckDigitError
from .identifier import Identifier


class IdentifierWithCheckdigit(Identifier, LuhnMixin):

    checkdigit_pattern = r'^[0-9]{1}$'

    def __init__(self, last_identifier=None):
        if self.checkdigit_pattern:
            last_identifier = self.remove_checkdigit(last_identifier or self.last_identifier)
        super().__init__(last_identifier)

    def next_identifier(self):
        """Sets the identifier attr to the next identifier.

        Removes the checkdigit if it has one."""
        if self.checkdigit_pattern:
            if re.match(self.identifier_pattern_with_checkdigit, self.identifier):
                self.identifier = self.remove_checkdigit(self.identifier)
            pattern = self.identifier_pattern_with_checkdigit
        else:
            checkdigit = None
            pattern = self.identifier_pattern
        identifier = self.remove_separator(self.identifier)
        identifier = self.increment(identifier)
        if self.checkdigit_pattern:
            checkdigit = self.calculate_checkdigit(identifier)
        identifier = self.insert_separator(identifier, checkdigit)
        self.identifier = self.validate_identifier_pattern(
            identifier,
            pattern=pattern)
        self.update_history()

    @property
    def identifier_pattern_with_checkdigit(self):
        return '{}{}'.format(self.identifier_pattern[:-1], self.checkdigit_pattern[1:])

    def insert_separator(self, identifier, checkdigit=None):
        identifier = super().insert_separator(identifier)
        identifier = (self.separator or '').join([identifier, checkdigit] if checkdigit else [identifier])
        return identifier

    def remove_checkdigit(self, identifier_with_checkdigit):
        """Returns a tuple of identifier, less the check digit, and the check digit.

        If you specify identifier_pattern it will re.match the identifier or
        raise an error."""
        identifier = None
        if self.checkdigit_pattern and identifier_with_checkdigit:
            try:
                checkdigit = re.findall(self.checkdigit_pattern[1:], identifier_with_checkdigit)[0]
            except IndexError:
                raise CheckDigitError(
                    'Cannot match check digit for this identifier using pattern {}. Got {}.'.format(
                        self.checkdigit_pattern, identifier_with_checkdigit))
            identifier = identifier_with_checkdigit[:-len(checkdigit)]
            checkdigit = checkdigit.replace(self.separator or '', '')
            if not checkdigit == self.calculate_checkdigit(identifier):
                raise CheckDigitError(
                    'Identifier with check digit {} is invalid. Got identifier {}'.format(
                        checkdigit, identifier_with_checkdigit))
        return identifier