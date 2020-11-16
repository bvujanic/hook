import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from webhook.upserter import Upserter as Upserter  # noqa # pylint: disable=unused-import, wrong-import-position
