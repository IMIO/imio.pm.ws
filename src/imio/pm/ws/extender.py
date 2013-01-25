from zope.component import adapts

from zope.interface import implements
from archetypes.schemaextender.interfaces import ISchemaExtender, IBrowserLayerAwareExtender
from archetypes.schemaextender.field import ExtensionField

from interfaces import IExternalIdentifierable

from Products.PloneMeeting.interfaces import IMeetingItem

from Products.Archetypes.public import StringWidget, StringField

from imio.pm.ws.interfaces import IWS4PMLayer
from imio.pm.ws.config import EXTERNAL_IDENTIFIER_FIELD_NAME


class ExternalIdentifierStringField(ExtensionField, StringField):
    """A trivial field."""


class ExternalIdentifierExtender(object):
    """ExternalIdentifier class"""

    implements(ISchemaExtender, IBrowserLayerAwareExtender)

    #adapts elements that provide the IExternalIdentifierable marker interface
    adapts(IExternalIdentifierable)

    layer = IWS4PMLayer

    fields = [
        ExternalIdentifierStringField(EXTERNAL_IDENTIFIER_FIELD_NAME,
        required=False,
        default='',
        searchable=False,
        languageIndependent=True,
        widget = StringWidget(
                    label=(u"External identifier"),
                    description=(u"You may enter an external identifier here if the item is created using an external service"),))
            ]

    def __init__(self, context):
        self.context = context

    def getOrder(self, schematas):
        """
        """
        return schematas

    def getFields(self):
        return self.fields

