__version__ = '4.0b1'

# Check Django compatibility before other imports which may fail if the
# wrong version of Django is installed.
from .utils import check_django_compatability

check_django_compatability()

from .functions import register_functions  # noqa
from .lookups import register_lookups  # noqa

register_functions()
register_lookups()
