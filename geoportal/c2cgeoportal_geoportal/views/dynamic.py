# -*- coding: utf-8 -*-

# Copyright (c) 2018-2021, Camptocamp SA
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# The views and conclusions contained in the software and documentation are those
# of the authors and should not be interpreted as representing official policies,
# either expressed or implied, of the FreeBSD Project.


import re
import urllib.parse
from typing import Any, Dict, List, Union, cast

import pyramid.request
from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config
from sqlalchemy import func

from c2cgeoportal_commons import models
from c2cgeoportal_commons.models import main
from c2cgeoportal_geoportal.lib.cacheversion import get_cache_version
from c2cgeoportal_geoportal.lib.caching import Cache, get_region, set_common_headers

CACHE_REGION = get_region("std")


class DynamicView:
    def __init__(self, request: pyramid.request.Request):
        self.request = request
        self.settings = request.registry.settings
        self.interfaces_config = self.settings["interfaces_config"]

    def get(self, value: Dict[str, Any], interface: str) -> Dict[str, Any]:
        return cast(Dict[str, Any], self.interfaces_config.get(interface, {}).get(value, {}))

    @CACHE_REGION.cache_on_arguments()
    def _fulltextsearch_groups(self) -> List[str]:  # pylint: disable=no-self-use
        return [
            group[0]
            for group in models.DBSession.query(func.distinct(main.FullTextSearch.layer_name))
            .filter(main.FullTextSearch.layer_name.isnot(None))
            .all()
        ]

    def _interface(
        self, interface_config: Dict[str, Any], interface_name: str, dynamic: Dict[str, Any]
    ) -> Dict[str, Any]:

        if "extends" in interface_config:
            constants = self._interface(
                self.interfaces_config[interface_config["extends"]], interface_name, dynamic
            )
        else:
            constants = {}

        constants.update(interface_config.get("constants", {}))
        constants.update(
            {
                name: dynamic[value]
                for name, value in interface_config.get("dynamic_constants", {}).items()
                if value is not None
            }
        )
        constants.update(
            {
                name: self.request.static_url(static_["name"]) + static_.get("append", "")
                for name, static_ in interface_config.get("static", {}).items()
            }
        )

        for constant, config in interface_config.get("routes", {}).items():
            route_name = interface_name if config.get("currentInterface", False) else config["name"]
            params: Dict[str, str] = {}
            params.update(config.get("params", {}))
            for name, dyn in config.get("dynamic_params", {}).items():
                params[name] = dynamic[dyn]
            constants[constant] = self.request.route_url(
                route_name, *config.get("elements", []), _query=params, **config.get("kw", {})
            )

        return constants

    @view_config(route_name="dynamic", renderer="fast_json")
    def dynamic(self) -> Dict[str, Any]:
        interface_name = self.request.params.get("interface")

        if interface_name not in self.interfaces_config:
            raise HTTPNotFound("Interface {} doesn't exists in the 'interfaces_config'.")

        interface_config = self.interfaces_config[interface_name]

        dynamic = {
            "interface": interface_name,
            "cache_version": get_cache_version(),
            "two_factor": self.request.registry.settings.get("authentication", {}).get("two_factor", False),
            "lang_urls": {
                lang: self.request.static_url(
                    "/etc/geomapfish/static/{lang}.json".format(lang=lang),
                    _query={"cache": get_cache_version()},
                )
                for lang in self.request.registry.settings["available_locale_names"]
            },
            "fulltextsearch_groups": self._fulltextsearch_groups(),
        }

        constants = self._interface(interface_config, interface_name, dynamic)

        do_redirect = False
        url = None
        if "redirect_interface" in interface_config:
            no_redirect_query: Dict[str, Union[str, List[str]]] = {"no_redirect": "t"}
            if "query" in self.request.params:
                query = urllib.parse.parse_qs(self.request.params["query"][1:], keep_blank_values=True)
                no_redirect_query.update(query)
            else:
                query = {}
            theme = None
            if "path" in self.request.params:
                match = re.match(".*/theme/(.*)", self.request.params["path"])
                if match is not None:
                    theme = match.group(1)
            if theme is not None:
                no_redirect_url = self.request.route_url(
                    interface_config["redirect_interface"] + "theme", themes=theme, _query=no_redirect_query
                )
                url = self.request.route_url(
                    interface_config["redirect_interface"] + "theme", themes=theme, _query=query
                ).replace("+", "%20")
            else:
                no_redirect_url = self.request.route_url(
                    interface_config["redirect_interface"], _query=no_redirect_query
                )
                url = self.request.route_url(interface_config["redirect_interface"], _query=query).replace(
                    "+", "%20"
                )

            if "no_redirect" in query:
                constants["redirectUrl"] = ""
            else:
                if interface_config.get("do_redirect", False):
                    do_redirect = True
                else:
                    constants["redirectUrl"] = no_redirect_url

        set_common_headers(self.request, "dynamic", Cache.NO)
        return {"constants": constants, "doRedirect": do_redirect, "redirectUrl": url}
