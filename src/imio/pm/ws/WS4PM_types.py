##################################################
# file: WS4PM_types.py
#
# schema types generated by "ZSI.generate.wsdl2python.WriteServiceModule"
#    /srv/zsi/bin/wsdl2py currentWSDL.txt -o . -b
#
##################################################

import ZSI
import ZSI.TCcompound
from ZSI.schema import LocalElementDeclaration, ElementDeclaration, TypeDefinition, GTD, GED
from ZSI.generate.pyclass import pyclass_type

##############################
# targetNamespace
# http://ws4pm.imio.be
##############################

class ns0:
    targetNamespace = "http://ws4pm.imio.be"

    class TestConnectionRequest_Def(ZSI.TCcompound.ComplexType, TypeDefinition):
        schema = "http://ws4pm.imio.be"
        type = (schema, "TestConnectionRequest")
        def __init__(self, pname, ofwhat=(), attributes=None, extend=False, restrict=False, **kw):
            ns = ns0.TestConnectionRequest_Def.schema
            TClist = [ZSI.TC.String(pname="dummy", aname="_dummy", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded"))]
            self.attribute_typecode_dict = attributes or {}
            if extend: TClist += ofwhat
            if restrict: TClist = ofwhat
            ZSI.TCcompound.ComplexType.__init__(self, None, TClist, pname=pname, inorder=0, **kw)
            class Holder:
                __metaclass__ = pyclass_type
                typecode = self
                def __init__(self):
                    # pyclass
                    self._dummy = "dummy"
                    return
            Holder.__name__ = "TestConnectionRequest_Holder"
            self.pyclass = Holder

    class CheckIsLinkedRequest_Def(ZSI.TCcompound.ComplexType, TypeDefinition):
        schema = "http://ws4pm.imio.be"
        type = (schema, "CheckIsLinkedRequest")
        def __init__(self, pname, ofwhat=(), attributes=None, extend=False, restrict=False, **kw):
            ns = ns0.CheckIsLinkedRequest_Def.schema
            TClist = [ZSI.TC.String(pname="meetingConfigId", aname="_meetingConfigId", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="externalIdentifier", aname="_externalIdentifier", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded"))]
            self.attribute_typecode_dict = attributes or {}
            if extend: TClist += ofwhat
            if restrict: TClist = ofwhat
            ZSI.TCcompound.ComplexType.__init__(self, None, TClist, pname=pname, inorder=0, **kw)
            class Holder:
                __metaclass__ = pyclass_type
                typecode = self
                def __init__(self):
                    # pyclass
                    self._meetingConfigId = None
                    self._externalIdentifier = None
                    return
            Holder.__name__ = "CheckIsLinkedRequest_Holder"
            self.pyclass = Holder

    class ConfigInfosRequest_Def(ZSI.TCcompound.ComplexType, TypeDefinition):
        schema = "http://ws4pm.imio.be"
        type = (schema, "ConfigInfosRequest")
        def __init__(self, pname, ofwhat=(), attributes=None, extend=False, restrict=False, **kw):
            ns = ns0.ConfigInfosRequest_Def.schema
            TClist = [ZSI.TC.String(pname="dummy", aname="_dummy", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded"))]
            self.attribute_typecode_dict = attributes or {}
            if extend: TClist += ofwhat
            if restrict: TClist = ofwhat
            ZSI.TCcompound.ComplexType.__init__(self, None, TClist, pname=pname, inorder=0, **kw)
            class Holder:
                __metaclass__ = pyclass_type
                typecode = self
                def __init__(self):
                    # pyclass
                    self._dummy = "dummy"
                    return
            Holder.__name__ = "ConfigInfosRequest_Holder"
            self.pyclass = Holder

    class ItemInfosRequest_Def(ZSI.TCcompound.ComplexType, TypeDefinition):
        schema = "http://ws4pm.imio.be"
        type = (schema, "ItemInfosRequest")
        def __init__(self, pname, ofwhat=(), attributes=None, extend=False, restrict=False, **kw):
            ns = ns0.ItemInfosRequest_Def.schema
            TClist = [ZSI.TC.String(pname="UID", aname="_UID", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.Boolean(pname="showExtraInfos", aname="_showExtraInfos", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.Boolean(pname="showAnnexes", aname="_showAnnexes", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.Boolean(pname="showTemplates", aname="_showTemplates", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="inTheNameOf", aname="_inTheNameOf", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded"))]
            self.attribute_typecode_dict = attributes or {}
            if extend: TClist += ofwhat
            if restrict: TClist = ofwhat
            ZSI.TCcompound.ComplexType.__init__(self, None, TClist, pname=pname, inorder=0, **kw)
            class Holder:
                __metaclass__ = pyclass_type
                typecode = self
                def __init__(self):
                    # pyclass
                    self._UID = None
                    self._showExtraInfos = 0
                    self._showAnnexes = 0
                    self._showTemplates = 0
                    self._inTheNameOf = None
                    return
            Holder.__name__ = "ItemInfosRequest_Holder"
            self.pyclass = Holder

    class ItemTemplateRequest_Def(ZSI.TCcompound.ComplexType, TypeDefinition):
        schema = "http://ws4pm.imio.be"
        type = (schema, "ItemTemplateRequest")
        def __init__(self, pname, ofwhat=(), attributes=None, extend=False, restrict=False, **kw):
            ns = ns0.ItemTemplateRequest_Def.schema
            TClist = [ZSI.TC.String(pname="itemUID", aname="_itemUID", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="templateUID", aname="_templateUID", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded"))]
            self.attribute_typecode_dict = attributes or {}
            if extend: TClist += ofwhat
            if restrict: TClist = ofwhat
            ZSI.TCcompound.ComplexType.__init__(self, None, TClist, pname=pname, inorder=0, **kw)
            class Holder:
                __metaclass__ = pyclass_type
                typecode = self
                def __init__(self):
                    # pyclass
                    self._itemUID = None
                    self._templateUID = None
                    return
            Holder.__name__ = "ItemTemplateRequest_Holder"
            self.pyclass = Holder

    class SearchItemsRequest_Def(ZSI.TCcompound.ComplexType, TypeDefinition):
        schema = "http://ws4pm.imio.be"
        type = (schema, "SearchItemsRequest")
        def __init__(self, pname, ofwhat=(), attributes=None, extend=False, restrict=False, **kw):
            ns = ns0.SearchItemsRequest_Def.schema
            TClist = [ZSI.TC.String(pname="Creator", aname="_Creator", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="Description", aname="_Description", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="SearchableText", aname="_SearchableText", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="Title", aname="_Title", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="UID", aname="_UID", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="getCategory", aname="_getCategory", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="getDecision", aname="_getDecision", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="getProposingGroup", aname="_getProposingGroup", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="portal_type", aname="_portal_type", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="review_state", aname="_review_state", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="meetingConfigId", aname="_meetingConfigId", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="externalIdentifier", aname="_externalIdentifier", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="inTheNameOf", aname="_inTheNameOf", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded"))]
            self.attribute_typecode_dict = attributes or {}
            if extend: TClist += ofwhat
            if restrict: TClist = ofwhat
            ZSI.TCcompound.ComplexType.__init__(self, None, TClist, pname=pname, inorder=0, **kw)
            class Holder:
                __metaclass__ = pyclass_type
                typecode = self
                def __init__(self):
                    # pyclass
                    self._Creator = None
                    self._Description = None
                    self._SearchableText = None
                    self._Title = None
                    self._UID = None
                    self._getCategory = None
                    self._getDecision = None
                    self._getProposingGroup = None
                    self._portal_type = None
                    self._review_state = None
                    self._meetingConfigId = None
                    self._externalIdentifier = None
                    self._inTheNameOf = None
                    return
            Holder.__name__ = "SearchItemsRequest_Holder"
            self.pyclass = Holder

    class CreateItemRequest_Def(ZSI.TCcompound.ComplexType, TypeDefinition):
        schema = "http://ws4pm.imio.be"
        type = (schema, "CreateItemRequest")
        def __init__(self, pname, ofwhat=(), attributes=None, extend=False, restrict=False, **kw):
            ns = ns0.CreateItemRequest_Def.schema
            TClist = [ZSI.TC.String(pname="meetingConfigId", aname="_meetingConfigId", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="proposingGroupId", aname="_proposingGroupId", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), GTD("http://ws4pm.imio.be","CreationData",lazy=False)(pname="creationData", aname="_creationData", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="inTheNameOf", aname="_inTheNameOf", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded"))]
            self.attribute_typecode_dict = attributes or {}
            if extend: TClist += ofwhat
            if restrict: TClist = ofwhat
            ZSI.TCcompound.ComplexType.__init__(self, None, TClist, pname=pname, inorder=0, **kw)
            class Holder:
                __metaclass__ = pyclass_type
                typecode = self
                def __init__(self):
                    # pyclass
                    self._meetingConfigId = None
                    self._proposingGroupId = None
                    self._creationData = None
                    self._inTheNameOf = None
                    return
            Holder.__name__ = "CreateItemRequest_Holder"
            self.pyclass = Holder

    class ConfigInfo_Def(ZSI.TCcompound.ComplexType, TypeDefinition):
        schema = "http://ws4pm.imio.be"
        type = (schema, "ConfigInfo")
        def __init__(self, pname, ofwhat=(), attributes=None, extend=False, restrict=False, **kw):
            ns = ns0.ConfigInfo_Def.schema
            TClist = [ZSI.TC.String(pname="UID", aname="_UID", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="id", aname="_id", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="title", aname="_title", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="description", aname="_description", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="type", aname="_type", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded"))]
            self.attribute_typecode_dict = attributes or {}
            if extend: TClist += ofwhat
            if restrict: TClist = ofwhat
            ZSI.TCcompound.ComplexType.__init__(self, None, TClist, pname=pname, inorder=0, **kw)
            class Holder:
                __metaclass__ = pyclass_type
                typecode = self
                def __init__(self):
                    # pyclass
                    self._UID = None
                    self._id = None
                    self._title = None
                    self._description = None
                    self._type = None
                    return
            Holder.__name__ = "ConfigInfo_Holder"
            self.pyclass = Holder

    class CreationData_Def(ZSI.TCcompound.ComplexType, TypeDefinition):
        schema = "http://ws4pm.imio.be"
        type = (schema, "CreationData")
        def __init__(self, pname, ofwhat=(), attributes=None, extend=False, restrict=False, **kw):
            ns = ns0.CreationData_Def.schema
            TClist = [ZSI.TC.String(pname="title", aname="_title", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="category", aname="_category", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="description", aname="_description", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="decision", aname="_decision", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="externalIdentifier", aname="_externalIdentifier", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), GTD("http://ws4pm.imio.be","AnnexInfo",lazy=False)(pname="annexes", aname="_annexes", minOccurs=0, maxOccurs=10, nillable=False, typed=False, encoded=kw.get("encoded"))]
            self.attribute_typecode_dict = attributes or {}
            if extend: TClist += ofwhat
            if restrict: TClist = ofwhat
            ZSI.TCcompound.ComplexType.__init__(self, None, TClist, pname=pname, inorder=0, **kw)
            class Holder:
                __metaclass__ = pyclass_type
                typecode = self
                def __init__(self):
                    # pyclass
                    self._title = None
                    self._category = None
                    self._description = None
                    self._decision = None
                    self._externalIdentifier = None
                    self._annexes = []
                    return
            Holder.__name__ = "CreationData_Holder"
            self.pyclass = Holder

    class AnnexInfo_Def(ZSI.TCcompound.ComplexType, TypeDefinition):
        schema = "http://ws4pm.imio.be"
        type = (schema, "AnnexInfo")
        def __init__(self, pname, ofwhat=(), attributes=None, extend=False, restrict=False, **kw):
            ns = ns0.AnnexInfo_Def.schema
            TClist = [ZSI.TC.String(pname="title", aname="_title", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="annexTypeId", aname="_annexTypeId", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="filename", aname="_filename", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.Base64String(pname="file", aname="_file", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded"))]
            self.attribute_typecode_dict = attributes or {}
            if extend: TClist += ofwhat
            if restrict: TClist = ofwhat
            ZSI.TCcompound.ComplexType.__init__(self, None, TClist, pname=pname, inorder=0, **kw)
            class Holder:
                __metaclass__ = pyclass_type
                typecode = self
                def __init__(self):
                    # pyclass
                    self._title = None
                    self._annexTypeId = None
                    self._filename = None
                    self._file = None
                    return
            Holder.__name__ = "AnnexInfo_Holder"
            self.pyclass = Holder

    class TemplateInfo_Def(ZSI.TCcompound.ComplexType, TypeDefinition):
        schema = "http://ws4pm.imio.be"
        type = (schema, "TemplateInfo")
        def __init__(self, pname, ofwhat=(), attributes=None, extend=False, restrict=False, **kw):
            ns = ns0.TemplateInfo_Def.schema
            TClist = [ZSI.TC.String(pname="title", aname="_title", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="templateType", aname="_templateType", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="templateUID", aname="_templateUID", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded"))]
            self.attribute_typecode_dict = attributes or {}
            if extend: TClist += ofwhat
            if restrict: TClist = ofwhat
            ZSI.TCcompound.ComplexType.__init__(self, None, TClist, pname=pname, inorder=0, **kw)
            class Holder:
                __metaclass__ = pyclass_type
                typecode = self
                def __init__(self):
                    # pyclass
                    self._title = None
                    self._templateType = None
                    self._templateUID = None
                    return
            Holder.__name__ = "TemplateInfo_Holder"
            self.pyclass = Holder

    class ItemInfo_Def(ZSI.TCcompound.ComplexType, TypeDefinition):
        schema = "http://ws4pm.imio.be"
        type = (schema, "ItemInfo")
        def __init__(self, pname, ofwhat=(), attributes=None, extend=False, restrict=False, **kw):
            ns = ns0.ItemInfo_Def.schema
            TClist = [ZSI.TC.String(pname="UID", aname="_UID", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="id", aname="_id", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="title", aname="_title", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="creator", aname="_creator", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="category", aname="_category", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="description", aname="_description", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="decision", aname="_decision", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="review_state", aname="_review_state", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TCtimes.gDateTime(pname="meeting_date", aname="_meeting_date", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="absolute_url", aname="_absolute_url", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="externalIdentifier", aname="_externalIdentifier", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.AnyType(pname="extraInfos", aname="_extraInfos", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), GTD("http://ws4pm.imio.be","AnnexInfo",lazy=False)(pname="annexes", aname="_annexes", minOccurs=0, maxOccurs="unbounded", nillable=False, typed=False, encoded=kw.get("encoded")), GTD("http://ws4pm.imio.be","TemplateInfo",lazy=False)(pname="templates", aname="_templates", minOccurs=0, maxOccurs="unbounded", nillable=False, typed=False, encoded=kw.get("encoded"))]
            self.attribute_typecode_dict = attributes or {}
            if extend: TClist += ofwhat
            if restrict: TClist = ofwhat
            ZSI.TCcompound.ComplexType.__init__(self, None, TClist, pname=pname, inorder=0, **kw)
            class Holder:
                __metaclass__ = pyclass_type
                typecode = self
                def __init__(self):
                    # pyclass
                    self._UID = None
                    self._id = None
                    self._title = None
                    self._creator = None
                    self._category = None
                    self._description = None
                    self._decision = None
                    self._review_state = None
                    self._meeting_date = None
                    self._absolute_url = None
                    self._externalIdentifier = None
                    self._extraInfos = None
                    self._annexes = []
                    self._templates = []
                    return
            Holder.__name__ = "ItemInfo_Holder"
            self.pyclass = Holder

    class testConnectionRequest_Dec(ElementDeclaration):
        literal = "testConnectionRequest"
        schema = "http://ws4pm.imio.be"
        substitutionGroup = None
        def __init__(self, **kw):
            kw["pname"] = (u'http://ws4pm.imio.be', u'testConnectionRequest')
            kw["aname"] = "_testConnectionRequest"
            if ns0.TestConnectionRequest_Def not in ns0.testConnectionRequest_Dec.__bases__:
                bases = list(ns0.testConnectionRequest_Dec.__bases__)
                bases.insert(0, ns0.TestConnectionRequest_Def)
                ns0.testConnectionRequest_Dec.__bases__ = tuple(bases)

            ns0.TestConnectionRequest_Def.__init__(self, **kw)
            if self.pyclass is not None: self.pyclass.__name__ = "testConnectionRequest_Dec_Holder"

    class testConnectionResponse_Dec(ZSI.TCcompound.ComplexType, ElementDeclaration):
        literal = "testConnectionResponse"
        schema = "http://ws4pm.imio.be"
        def __init__(self, **kw):
            ns = ns0.testConnectionResponse_Dec.schema
            TClist = [ZSI.TC.Boolean(pname="connectionState", aname="_connectionState", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded"))]
            kw["pname"] = (u'http://ws4pm.imio.be', u'testConnectionResponse')
            kw["aname"] = "_testConnectionResponse"
            self.attribute_typecode_dict = {}
            ZSI.TCcompound.ComplexType.__init__(self,None,TClist,inorder=0,**kw)
            class Holder:
                __metaclass__ = pyclass_type
                typecode = self
                def __init__(self):
                    # pyclass
                    self._connectionState = None
                    return
            Holder.__name__ = "testConnectionResponse_Holder"
            self.pyclass = Holder

    class checkIsLinkedRequest_Dec(ElementDeclaration):
        literal = "checkIsLinkedRequest"
        schema = "http://ws4pm.imio.be"
        substitutionGroup = None
        def __init__(self, **kw):
            kw["pname"] = (u'http://ws4pm.imio.be', u'checkIsLinkedRequest')
            kw["aname"] = "_checkIsLinkedRequest"
            if ns0.CheckIsLinkedRequest_Def not in ns0.checkIsLinkedRequest_Dec.__bases__:
                bases = list(ns0.checkIsLinkedRequest_Dec.__bases__)
                bases.insert(0, ns0.CheckIsLinkedRequest_Def)
                ns0.checkIsLinkedRequest_Dec.__bases__ = tuple(bases)

            ns0.CheckIsLinkedRequest_Def.__init__(self, **kw)
            if self.pyclass is not None: self.pyclass.__name__ = "checkIsLinkedRequest_Dec_Holder"

    class checkIsLinkedResponse_Dec(ZSI.TCcompound.ComplexType, ElementDeclaration):
        literal = "checkIsLinkedResponse"
        schema = "http://ws4pm.imio.be"
        def __init__(self, **kw):
            ns = ns0.checkIsLinkedResponse_Dec.schema
            TClist = [ZSI.TC.Boolean(pname="isLinked", aname="_isLinked", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded"))]
            kw["pname"] = (u'http://ws4pm.imio.be', u'checkIsLinkedResponse')
            kw["aname"] = "_checkIsLinkedResponse"
            self.attribute_typecode_dict = {}
            ZSI.TCcompound.ComplexType.__init__(self,None,TClist,inorder=0,**kw)
            class Holder:
                __metaclass__ = pyclass_type
                typecode = self
                def __init__(self):
                    # pyclass
                    self._isLinked = None
                    return
            Holder.__name__ = "checkIsLinkedResponse_Holder"
            self.pyclass = Holder

    class getConfigInfosRequest_Dec(ElementDeclaration):
        literal = "getConfigInfosRequest"
        schema = "http://ws4pm.imio.be"
        substitutionGroup = None
        def __init__(self, **kw):
            kw["pname"] = (u'http://ws4pm.imio.be', u'getConfigInfosRequest')
            kw["aname"] = "_getConfigInfosRequest"
            if ns0.ConfigInfosRequest_Def not in ns0.getConfigInfosRequest_Dec.__bases__:
                bases = list(ns0.getConfigInfosRequest_Dec.__bases__)
                bases.insert(0, ns0.ConfigInfosRequest_Def)
                ns0.getConfigInfosRequest_Dec.__bases__ = tuple(bases)

            ns0.ConfigInfosRequest_Def.__init__(self, **kw)
            if self.pyclass is not None: self.pyclass.__name__ = "getConfigInfosRequest_Dec_Holder"

    class getConfigInfosResponse_Dec(ZSI.TCcompound.ComplexType, ElementDeclaration):
        literal = "getConfigInfosResponse"
        schema = "http://ws4pm.imio.be"
        def __init__(self, **kw):
            ns = ns0.getConfigInfosResponse_Dec.schema
            TClist = [GTD("http://ws4pm.imio.be","ConfigInfo",lazy=False)(pname="configInfo", aname="_configInfo", minOccurs=0, maxOccurs="unbounded", nillable=False, typed=False, encoded=kw.get("encoded"))]
            kw["pname"] = (u'http://ws4pm.imio.be', u'getConfigInfosResponse')
            kw["aname"] = "_getConfigInfosResponse"
            self.attribute_typecode_dict = {}
            ZSI.TCcompound.ComplexType.__init__(self,None,TClist,inorder=0,**kw)
            class Holder:
                __metaclass__ = pyclass_type
                typecode = self
                def __init__(self):
                    # pyclass
                    self._configInfo = []
                    return
            Holder.__name__ = "getConfigInfosResponse_Holder"
            self.pyclass = Holder

    class getItemInfosRequest_Dec(ElementDeclaration):
        literal = "getItemInfosRequest"
        schema = "http://ws4pm.imio.be"
        substitutionGroup = None
        def __init__(self, **kw):
            kw["pname"] = (u'http://ws4pm.imio.be', u'getItemInfosRequest')
            kw["aname"] = "_getItemInfosRequest"
            if ns0.ItemInfosRequest_Def not in ns0.getItemInfosRequest_Dec.__bases__:
                bases = list(ns0.getItemInfosRequest_Dec.__bases__)
                bases.insert(0, ns0.ItemInfosRequest_Def)
                ns0.getItemInfosRequest_Dec.__bases__ = tuple(bases)

            ns0.ItemInfosRequest_Def.__init__(self, **kw)
            if self.pyclass is not None: self.pyclass.__name__ = "getItemInfosRequest_Dec_Holder"

    class getItemInfosResponse_Dec(ZSI.TCcompound.ComplexType, ElementDeclaration):
        literal = "getItemInfosResponse"
        schema = "http://ws4pm.imio.be"
        def __init__(self, **kw):
            ns = ns0.getItemInfosResponse_Dec.schema
            TClist = [GTD("http://ws4pm.imio.be","ItemInfo",lazy=False)(pname="itemInfo", aname="_itemInfo", minOccurs=0, maxOccurs="unbounded", nillable=False, typed=False, encoded=kw.get("encoded"))]
            kw["pname"] = (u'http://ws4pm.imio.be', u'getItemInfosResponse')
            kw["aname"] = "_getItemInfosResponse"
            self.attribute_typecode_dict = {}
            ZSI.TCcompound.ComplexType.__init__(self,None,TClist,inorder=0,**kw)
            class Holder:
                __metaclass__ = pyclass_type
                typecode = self
                def __init__(self):
                    # pyclass
                    self._itemInfo = []
                    return
            Holder.__name__ = "getItemInfosResponse_Holder"
            self.pyclass = Holder

    class getItemTemplateRequest_Dec(ElementDeclaration):
        literal = "getItemTemplateRequest"
        schema = "http://ws4pm.imio.be"
        substitutionGroup = None
        def __init__(self, **kw):
            kw["pname"] = (u'http://ws4pm.imio.be', u'getItemTemplateRequest')
            kw["aname"] = "_getItemTemplateRequest"
            if ns0.ItemTemplateRequest_Def not in ns0.getItemTemplateRequest_Dec.__bases__:
                bases = list(ns0.getItemTemplateRequest_Dec.__bases__)
                bases.insert(0, ns0.ItemTemplateRequest_Def)
                ns0.getItemTemplateRequest_Dec.__bases__ = tuple(bases)

            ns0.ItemTemplateRequest_Def.__init__(self, **kw)
            if self.pyclass is not None: self.pyclass.__name__ = "getItemTemplateRequest_Dec_Holder"

    class getItemTemplateResponse_Dec(ZSI.TCcompound.ComplexType, ElementDeclaration):
        literal = "getItemTemplateResponse"
        schema = "http://ws4pm.imio.be"
        def __init__(self, **kw):
            ns = ns0.getItemTemplateResponse_Dec.schema
            TClist = [ZSI.TC.Base64String(pname="file", aname="_file", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded"))]
            kw["pname"] = (u'http://ws4pm.imio.be', u'getItemTemplateResponse')
            kw["aname"] = "_getItemTemplateResponse"
            self.attribute_typecode_dict = {}
            ZSI.TCcompound.ComplexType.__init__(self,None,TClist,inorder=0,**kw)
            class Holder:
                __metaclass__ = pyclass_type
                typecode = self
                def __init__(self):
                    # pyclass
                    self._file = None
                    return
            Holder.__name__ = "getItemTemplateResponse_Holder"
            self.pyclass = Holder

    class searchItemsRequest_Dec(ElementDeclaration):
        literal = "searchItemsRequest"
        schema = "http://ws4pm.imio.be"
        substitutionGroup = None
        def __init__(self, **kw):
            kw["pname"] = (u'http://ws4pm.imio.be', u'searchItemsRequest')
            kw["aname"] = "_searchItemsRequest"
            if ns0.SearchItemsRequest_Def not in ns0.searchItemsRequest_Dec.__bases__:
                bases = list(ns0.searchItemsRequest_Dec.__bases__)
                bases.insert(0, ns0.SearchItemsRequest_Def)
                ns0.searchItemsRequest_Dec.__bases__ = tuple(bases)

            ns0.SearchItemsRequest_Def.__init__(self, **kw)
            if self.pyclass is not None: self.pyclass.__name__ = "searchItemsRequest_Dec_Holder"

    class searchItemsResponse_Dec(ZSI.TCcompound.ComplexType, ElementDeclaration):
        literal = "searchItemsResponse"
        schema = "http://ws4pm.imio.be"
        def __init__(self, **kw):
            ns = ns0.searchItemsResponse_Dec.schema
            TClist = [GTD("http://ws4pm.imio.be","ItemInfo",lazy=False)(pname="itemInfo", aname="_itemInfo", minOccurs=0, maxOccurs="unbounded", nillable=False, typed=False, encoded=kw.get("encoded"))]
            kw["pname"] = (u'http://ws4pm.imio.be', u'searchItemsResponse')
            kw["aname"] = "_searchItemsResponse"
            self.attribute_typecode_dict = {}
            ZSI.TCcompound.ComplexType.__init__(self,None,TClist,inorder=0,**kw)
            class Holder:
                __metaclass__ = pyclass_type
                typecode = self
                def __init__(self):
                    # pyclass
                    self._itemInfo = []
                    return
            Holder.__name__ = "searchItemsResponse_Holder"
            self.pyclass = Holder

    class createItemRequest_Dec(ElementDeclaration):
        literal = "createItemRequest"
        schema = "http://ws4pm.imio.be"
        substitutionGroup = None
        def __init__(self, **kw):
            kw["pname"] = (u'http://ws4pm.imio.be', u'createItemRequest')
            kw["aname"] = "_createItemRequest"
            if ns0.CreateItemRequest_Def not in ns0.createItemRequest_Dec.__bases__:
                bases = list(ns0.createItemRequest_Dec.__bases__)
                bases.insert(0, ns0.CreateItemRequest_Def)
                ns0.createItemRequest_Dec.__bases__ = tuple(bases)

            ns0.CreateItemRequest_Def.__init__(self, **kw)
            if self.pyclass is not None: self.pyclass.__name__ = "createItemRequest_Dec_Holder"

    class createItemResponse_Dec(ZSI.TCcompound.ComplexType, ElementDeclaration):
        literal = "createItemResponse"
        schema = "http://ws4pm.imio.be"
        def __init__(self, **kw):
            ns = ns0.createItemResponse_Dec.schema
            TClist = [ZSI.TC.String(pname="UID", aname="_UID", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="warnings", aname="_warnings", minOccurs=0, maxOccurs="unbounded", nillable=False, typed=False, encoded=kw.get("encoded"))]
            kw["pname"] = (u'http://ws4pm.imio.be', u'createItemResponse')
            kw["aname"] = "_createItemResponse"
            self.attribute_typecode_dict = {}
            ZSI.TCcompound.ComplexType.__init__(self,None,TClist,inorder=0,**kw)
            class Holder:
                __metaclass__ = pyclass_type
                typecode = self
                def __init__(self):
                    # pyclass
                    self._UID = None
                    self._warnings = []
                    return
            Holder.__name__ = "createItemResponse_Holder"
            self.pyclass = Holder

# end class ns0 (tns: http://ws4pm.imio.be)
