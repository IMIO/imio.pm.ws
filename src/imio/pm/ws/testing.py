# -*- coding: utf-8 -*-
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.testing import z2
from plone.testing import zca
from Products.PloneMeeting.testing import PMLayer

import imio.pm.ws


class WSLayer(PMLayer):
    """ """


WS4PM_ZCML = zca.ZCMLSandbox(filename="testing.zcml",
                             package=imio.pm.ws,
                             name='WS4PM_ZCML')

WS4PM_Z2 = z2.IntegrationTesting(bases=(z2.STARTUP, WS4PM_ZCML),
                                 name='WS4PM_Z2')

WS4PM_PM_TEST_PROFILE = WSLayer(
    zcml_filename="testing.zcml",
    zcml_package=imio.pm.ws,
    additional_z2_products=('imio.dashboard',
                            'Products.PloneMeeting',
                            'Products.CMFPlacefulWorkflow',
                            'Products.PasswordStrength'),
    gs_profile_id='Products.PloneMeeting:testing',
    name="WS4PM_PM_TEST_PROFILE")

WS4PM_PM_TEST_PROFILE_INTEGRATION = IntegrationTesting(
    bases=(WS4PM_PM_TEST_PROFILE,), name="WS4PM_PM_TEST_PROFILE_INTEGRATION")

WS4PM_PM_TEST_PROFILE_FUNCTIONAL = FunctionalTesting(
    bases=(WS4PM_PM_TEST_PROFILE,), name="WS4PM_PM_TEST_PROFILE_FUNCTIONAL")
