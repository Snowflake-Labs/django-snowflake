__version__ = '6.0a0'

# Check Django compatibility before other imports which may fail if the
# wrong version of Django is installed.
from .utils import check_django_compatability

check_django_compatability()

from .aggregates import register_aggregates  # noqa
from .expressions import register_expressions  # noqa
from .functions import register_functions  # noqa
from .lookups import register_lookups  # noqa

register_aggregates()
register_expressions()
register_functions()
register_lookups()
