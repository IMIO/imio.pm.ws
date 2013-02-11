##################################################
# file: WS4PM_server.py
#
# skeleton generated by "ZSI.generate.wsdl2dispatch.ServiceModuleWriter"
#      /srv/zsi/bin/wsdl2py currentWSDL.txt -o . -b
#
##################################################

from ZSI.schema import GED, GTD
from ZSI.TCcompound import ComplexType, Struct
from WS4PM_types import *
from ZSI.ServiceContainer import ServiceSOAPBinding

# Messages  
testConnectionRequest = GED("http://ws4pm.imio.be", "testConnectionRequest").pyclass

testConnectionResponse = GED("http://ws4pm.imio.be", "testConnectionResponse").pyclass

getConfigInfosRequest = GED("http://ws4pm.imio.be", "getConfigInfosRequest").pyclass

getConfigInfosResponse = GED("http://ws4pm.imio.be", "getConfigInfosResponse").pyclass

getItemInfosRequest = GED("http://ws4pm.imio.be", "getItemInfosRequest").pyclass

getItemInfosResponse = GED("http://ws4pm.imio.be", "getItemInfosResponse").pyclass

searchItemsRequest = GED("http://ws4pm.imio.be", "searchItemsRequest").pyclass

searchItemsResponse = GED("http://ws4pm.imio.be", "searchItemsResponse").pyclass

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

    def soap_getConfigInfos(self, ps, **kw):
        request = ps.Parse(getConfigInfosRequest.typecode)
        return request,getConfigInfosResponse()

    soapAction['http://ws4pm.imio.be/getConfigInfos'] = 'soap_getConfigInfos'
    root[(getConfigInfosRequest.typecode.nspname,getConfigInfosRequest.typecode.pname)] = 'soap_getConfigInfos'

    def soap_getItemInfos(self, ps, **kw):
        request = ps.Parse(getItemInfosRequest.typecode)
        return request,getItemInfosResponse()

    soapAction['http://ws4pm.imio.be/getItemInfos'] = 'soap_getItemInfos'
    root[(getItemInfosRequest.typecode.nspname,getItemInfosRequest.typecode.pname)] = 'soap_getItemInfos'

    def soap_searchItems(self, ps, **kw):
        request = ps.Parse(searchItemsRequest.typecode)
        return request,searchItemsResponse()

    soapAction['http://ws4pm.imio.be/searchItems'] = 'soap_searchItems'
    root[(searchItemsRequest.typecode.nspname,searchItemsRequest.typecode.pname)] = 'soap_searchItems'

    def soap_createItem(self, ps, **kw):
        request = ps.Parse(createItemRequest.typecode)
        return request,createItemResponse()

    soapAction['http://ws4pm.imio.be/createItem'] = 'soap_createItem'
    root[(createItemRequest.typecode.nspname,createItemRequest.typecode.pname)] = 'soap_createItem'

