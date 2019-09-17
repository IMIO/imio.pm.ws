# -*- coding: utf-8 -*-

from imio.pm.ws.tests.WS4PMTestCase import WS4PMTestCase


class testSetup(WS4PMTestCase):
    """
        Tests the setup : install/uninstall process and WSDL
    """

    def test_ws_uninstall(self):
        """
          At uninstall time, we remove the BrowserLayer that makes
          schemaextender and ws4pm.wsdl available.  We also remove the added indexes/columns.
        """
        # by default, the WSDL is available and the schemaextender
        self.assertEquals(self.portal.restrictedTraverse('@@ws4pm.wsdl').context.absolute_url(),
                          self.portal.absolute_url())
        self.changeUser('pmManager')
        item = self.create('MeetingItem')
        self.failUnless('externalIdentifier' in item.Schema().keys())
        # the BrowserLayer is registered
        from imio.pm.ws.interfaces import IWS4PMLayer
        from plone.browserlayer.utils import registered_layers
        self.failUnless(IWS4PMLayer in registered_layers())
        # portal_catalog contains an index and a metadata for "externalIdentifier"
        self.failUnless("externalIdentifier" in self.portal.portal_catalog.indexes())
        self.failUnless("externalIdentifier" in self.portal.portal_catalog.schema())
        # now uninstall imio.pm.ws
        self.portal.portal_setup.runAllImportStepsFromProfile('profile-imio.pm.ws:uninstall')
        # no more schemaextender
        self.failIf('externalIdentifier' in item.Schema().keys())
        # the WSDL is no more available
        # this does not seem to work in tests?  While uninstalling the BrowserLayer
        # the BrowserView ws4pm.wsdl is still available... ???
        # but the BrowserLayer is no more registered...
        self.failIf(IWS4PMLayer in registered_layers())
        # indexes/metadatas are removed from portal_catalog
        self.failIf("externalIdentifier" in self.portal.portal_catalog.indexes())
        self.failIf("externalIdentifier" in self.portal.portal_catalog.schema())


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    # add a prefix because we heritate from testMeeting and we do not want every tests of testMeeting to be run here...
    suite.addTest(makeSuite(testSetup, prefix='test_ws_'))
    return suite
