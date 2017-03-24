# -*- coding: utf-8 -*-
"""
"""
from ZSI.schema import GTD
from imio.pm.ws.WS4PM_types import *


AnnexInfo = GTD('http://ws4pm.imio.be', 'AnnexInfo')('').pyclass
BasicInfo = GTD('http://ws4pm.imio.be', 'BasicInfo')('').pyclass
ConfigInfo = GTD('http://ws4pm.imio.be', 'ConfigInfo')('').pyclass
GroupInfo = GTD('http://ws4pm.imio.be', 'GroupInfo')('').pyclass
ItemInfo = GTD('http://ws4pm.imio.be', 'ItemInfo')('').pyclass
MeetingInfo = GTD('http://ws4pm.imio.be', 'MeetingInfo')('').pyclass
TemplateInfo = GTD('http://ws4pm.imio.be', 'TemplateInfo')('').pyclass
