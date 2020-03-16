# -*- coding: utf-8 -*-
"""
"""
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest


class IWS4PMLayer(IBrowserRequest):
    """
      Define a layer so the WDSL and schemaextender are only available when the BrowserLayer is installed
    """


class ITestConnectionRequest(Interface):
    """
    Marker interface for change request
    """


class ICheckIsLinkedRequest(Interface):
    """
    Marker interface for change request
    """


class IConfigInfosRequest(Interface):
    """
    Marker interface for change request
    """


class IUserInfosRequest(Interface):
    """
    Marker interface for change request
    """


class IItemInfosRequest(Interface):
    """
    Marker interface for change request
    """


class ISingleItemInfosRequest(Interface):
    """
    Marker interface for change request
    """


class IItemTemplateRequest(Interface):
    """
    Marker interface for change request
    """


class ISearchItemsRequest(Interface):
    """
    Marker interface for change request
    """


class IMeetingsAcceptingItemsRequest(Interface):
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
