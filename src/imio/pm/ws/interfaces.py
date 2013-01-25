# -*- coding: utf-8 -*-
"""
"""
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest

class IWS4PMLayer(IBrowserRequest):
    """
      Define a layer so the WDSL and schemaextender are only available when the BrowserLayer is installed
    """

class IConfigInfosRequest(Interface):
    """
    Marker interface for change request
    """

class IItemInfosRequest(Interface):
    """
    Marker interface for change request
    """

class ISearchItemsRequest(Interface):
    """
    Marker interface for change request
    """

class ICreateItemRequest(Interface):
    """
    Marker interface for change request
    """

class IExternalIdentifierable(Interface):
    """
    Marker interface for externalIdentifier field schema extender
    """