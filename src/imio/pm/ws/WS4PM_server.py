##################################################
# file: WS4PM_server.py
#
# skeleton generated by "ZSI.generate.wsdl2dispatch.ServiceModuleWriter"
#      /srv/ZSI/bin/wsdl2py dumpedWSDL.txt -o . -b
#
##################################################

from ZSI.schema import GED, GTD
from ZSI.TCcompound import ComplexType, Struct
from WS4PM_types import *
from ZSI.ServiceContainer import ServiceSOAPBinding

# Messages  
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

getSingleItemInfosRequest = GED("http://ws4pm.imio.be", "getSingleItemInfosRequest").pyclass

getSingleItemInfosResponse = GED("http://ws4pm.imio.be", "getSingleItemInfosResponse").pyclass

getItemTemplateRequest = GED("http://ws4pm.imio.be", "getItemTemplateRequest").pyclass

getItemTemplateResponse = GED("http://ws4pm.imio.be", "getItemTemplateResponse").pyclass

searchItemsRequest = GED("http://ws4pm.imio.be", "searchItemsRequest").pyclass

searchItemsResponse = GED("http://ws4pm.imio.be", "searchItemsResponse").pyclass

meetingsAcceptingItemsRequest = GED("http://ws4pm.imio.be", "meetingsAcceptingItemsRequest").pyclass

meetingsAcceptingItemsResponse = GED("http://ws4pm.imio.be", "meetingsAcceptingItemsResponse").pyclass

createItemRequest = GED("http://ws4pm.imio.be", "createItemRequest").pyclass

createItemResponse = GED("http://ws4pm.imio.be", "createItemResponse").pyclass


# Service Skeletons
class WS4PM(ServiceSOAPBinding):
    soapAction = {}
    root = {}

    def __init__(self, post='', **kw):
        ServiceSOAPBinding.__init__(self, post)

    def soap_testConnection(self, ps, **kw):
        request = ps.Parse(testConnectionRequest.typecode)
        return request,testConnectionResponse()

    soapAction['http://ws4pm.imio.be/testConnection'] = 'soap_testConnection'
    root[(testConnectionRequest.typecode.nspname,testConnectionRequest.typecode.pname)] = 'soap_testConnection'

    def soap_checkIsLinked(self, ps, **kw):
        request = ps.Parse(checkIsLinkedRequest.typecode)
        return request,checkIsLinkedResponse()

    soapAction['http://ws4pm.imio.be/checkIsLinked'] = 'soap_checkIsLinked'
    root[(checkIsLinkedRequest.typecode.nspname,checkIsLinkedRequest.typecode.pname)] = 'soap_checkIsLinked'

    def soap_getConfigInfos(self, ps, **kw):
        request = ps.Parse(getConfigInfosRequest.typecode)
        return request,getConfigInfosResponse()

    soapAction['http://ws4pm.imio.be/getConfigInfos'] = 'soap_getConfigInfos'
    root[(getConfigInfosRequest.typecode.nspname,getConfigInfosRequest.typecode.pname)] = 'soap_getConfigInfos'

    def soap_getUserInfos(self, ps, **kw):
        request = ps.Parse(getUserInfosRequest.typecode)
        return request,getUserInfosResponse()

    soapAction['http://ws4pm.imio.be/getUserInfos'] = 'soap_getUserInfos'
    root[(getUserInfosRequest.typecode.nspname,getUserInfosRequest.typecode.pname)] = 'soap_getUserInfos'

    def soap_getItemInfos(self, ps, **kw):
        request = ps.Parse(getItemInfosRequest.typecode)
        return request,getItemInfosResponse()

    soapAction['http://ws4pm.imio.be/getItemInfos'] = 'soap_getItemInfos'
    root[(getItemInfosRequest.typecode.nspname,getItemInfosRequest.typecode.pname)] = 'soap_getItemInfos'

    def soap_getSingleItemInfos(self, ps, **kw):
        request = ps.Parse(getSingleItemInfosRequest.typecode)
        return request,getSingleItemInfosResponse()

    soapAction['http://ws4pm.imio.be/getSingleItemInfos'] = 'soap_getSingleItemInfos'
    root[(getSingleItemInfosRequest.typecode.nspname,getSingleItemInfosRequest.typecode.pname)] = 'soap_getSingleItemInfos'

    def soap_getItemTemplate(self, ps, **kw):
        request = ps.Parse(getItemTemplateRequest.typecode)
        return request,getItemTemplateResponse()

    soapAction['http://ws4pm.imio.be/getItemTemplate'] = 'soap_getItemTemplate'
    root[(getItemTemplateRequest.typecode.nspname,getItemTemplateRequest.typecode.pname)] = 'soap_getItemTemplate'

    def soap_searchItems(self, ps, **kw):
        request = ps.Parse(searchItemsRequest.typecode)
        return request,searchItemsResponse()

    soapAction['http://ws4pm.imio.be/searchItems'] = 'soap_searchItems'
    root[(searchItemsRequest.typecode.nspname,searchItemsRequest.typecode.pname)] = 'soap_searchItems'

    def soap_meetingsAcceptingItems(self, ps, **kw):
        request = ps.Parse(meetingsAcceptingItemsRequest.typecode)
        return request,meetingsAcceptingItemsResponse()

    soapAction['http://ws4pm.imio.be/meetingsAcceptingItems'] = 'soap_meetingsAcceptingItems'
    root[(meetingsAcceptingItemsRequest.typecode.nspname,meetingsAcceptingItemsRequest.typecode.pname)] = 'soap_meetingsAcceptingItems'

    def soap_createItem(self, ps, **kw):
        request = ps.Parse(createItemRequest.typecode)
        return request,createItemResponse()

    soapAction['http://ws4pm.imio.be/createItem'] = 'soap_createItem'
    root[(createItemRequest.typecode.nspname,createItemRequest.typecode.pname)] = 'soap_createItem'

