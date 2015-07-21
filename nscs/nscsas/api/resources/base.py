from pecan import expose, abort, response
from pecan.rest import RestController
import inspect
import wsme
from wsme import types as wtypes
from netaddr.ip import IPNetwork, IPAddress
from netaddr.core import AddrFormatError

from oslo_log import log as logging
from oslo_i18n._i18n import _

LOG = logging.getLogger(__name__)


class EntityNotFound(Exception):
    code = 404

    def __init__(self, entity, id):
        super(EntityNotFound, self).__init__(
            _("%(entity)s '%(id)s' Not Found") % {'entity': entity,
                                                  'id': id})


class BoundedInt(wtypes.UserType):
    basetype = int
    name = 'bounded int'

    def __init__(self, min=None, max=None):
        self.min = min
        self.max = max

    @staticmethod
    def frombasetype(value):
        return int(value) if value is not None else None

    def validate(self, value):
        if self.min is not None and value < self.min:
            error = _('Value %(value)s is invalid (should be greater or equal '
                      'to %(min)s)') % dict(value=value, min=self.min)
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        if self.max is not None and value > self.max:
            error = _('Value %(value)s is invalid (should be lower or equal '
                      'to %(max)s)') % dict(value=value, max=self.max)
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))
        return value


class BoundedStr(wtypes.UserType):
    basetype = str
    name = 'bounded string'

    def __init__(self, minlen=None, maxlen=None):
        self.minlen = minlen
        self.maxlen = maxlen

    @staticmethod
    def frombasetype(value):
        return str(value) if value is not None else ''

    def validate(self, value):
        if self.minlen is not None and len(value) < self.minlen:
            error = _('Value %(value)s is invalid (length should be greater or equal '
                      'to %(min)s)') % dict(value=value, min=self.minlen)
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))

        if self.maxlen is not None and len(value) > self.maxlen:
            error = _('Value %(value)s is invalid (length should be lower or equal '
                      'to %(max)s)') % dict(value=value, max=self.maxlen)
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))
        return value


class CIDR(wtypes.wsproperty):

    def __init__(self, name, **kwargs):
        self._name = '_CIDR_%s' % name
        mandatory = kwargs.pop('mandatory', False)
        super(CIDR, self).__init__(datatype=wtypes.text, fget=self._get,
                                   fset=self._set, mandatory=mandatory)

    def _get(self, parent):
        if hasattr(parent, self._name):
            value = getattr(parent, self._name)
            return value or wsme.Unset
        return wsme.Unset

    def _set(self, parent, value):
        try:
            if value and IPNetwork(value):
                setattr(parent, self._name, value)
        except AddrFormatError:
            error = _('Value %(value)s is not a valid IP Address') % dict(value=value)
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))


def validate_ip(value):
    try:
        if value:
            IPAddress(value)
    except AddrFormatError:
        error = _('Value %(value)s is not a valid IP Address') % dict(value=value)
        response.translatable_error = error
        raise wsme.exc.ClientSideError(unicode(error))


class IP(wtypes.wsproperty):

    def __init__(self, name, **kwargs):
        self._name = '_IP_%s' % name
        mandatory = kwargs.pop('mandatory', False)
        super(IP, self).__init__(datatype=wtypes.text, fget=self._get,
                                 fset=self._set, mandatory=mandatory)

    def _get(self, parent):
        if hasattr(parent, self._name):
            value = getattr(parent, self._name)
            return value or wsme.Unset
        return wsme.Unset

    def _set(self, parent, value):
        try:
            if value and IPAddress(value):
                setattr(parent, self._name, value)
        except AddrFormatError:
            error = _('Value %(value)s is not a valid IP Address') % dict(value=value)
            response.translatable_error = error
            raise wsme.exc.ClientSideError(unicode(error))


class AdvEnum(wtypes.wsproperty):
    """Handle default and mandatory for wtypes.Enum
    """
    def __init__(self, name, *args, **kwargs):
        self._name = '_advenum_%s' % name
        mandatory = kwargs.pop('mandatory', False)
        if kwargs.pop('capitalize', False):
            arg_caps = [args[0]]
            for a in args[1:]:
                arg_caps.append(a.capitalize())
            args = arg_caps
        enum = wtypes.Enum(*args, **kwargs)
        super(AdvEnum, self).__init__(datatype=enum, fget=self._get,
                                      fset=self._set, mandatory=mandatory)

    def _get(self, parent):
        if hasattr(parent, self._name):
            value = getattr(parent, self._name)
            return value or wsme.Unset
        return wsme.Unset

    def _set(self, parent, value):
        if self.datatype.validate(value):
            setattr(parent, self._name, value)


class _Base(wtypes.Base):
    @classmethod
    def from_db_model(cls, m):
        return cls(**(m.as_dict()))

    @classmethod
    def from_db_and_links(cls, m, links):
        return cls(links=links, **(m.as_dict()))

    def as_dict(self, db_model):
        valid_keys = inspect.getargspec(db_model.__init__)[0]
        if 'self' in valid_keys:
            valid_keys.remove('self')
        return self.as_dict_from_keys(valid_keys)

    def as_dict_from_keys(self, keys):
        return dict((k, getattr(self, k))
                    for k in keys
                    if hasattr(self, k) and getattr(self, k) != wsme.Unset)


class BaseController(RestController):
    """
    This class implements base functions for handling REST requests
    """

    @expose('json')
    def get_all(self):
        abort(status_code=404, explanation="Not Implemented", detail="Method Not Implemented")

    @expose('json')
    def get_one(self, *args):
        abort(status_code=404, explanation="Not Implemented", detail="Method Not Implemented")

    @expose('json')
    def post(self, *args):
        abort(status_code=404, explanation="Not Implemented", detail="Method Not Implemented")

    @expose('json')
    def put(self, *args):
        abort(status_code=404, explanation="Not Implemented", detail="Method Not Implemented")

    @expose('json')
    def delete(self, *args):
        abort(status_code=404, explanation="Not Implemented", detail="Method Not Implemented")
