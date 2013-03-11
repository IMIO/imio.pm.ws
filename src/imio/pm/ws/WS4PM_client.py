##################################################
# file: WS4PM_client.py
# 
# client stubs generated by "ZSI.generate.wsdl2python.WriteServiceModule"
#     /srv/zsi/bin/wsdl2py currentWSDL.txt -o . -b
# 
##################################################

from WS4PM_types import *
import urlparse, types
from ZSI.TCcompound import ComplexType, Struct
from ZSI import client
from ZSI.schema import GED, GTD
import ZSI
from ZSI.generate.pyclass import pyclass_type

# Locator
class WS4PMLocator:
    WS4PMSOAP_address = "http://ws4pm.imio.be"
    def getWS4PMSOAPAddress(self):
        return WS4PMLocator.WS4PMSOAP_address
    def getWS4PMSOAP(self, url=None, **kw):
        return WS4PMSOAPSOAP(url or WS4PMLocator.WS4PMSOAP_address, **kw)

# Methods
class WS4PMSOAPSOAP:
    def __init__(self, url, **kw):
        kw.setdefault("readerclass", None)
        kw.setdefault("writerclass", None)
        # no resource properties
        self.binding = client.Binding(url=url, **kw)
        # no ws-addressing

    # op: testConnection
    def testConnection(self, request, **kw):
        if isinstance(request, testConnectionRequest) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://ws4pm.imio.be/testConnection", **kw)
        # no output wsaction
        response = self.binding.Receive(testConnectionResponse.typecode)
        return response

    # op: checkIsLinked
    def checkIsLinked(self, request, **kw):
        if isinstance(request, checkIsLinkedRequest) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://ws4pm.imio.be/checkIsLinked", **kw)
        # no output wsaction
        response = self.binding.Receive(checkIsLinkedResponse.typecode)
        return response

    # op: getConfigInfos
    def getConfigInfos(self, request, **kw):
        if isinstance(request, getConfigInfosRequest) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://ws4pm.imio.be/getConfigInfos", **kw)
        # no output wsaction
        response = self.binding.Receive(getConfigInfosResponse.typecode)
        return response

    # op: getUserInfos
    def getUserInfos(self, request, **kw):
        if isinstance(request, getUserInfosRequest) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://portal_url/getUserInfos", **kw)
        # no output wsaction
        response = self.binding.Receive(getUserInfosResponse.typecode)
        return response

    # op: getItemInfos
    def getItemInfos(self, request, **kw):
        if isinstance(request, getItemInfosRequest) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://ws4pm.imio.be/getItemInfos", **kw)
        # no output wsaction
        response = self.binding.Receive(getItemInfosResponse.typecode)
        return response

    # op: getItemTemplate
    def getItemTemplate(self, request, **kw):
        if isinstance(request, getItemTemplateRequest) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://ws4pm.imio.be/searchItems", **kw)
        # no output wsaction
        response = self.binding.Receive(getItemTemplateResponse.typecode)
        return response

    # op: searchItems
    def searchItems(self, request, **kw):
        if isinstance(request, searchItemsRequest) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://ws4pm.imio.be/searchItems", **kw)
        # no output wsaction
        response = self.binding.Receive(searchItemsResponse.typecode)
        return response

    # op: createItem
    def createItem(self, request, **kw):
        if isinstance(request, createItemRequest) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://ws4pm.imio.be/createItem", **kw)
        # no output wsaction
        response = self.binding.Receive(createItemResponse.typecode)
        return response

testConnectionRequest = GED("http://ws4pm.imio.be", "testConnectionRequest").pyclass

testConnectionResponse = GED("http://ws4pm.imio.be", "testConnectionResponse").pyclass

checkIsLinkedRequest = GED("http://ws4pm.imio.be", "checkIsLinkedRequest").pyclass

checkIsLinkedResponse = GED("http://ws4pm.imio.be", "checkIsLinkedResponse").pyclass

getConfigInfosRequest = GED("http://ws4pm.imio.be", "getConfigInfosRequest").pyclass

getConfigInfosResponse = GED("http://ws4pm.imio.be", "getConfigInfosResponse").pyclass

getUserInfosRequest = GED("http://ws4pm.imio.be", "getUserInfosRequest").pyclass

getUserInfosResponse = GED("http://ws4pm.imio.be", "getUserInfosResponse").pyclass

getItemInfosRequest = GED("http://ws4pm.imio.be", "getItemInfosRequest").pyclass

getItemInfosResponse = GED("http://ws4pm.imio.be", "getItemInfosResponse").pyclass

getItemTemplateRequest = GED("http://ws4pm.imio.be", "getItemTemplateRequest").pyclass

getItemTemplateResponse = GED("http://ws4pm.imio.be", "getItemTemplateResponse").pyclass

searchItemsRequest = GED("http://ws4pm.imio.be", "searchItemsRequest").pyclass

searchItemsResponse = GED("http://ws4pm.imio.be", "searchItemsResponse").pyclass

createItemRequest = GED("http://ws4pm.imio.be", "createItemRequest").pyclass

createItemResponse = GED("http://ws4pm.imio.be", "createItemResponse").pyclass
