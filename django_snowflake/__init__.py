__version__ = '5.1'

# Check Django compatibility before other imports which may fail if the
# wrong version of Django is installed.
from .utils import check_django_compatability

check_django_compatability()

from .expressions import register_expressions  # noqa
from .functions import register_functions  # noqa
from .lookups import register_lookups  # noqa

register_expressions()
register_functions()
register_lookups()
