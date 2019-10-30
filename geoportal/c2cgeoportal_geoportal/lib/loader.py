import os
from typing import Dict

from c2c.template.config import config as configuration
from plaster_pastedeploy import Loader as BaseLoader


class Loader(BaseLoader):
    def _get_defaults(self, defaults: Dict[str, str] = None) -> Dict[str, str]:
        d = {}  # type: Dict[str, str]
        d.update({k: v.replace("%", "%%") for k, v in os.environ.items()})
        if defaults:
            d.update(defaults)
        return super()._get_defaults(d)

    def get_wsgi_app_settings(self, name: str = None, defaults: Dict[str, str] = None) -> Dict:
        settings = super().get_wsgi_app_settings(name, defaults)
        configuration.init(settings.get("app.cfg"))
        settings.update(configuration.get_config())
        return settings

    def __repr__(self) -> str:
        return 'c2cgeoportal_geoportal.lib.loader.Loader(uri="{0}")'.format(self.uri)
