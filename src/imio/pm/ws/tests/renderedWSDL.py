renderedWSDL = u"""<?xml version="1.0" encoding="UTF-8"?>
<wsdl:definitions xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/" xmlns:tns="http://ws4pm.imio.be" xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" name="WS4PM" targetNamespace="http://ws4pm.imio.be">
    <wsdl:types>
        <xsd:schema targetNamespace="http://ws4pm.imio.be">
            <xsd:element name="testConnectionRequest" type="tns:TestConnectionRequest"/>
            <xsd:complexType name="TestConnectionRequest">
                <xsd:sequence>
                    <xsd:element name="dummy" type="xsd:string" maxOccurs="1" minOccurs="0" default="dummy"/>
                </xsd:sequence>
            </xsd:complexType>
            <xsd:element name="testConnectionResponse">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="connectionState" type="xsd:boolean" maxOccurs="1" minOccurs="1"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
            <xsd:element name="checkIsLinkedRequest" type="tns:CheckIsLinkedRequest"/>
            <xsd:complexType name="CheckIsLinkedRequest">
                <xsd:sequence>
                    <xsd:element name="meetingConfigId" type="xsd:string" maxOccurs="1" minOccurs="0"/>
                    <xsd:element name="externalIdentifier" type="xsd:string" minOccurs="1" maxOccurs="1"/>
                </xsd:sequence>
            </xsd:complexType>
            <xsd:element name="checkIsLinkedResponse">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="isLinked" type="xsd:boolean" maxOccurs="1" minOccurs="1"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
            <xsd:element name="getConfigInfosRequest" type="tns:ConfigInfosRequest"/>
            <xsd:complexType name="ConfigInfosRequest">
                <xsd:sequence>
                    <xsd:element name="showCategories" type="xsd:boolean" maxOccurs="1" minOccurs="1" default="0"/>
                    <xsd:element name="userToShowCategoriesFor" type="xsd:string" maxOccurs="1" minOccurs="0"/>
                </xsd:sequence>
            </xsd:complexType>
            <xsd:element name="getConfigInfosResponse">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="configInfo" type="tns:ConfigInfo" maxOccurs="unbounded" minOccurs="0"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
            <xsd:element name="getUserInfosRequest" type="tns:UserInfosRequest"/>
            <xsd:complexType name="UserInfosRequest">
                <xsd:sequence>
                    <xsd:element name="userId" type="xsd:string" maxOccurs="1" minOccurs="1"/>
                    <xsd:element name="showGroups" type="xsd:boolean" maxOccurs="1" minOccurs="1" default="0"/>
                    <xsd:element name="suffix" type="xsd:string" maxOccurs="1" minOccurs="0"/>
                </xsd:sequence>
            </xsd:complexType>
            <xsd:element name="getUserInfosResponse">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="fullname" type="xsd:string" maxOccurs="1" minOccurs="1"/>
                        <xsd:element name="email" type="xsd:string" maxOccurs="1" minOccurs="1"/>
                        <xsd:element name="groups" type="tns:BasicInfo" maxOccurs="unbounded" minOccurs="0"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
            <xsd:element name="getItemInfosRequest" type="tns:ItemInfosRequest"/>
            <xsd:complexType name="ItemInfosRequest">
                <xsd:sequence>
                    <xsd:element name="UID" type="xsd:string" maxOccurs="1" minOccurs="1"/>
                    <xsd:element name="showExtraInfos" type="xsd:boolean" maxOccurs="1" minOccurs="1" default="0"/>
                    <xsd:element name="showAnnexes" type="xsd:boolean" maxOccurs="1" minOccurs="1" default="0"/>
                    <xsd:element name="showTemplates" type="xsd:boolean" maxOccurs="1" minOccurs="0" default="0"/>
                    <xsd:element name="inTheNameOf" type="xsd:string" maxOccurs="1" minOccurs="0"/>
                </xsd:sequence>
            </xsd:complexType>
            <xsd:element name="getItemInfosResponse">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="itemInfo" type="tns:ItemInfo" maxOccurs="unbounded" minOccurs="0"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
            <xsd:element name="getItemTemplateRequest" type="tns:ItemTemplateRequest"/>
            <xsd:complexType name="ItemTemplateRequest">
                <xsd:sequence>
                    <xsd:element name="itemUID" type="xsd:string" maxOccurs="1" minOccurs="1"/>
                    <xsd:element name="templateId" type="xsd:string" maxOccurs="1" minOccurs="1"/>
                    <xsd:element name="inTheNameOf" type="xsd:string" maxOccurs="1" minOccurs="0"/>
                </xsd:sequence>
            </xsd:complexType>
            <xsd:element name="getItemTemplateResponse">
                <xsd:complexType name="ItemTemplateResponse">
                    <xsd:sequence>
                        <xsd:element name="file" type="xsd:base64Binary" minOccurs="1" maxOccurs="1"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
            <xsd:element name="searchItemsRequest" type="tns:SearchItemsRequest"/>
            <xsd:complexType name="SearchItemsRequest">
                <xsd:sequence>
                    <xsd:element name="Creator" type="xsd:string" maxOccurs="1" minOccurs="0"/>
                    <xsd:element name="Description" type="xsd:string" maxOccurs="1" minOccurs="0"/>
                    <xsd:element name="SearchableText" type="xsd:string" maxOccurs="1" minOccurs="0"/>
                    <xsd:element name="Title" type="xsd:string" maxOccurs="1" minOccurs="0"/>
                    <xsd:element name="UID" type="xsd:string" maxOccurs="1" minOccurs="0"/>
                    <xsd:element name="getCategory" type="xsd:string" maxOccurs="1" minOccurs="0"/>
                    <xsd:element name="getDecision" type="xsd:string" maxOccurs="1" minOccurs="0"/>
                    <xsd:element name="getProposingGroup" type="xsd:string" maxOccurs="1" minOccurs="0"/>
                    <xsd:element name="portal_type" type="xsd:string" maxOccurs="1" minOccurs="0"/>
                    <xsd:element name="review_state" type="xsd:string" maxOccurs="1" minOccurs="0"/>
                    <xsd:element name="meetingConfigId" type="xsd:string" maxOccurs="1" minOccurs="0"/>
                    <xsd:element name="externalIdentifier" type="xsd:string" minOccurs="0" maxOccurs="1"/>
                    <xsd:element name="inTheNameOf" type="xsd:string" maxOccurs="1" minOccurs="0"/>
                </xsd:sequence>
            </xsd:complexType>
            <xsd:element name="searchItemsResponse">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="itemInfo" type="tns:ItemInfo" maxOccurs="unbounded" minOccurs="0"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
            <xsd:element name="createItemRequest" type="tns:CreateItemRequest"/>
            <xsd:complexType name="CreateItemRequest">
                <xsd:sequence>
                    <xsd:element name="meetingConfigId" type="xsd:string" maxOccurs="1" minOccurs="1"/>
                    <xsd:element name="proposingGroupId" type="xsd:string" maxOccurs="1" minOccurs="1"/>
                    <xsd:element name="creationData" type="tns:CreationData"/>
                    <xsd:element name="inTheNameOf" type="xsd:string" maxOccurs="1" minOccurs="0"/>
                </xsd:sequence>
            </xsd:complexType>
            <xsd:element name="createItemResponse">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="UID" type="xsd:string" maxOccurs="1" minOccurs="1"/>
                        <xsd:element name="warnings" type="xsd:string" maxOccurs="unbounded" minOccurs="0"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
            <xsd:complexType name="ConfigInfo">
                <xsd:sequence>
                    <xsd:element name="UID" type="xsd:string" minOccurs="1" maxOccurs="1"/>
                    <xsd:element name="id" type="xsd:string" minOccurs="1" maxOccurs="1"/>
                    <xsd:element name="title" type="xsd:string" minOccurs="1" maxOccurs="1"/>
                    <xsd:element name="description" type="xsd:string" minOccurs="1" maxOccurs="1"/>
                    <xsd:element name="type" type="xsd:string" minOccurs="1" maxOccurs="1"/>
                    <xsd:element name="categories" type="tns:BasicInfo" minOccurs="0" maxOccurs="unbounded"/>
                </xsd:sequence>
            </xsd:complexType>
            <xsd:complexType name="BasicInfo">
                <xsd:sequence>
                    <xsd:element name="UID" type="xsd:string" minOccurs="1" maxOccurs="1"/>
                    <xsd:element name="id" type="xsd:string" minOccurs="1" maxOccurs="1"/>
                    <xsd:element name="title" type="xsd:string" minOccurs="1" maxOccurs="1"/>
                    <xsd:element name="description" type="xsd:string" minOccurs="1" maxOccurs="1"/>
                    <xsd:element name="suffix" type="xsd:string" minOccurs="1" maxOccurs="unbounded"/>
                </xsd:sequence>
            </xsd:complexType>
            <xsd:complexType name="CreationData">
                <xsd:sequence>
                    <xsd:element name="title" type="xsd:string" minOccurs="1" maxOccurs="1"/>
                    <xsd:element name="category" type="xsd:string" minOccurs="0" maxOccurs="1"/>
                    <xsd:element name="description" type="xsd:string" minOccurs="0" maxOccurs="1"/>
                    <xsd:element name="decision" type="xsd:string" minOccurs="0" maxOccurs="1"/>
                    <xsd:element name="externalIdentifier" type="xsd:string" minOccurs="0" maxOccurs="1"/>
                    <xsd:element name="annexes" type="tns:AnnexInfo" minOccurs="0" maxOccurs="10"/>
                </xsd:sequence>
            </xsd:complexType>
            <xsd:complexType name="AnnexInfo">
                <xsd:sequence>
                    <xsd:element name="title" type="xsd:string" minOccurs="1" maxOccurs="1"/>
                    <xsd:element name="annexTypeId" type="xsd:string" minOccurs="0" maxOccurs="1"/>
                    <xsd:element name="filename" type="xsd:string" minOccurs="0" maxOccurs="1"/>
                    <xsd:element name="file" type="xsd:base64Binary" minOccurs="1" maxOccurs="1"/>
                </xsd:sequence>
            </xsd:complexType>
            <xsd:complexType name="TemplateInfo">
                <xsd:sequence>
                    <xsd:element name="title" type="xsd:string" minOccurs="1" maxOccurs="1"/>
                    <xsd:element name="templateFormat" type="xsd:string" minOccurs="1" maxOccurs="1"/>
                    <xsd:element name="templateId" type="xsd:string" minOccurs="1" maxOccurs="1"/>
                    <xsd:element name="templateFilename" type="xsd:string" minOccurs="1" maxOccurs="1"/>
                </xsd:sequence>
            </xsd:complexType>
            <xsd:complexType name="ItemInfo">
                <xsd:sequence>
                    <xsd:element name="UID" type="xsd:string" minOccurs="1" maxOccurs="1"/>
                    <xsd:element name="id" type="xsd:string" minOccurs="1" maxOccurs="1"/>
                    <xsd:element name="title" type="xsd:string" minOccurs="1" maxOccurs="1"/>
                    <xsd:element name="creator" type="xsd:string" maxOccurs="1" minOccurs="1"/>
                    <xsd:element name="category" type="xsd:string" minOccurs="0" maxOccurs="1"/>
                    <xsd:element name="description" type="xsd:string" minOccurs="1" maxOccurs="1"/>
                    <xsd:element name="decision" type="xsd:string" minOccurs="1" maxOccurs="1"/>
                    <xsd:element name="review_state" type="xsd:string" minOccurs="1" maxOccurs="1"/>
                    <xsd:element name="meeting_date" type="xsd:dateTime" minOccurs="1" maxOccurs="1"/>
                    <xsd:element name="absolute_url" type="xsd:string" minOccurs="1" maxOccurs="1"/>
                    <xsd:element name="externalIdentifier" type="xsd:string" minOccurs="0" maxOccurs="1"/>
                    <xsd:element name="extraInfos" type="xsd:anyType"/>
                    <xsd:element name="annexes" type="tns:AnnexInfo" minOccurs="0" maxOccurs="unbounded"/>
                    <xsd:element name="templates" type="tns:TemplateInfo" minOccurs="0" maxOccurs="unbounded"/>
                </xsd:sequence>
            </xsd:complexType>
        </xsd:schema>
    </wsdl:types>
    <wsdl:message name="testConnectionRequest">
        <wsdl:part name="parameters" element="tns:testConnectionRequest"/>
    </wsdl:message>
    <wsdl:message name="testConnectionResponse">
        <wsdl:part name="return" element="tns:testConnectionResponse"/>
    </wsdl:message>
    <wsdl:message name="checkIsLinkedRequest">
        <wsdl:part name="parameters" element="tns:checkIsLinkedRequest"/>
    </wsdl:message>
    <wsdl:message name="checkIsLinkedResponse">
        <wsdl:part name="return" element="tns:checkIsLinkedResponse"/>
    </wsdl:message>
    <wsdl:message name="getConfigInfosRequest">
        <wsdl:part name="parameters" element="tns:getConfigInfosRequest"/>
    </wsdl:message>
    <wsdl:message name="getConfigInfosResponse">
        <wsdl:part name="return" element="tns:getConfigInfosResponse"/>
    </wsdl:message>
    <wsdl:message name="getUserInfosRequest">
        <wsdl:part name="parameters" element="tns:getUserInfosRequest"/>
    </wsdl:message>
    <wsdl:message name="getUserInfosResponse">
        <wsdl:part name="return" element="tns:getUserInfosResponse"/>
    </wsdl:message>
    <wsdl:message name="getItemInfosRequest">
        <wsdl:part name="parameters" element="tns:getItemInfosRequest"/>
    </wsdl:message>
    <wsdl:message name="getItemInfosResponse">
        <wsdl:part name="return" element="tns:getItemInfosResponse"/>
    </wsdl:message>
    <wsdl:message name="getItemTemplateRequest">
        <wsdl:part name="parameters" element="tns:getItemTemplateRequest"/>
    </wsdl:message>
    <wsdl:message name="getItemTemplateResponse">
        <wsdl:part name="return" element="tns:getItemTemplateResponse"/>
    </wsdl:message>
    <wsdl:message name="searchItemsRequest">
        <wsdl:part name="parameters" element="tns:searchItemsRequest"/>
    </wsdl:message>
    <wsdl:message name="searchItemsResponse">
        <wsdl:part name="return" element="tns:searchItemsResponse"/>
    </wsdl:message>
    <wsdl:message name="createItemRequest">
        <wsdl:part name="parameters" element="tns:createItemRequest"/>
    </wsdl:message>
    <wsdl:message name="createItemResponse">
        <wsdl:part name="return" element="tns:createItemResponse"/>
    </wsdl:message>
    <wsdl:portType name="WS4PMPortType">
        <wsdl:operation name="testConnection">
            <wsdl:input message="tns:testConnectionRequest"/>
            <wsdl:output message="tns:testConnectionResponse"/>
        </wsdl:operation>
        <wsdl:operation name="checkIsLinked">
            <wsdl:input message="tns:checkIsLinkedRequest"/>
            <wsdl:output message="tns:checkIsLinkedResponse"/>
        </wsdl:operation>
        <wsdl:operation name="getConfigInfos">
            <wsdl:input message="tns:getConfigInfosRequest"/>
            <wsdl:output message="tns:getConfigInfosResponse"/>
        </wsdl:operation>
        <wsdl:operation name="getUserInfos">
            <wsdl:input message="tns:getUserInfosRequest"/>
            <wsdl:output message="tns:getUserInfosResponse"/>
        </wsdl:operation>
        <wsdl:operation name="getItemInfos">
            <wsdl:input message="tns:getItemInfosRequest"/>
            <wsdl:output message="tns:getItemInfosResponse"/>
        </wsdl:operation>
        <wsdl:operation name="getItemTemplate">
            <wsdl:input message="tns:getItemTemplateRequest"/>
            <wsdl:output message="tns:getItemTemplateResponse"/>
        </wsdl:operation>
        <wsdl:operation name="searchItems">
            <wsdl:input message="tns:searchItemsRequest"/>
            <wsdl:output message="tns:searchItemsResponse"/>
        </wsdl:operation>
        <wsdl:operation name="createItem">
            <wsdl:input message="tns:createItemRequest"/>
            <wsdl:output message="tns:createItemResponse"/>
        </wsdl:operation>
    </wsdl:portType>
    <wsdl:binding name="WS4PMSOAPBinding" type="tns:WS4PMPortType">
        <soap:binding style="document" transport="http://schemas.xmlsoap.org/soap/http"/>
        <wsdl:operation name="testConnection">
            <xsd:annotation>
                <xsd:documentation> Method for testing the connection to the server Webservice </xsd:documentation>
            </xsd:annotation>
            <soap:operation soapAction="http://nohost/plone/testConnection"/>
            <wsdl:input>
                <soap:body use="literal"/>
            </wsdl:input>
            <wsdl:output>
                <soap:body use="literal"/>
            </wsdl:output>
        </wsdl:operation>
        <wsdl:operation name="checkIsLinked">
            <xsd:annotation>
                <xsd:documentation> Method for checking that an element is already linked to an existing item in PloneMeeting </xsd:documentation>
            </xsd:annotation>
            <soap:operation soapAction="http://nohost/plone/checkIsLinked"/>
            <wsdl:input>
                <soap:body use="literal"/>
            </wsdl:input>
            <wsdl:output>
                <soap:body use="literal"/>
            </wsdl:output>
        </wsdl:operation>
        <wsdl:operation name="getConfigInfos">
            <xsd:annotation>
                <xsd:documentation> Method for getting informations about the configuration </xsd:documentation>
            </xsd:annotation>
            <soap:operation soapAction="http://nohost/plone/getConfigInfos"/>
            <wsdl:input>
                <soap:body use="literal"/>
            </wsdl:input>
            <wsdl:output>
                <soap:body use="literal"/>
            </wsdl:output>
        </wsdl:operation>
        <wsdl:operation name="getUserInfos">
            <xsd:annotation>
                <xsd:documentation> Method for getting informations about a given user </xsd:documentation>
            </xsd:annotation>
            <soap:operation soapAction="http://nohost/plone/getUserInfos"/>
            <wsdl:input>
                <soap:body use="literal"/>
            </wsdl:input>
            <wsdl:output>
                <soap:body use="literal"/>
            </wsdl:output>
        </wsdl:operation>
        <wsdl:operation name="getItemInfos">
            <xsd:annotation>
                <xsd:documentation> Method for getting informations about a precise item you know the UID of </xsd:documentation>
            </xsd:annotation>
            <soap:operation soapAction="http://nohost/plone/getItemInfos"/>
            <wsdl:input>
                <soap:body use="literal"/>
            </wsdl:input>
            <wsdl:output>
                <soap:body use="literal"/>
            </wsdl:output>
        </wsdl:operation>
        <wsdl:operation name="getItemTemplate">
            <xsd:annotation>
                <xsd:documentation> Method for getting a specific generated template from PloneMeeting for a given item </xsd:documentation>
            </xsd:annotation>
            <soap:operation soapAction="http://nohost/plone/getItemTemplate"/>
            <wsdl:input>
                <soap:body use="literal"/>
            </wsdl:input>
            <wsdl:output>
                <soap:body use="literal"/>
            </wsdl:output>
        </wsdl:operation>
        <wsdl:operation name="searchItems">
            <xsd:annotation>
                <xsd:documentation> Method for getting informations about items using search parameters </xsd:documentation>
            </xsd:annotation>
            <soap:operation soapAction="http://nohost/plone/searchItems"/>
            <wsdl:input>
                <soap:body use="literal"/>
            </wsdl:input>
            <wsdl:output>
                <soap:body use="literal"/>
            </wsdl:output>
        </wsdl:operation>
        <wsdl:operation name="createItem">
            <xsd:annotation>
                <xsd:documentation> Method for creating an item with annexes </xsd:documentation>
            </xsd:annotation>
            <soap:operation soapAction="http://nohost/plone/createItem"/>
            <wsdl:input>
                <soap:body use="literal"/>
            </wsdl:input>
            <wsdl:output>
                <soap:body use="literal"/>
            </wsdl:output>
        </wsdl:operation>
    </wsdl:binding>
    <wsdl:service name="WS4PM">
        <wsdl:port binding="tns:WS4PMSOAPBinding" name="WS4PMSOAP">
            <soap:address location="http://nohost/plone"/>
        </wsdl:port>
    </wsdl:service>
</wsdl:definitions>"""
