renderedWSDL = u"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<wsdl:definitions xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/" xmlns:tns="http://ws4pm.imio.be" xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" name="WS4PM" targetNamespace="http://ws4pm.imio.be">
    <wsdl:types>
        <xsd:schema targetNamespace="http://ws4pm.imio.be">
            <xsd:element name="testConnectionRequest" type="tns:TestConnectionRequest"/>
            <xsd:complexType name="TestConnectionRequest">
                <xsd:sequence>
                    <xsd:element name="dummy" type="xsd:string" maxOccurs="1" minOccurs="1" default="dummy"/>
                </xsd:sequence>
            </xsd:complexType>
            <xsd:element name="testConnectionResponse">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="connectionState" type="xsd:boolean" maxOccurs="1" minOccurs="1"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
            <xsd:element name="getConfigInfosRequest" type="tns:ConfigInfosRequest"/>
            <xsd:complexType name="ConfigInfosRequest">
                <xsd:sequence>
                    <xsd:element name="dummy" type="xsd:string" maxOccurs="1" minOccurs="1" default="dummy"/>
                </xsd:sequence>
            </xsd:complexType>
            <xsd:element name="getConfigInfosResponse">
                <xsd:complexType>
                    <xsd:sequence maxOccurs="unbounded" minOccurs="0">
                        <xsd:element name="configInfo" type="tns:ConfigInfo"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
            <xsd:element name="getItemInfosRequest" type="tns:ItemInfosRequest"/>
            <xsd:complexType name="ItemInfosRequest">
                <xsd:sequence>
                    <xsd:element name="UID" type="xsd:string" maxOccurs="1" minOccurs="1"/>
                    <xsd:element name="showExtraInfos" type="xsd:boolean" maxOccurs="1" minOccurs="1" default="0"/>
                    <xsd:element name="showAnnexes" type="xsd:boolean" maxOccurs="1" minOccurs="1" default="0"/>
                </xsd:sequence>
            </xsd:complexType>
            <xsd:element name="getItemInfosResponse">
                <xsd:complexType>
                    <xsd:sequence maxOccurs="unbounded" minOccurs="0">
                        <xsd:element name="itemInfo" type="tns:ItemInfo"/>
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
                </xsd:sequence>
            </xsd:complexType>
            <xsd:element name="searchItemsResponse">
                <xsd:complexType>
                    <xsd:sequence maxOccurs="unbounded" minOccurs="0">
                        <xsd:element name="itemInfo" type="tns:ItemInfo"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
            <xsd:element name="createItemRequest" type="tns:CreateItemRequest"/>
            <xsd:complexType name="CreateItemRequest">
                <xsd:sequence>
                    <xsd:element name="meetingConfigId" type="xsd:string" maxOccurs="1" minOccurs="1"/>
                    <xsd:element name="proposingGroupId" type="xsd:string" maxOccurs="1" minOccurs="1"/>
                    <xsd:element name="creationData" type="tns:CreationData"/>
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
            <xsd:complexType name="ItemInfo">
                <xsd:sequence>
                    <xsd:element name="UID" type="xsd:string" minOccurs="1" maxOccurs="1"/>
                    <xsd:element name="id" type="xsd:string" minOccurs="1" maxOccurs="1"/>
                    <xsd:element name="title" type="xsd:string" minOccurs="1" maxOccurs="1"/>
                    <xsd:element name="category" type="xsd:string" minOccurs="0" maxOccurs="1"/>
                    <xsd:element name="description" type="xsd:string" minOccurs="1" maxOccurs="1"/>
                    <xsd:element name="decision" type="xsd:string" minOccurs="1" maxOccurs="1"/>
                    <xsd:element name="review_state" type="xsd:string" minOccurs="1" maxOccurs="1"/>
                    <xsd:element name="meeting_date" type="xsd:dateTime" minOccurs="1" maxOccurs="1"/>
                    <xsd:element name="absolute_url" type="xsd:string" minOccurs="1" maxOccurs="1"/>
                    <xsd:element name="externalIdentifier" type="xsd:string" minOccurs="0" maxOccurs="1"/>
                    <xsd:element name="extraInfos" type="xsd:anyType"/>
                    <xsd:element name="annexes" type="tns:AnnexInfo" minOccurs="0" maxOccurs="unbounded"/>
                </xsd:sequence>
            </xsd:complexType>
        </xsd:schema>
    </wsdl:types>
    <wsdl:message name="testConnectionRequest">
        <wsdl:part name="parameters" element="tns:testConnectionRequest"/>
    </wsdl:message>
    <wsdl:message name="testConnectionResponse">
        <wsdl:part name="parameters" element="tns:testConnectionResponse"/>
    </wsdl:message>
    <wsdl:message name="getConfigInfosRequest">
        <wsdl:part name="parameters" element="tns:getConfigInfosRequest"/>
    </wsdl:message>
    <wsdl:message name="getConfigInfosResponse">
        <wsdl:part name="parameters" element="tns:getConfigInfosResponse"/>
    </wsdl:message>
    <wsdl:message name="getItemInfosRequest">
        <wsdl:part name="parameters" element="tns:getItemInfosRequest"/>
    </wsdl:message>
    <wsdl:message name="getItemInfosResponse">
        <wsdl:part name="parameters" element="tns:getItemInfosResponse"/>
    </wsdl:message>
    <wsdl:message name="searchItemsRequest">
        <wsdl:part name="parameters" element="tns:searchItemsRequest"/>
    </wsdl:message>
    <wsdl:message name="searchItemsResponse">
        <wsdl:part name="parameters" element="tns:searchItemsResponse"/>
    </wsdl:message>
    <wsdl:message name="createItemRequest">
        <wsdl:part name="parameters" element="tns:createItemRequest"/>
    </wsdl:message>
    <wsdl:message name="createItemResponse">
        <wsdl:part name="parameters" element="tns:createItemResponse"/>
    </wsdl:message>
    <wsdl:portType name="WS4PM">
        <wsdl:operation name="testConnection">
            <wsdl:input message="tns:testConnectionRequest"/>
            <wsdl:output message="tns:testConnectionResponse"/>
        </wsdl:operation>
        <wsdl:operation name="getConfigInfos">
            <wsdl:input message="tns:getConfigInfosRequest"/>
            <wsdl:output message="tns:getConfigInfosResponse"/>
        </wsdl:operation>
        <wsdl:operation name="getItemInfos">
            <wsdl:input message="tns:getItemInfosRequest"/>
            <wsdl:output message="tns:getItemInfosResponse"/>
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
    <wsdl:binding name="WS4PMSOAP" type="tns:WS4PM">
        <soap:binding style="document" transport="http://schemas.xmlsoap.org/soap/http"/>
        <wsdl:operation name="testConnection">
            <xsd:annotation>
                <xsd:documentation> Method for testing the connection to the server Webservice </xsd:documentation>
            </xsd:annotation>
            <soap:operation soapAction="http://ws4pm.imio.be/testConnection"/>
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
        <wsdl:port binding="tns:WS4PMSOAP" name="WS4PMSOAP">
            <soap:address location="http://nohost/plone"/>
        </wsdl:port>
    </wsdl:service>
</wsdl:definitions>"""