# -*- coding: utf-8 -*-
#
# File: setuphandlers.py
#
# Copyright (c) 2013 by Imio
#
# GNU General Public License (GPL)
#

__author__ = """Gauthier Bastien <gauthier@imio.be>"""
__docformat__ = 'plaintext'


from Products.CMFCore.utils import getToolByName

import logging


logger = logging.getLogger('imio.pm.ws: setuphandlers')


def isNotImioPmWsProfile(context):
    return context.readDataFile("imio_pm_ws_marker.txt") is None


def postInstall(context):
    """Called as at the end of the setup process. """
    # the right place for your custom code
    if isNotImioPmWsProfile(context):
        return

    portal = context.getSite()
    #Update schema of existing MeetingItems to take new fields added by schemaextender
    _updateMeetingItemsSchema(portal)


def _updateMeetingItemsSchema(portal):
    """
      We add a 'externalIdentifier' field using archetypes.schemaextender
      to every objects providing the IMeetingItem interface
    """
    logger.info("Updating the schema of every MeetingItems...")
    at_tool = getToolByName(portal, 'archetype_tool')
    catalog = getToolByName(portal, 'portal_catalog')
    catalog.ZopeFindAndApply(portal,
                             obj_metatypes=('MeetingItem',),
                             search_sub=True,
                             apply_func=at_tool._updateObject)
    logger.info("Done!")
