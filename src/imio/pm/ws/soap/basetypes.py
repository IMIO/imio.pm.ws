# -*- coding: utf-8 -*-
"""
"""
from ZSI.schema import GTD
from imio.pm.ws.WS4PM_services_types import *
ItemInfo = GTD('http://ws4pm.imio.be', 'ItemInfo')('').pyclass
ConfigInfo = GTD('http://ws4pm.imio.be', 'ConfigInfo')('').pyclass
AnnexInfo = GTD('http://ws4pm.imio.be', 'AnnexInfo')('').pyclass
