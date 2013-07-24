# -*- coding: utf-8 -*-
from plone.testing import z2, zca
from plone.app.testing import PloneWithPackageLayer
from plone.app.testing import IntegrationTesting, FunctionalTesting
import imio.pm.ws


WS4PM_ZCML = zca.ZCMLSandbox(filename="testing.zcml",
                             package=imio.pm.ws,
                             name='WS4PM_ZCML')

WS4PM_Z2 = z2.IntegrationTesting(bases=(z2.STARTUP, WS4PM_ZCML),
                                 name='WS4PM_Z2')

WS4PM = PloneWithPackageLayer(
    zcml_filename="testing.zcml",
    zcml_package=imio.pm.ws,
    additional_z2_products=('Products.PloneMeeting', 'Products.CMFPlacefulWorkflow', 'imio.pm.ws'),
    gs_profile_id='imio.pm.ws:default',
    name="WS4PM")

WS4PM_PM_TEST_PROFILE = PloneWithPackageLayer(
    bases=(WS4PM, ),
    zcml_filename="testing.zcml",
    zcml_package=imio.pm.ws,
    additional_z2_products=('Products.PloneMeeting', 'Products.CMFPlacefulWorkflow', 'imio.pm.ws',),
    gs_profile_id='Products.PloneMeeting:testing',
    name="WS4PM_PM_TEST_PROFILE")

WS4PM_PM_TEST_PROFILE_INTEGRATION = IntegrationTesting(
    bases=(WS4PM_PM_TEST_PROFILE,), name="WS4PM_PM_TEST_PROFILE_INTEGRATION")

WS4PM_PM_TEST_PROFILE_FUNCTIONAL = FunctionalTesting(
    bases=(WS4PM_PM_TEST_PROFILE,), name="WS4PM_PM_TEST_PROFILE_FUNCTIONAL")
