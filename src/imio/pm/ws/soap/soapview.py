# -*- coding: utf-8 -*-

from AccessControl import Unauthorized
from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from BeautifulSoup import BeautifulSoup
from collective.contact.plonegroup.utils import get_organizations
from collective.iconifiedcategory.utils import calculate_category_id
from DateTime import DateTime
from HTMLParser import HTMLParser
from imio.helpers.content import get_user_fullname
from imio.helpers.content import get_vocab
from imio.helpers.content import uuidToObject
from imio.history.utils import add_event_to_wf_history
from imio.pm.ws.config import EXTERNAL_IDENTIFIER_FIELD_NAME
from imio.pm.ws.config import MAIN_DATA_FROM_ITEM_SCHEMA
from imio.pm.ws.config import POD_TEMPLATE_ID_PATTERN
from imio.pm.ws.soap.basetypes import AnnexInfo
from imio.pm.ws.soap.basetypes import BasicInfo
from imio.pm.ws.soap.basetypes import ConfigInfo
from imio.pm.ws.soap.basetypes import GroupInfo
from imio.pm.ws.soap.basetypes import ItemInfo
from imio.pm.ws.soap.basetypes import MeetingInfo
from imio.pm.ws.soap.basetypes import TemplateInfo
from lxml.html.clean import Cleaner
from magic import MagicException
from plone import api
from plone import namedfile
from plone.dexterity.utils import createContentInContainer
from Products.Archetypes.atapi import RichWidget
from Products.CMFPlone.utils import safe_unicode
from Products.Five import BrowserView
from Products.PloneMeeting.browser.overrides import PMDocumentGeneratorLinksViewlet
from Products.PloneMeeting.config import ITEM_NO_PREFERRED_MEETING_VALUE
from Products.PloneMeeting.MeetingItem import MeetingItem
from Products.PloneMeeting.utils import get_annexes
from Products.PloneMeeting.utils import org_id_to_uid
from time import localtime
from zope.i18n import translate

import logging
import magic
import os
import ZSI


logger = logging.getLogger('WS4PM')

WRONG_HTML_WARNING = "HTML used for creating the item at '${item_path}' by '${creator}' was not valid. " \
                     "Used corrected HTML."
MIMETYPE_NOT_FOUND_OF_ANNEX_WARNING = "Mimetype could not be determined correctly for annex '${annex_path}' of " \
                                      "item '${item_path}', this annex was not added."
NO_EXTENSION_FOR_MIMETYPE_OF_ANNEX_WARNING = "No extension available in mimetypes_registry for mimetype '${mime}' " \
                                             "for annex '${annex_path}' of item '${item_path}', " \
                                             "this annex was not added."
MULTIPLE_EXTENSION_FOR_MIMETYPE_OF_ANNEX_WARNING = "Could not determine an extension to use for mimetype '${mime}', " \
                                                   "too many available, for annex '${annex_path}' of " \
                                                   "item '${item_path}', this annex was not added."
ITEM_SOAP_CREATED = "create_item_using_imio_pm_ws_soap"


def setup_user_in_the_name_of(portal, member):
    """ """
    # remove AUTHENTICATED_USER during adopt_user to avoid
    # breaking utils.get_current_user_id
    original_auth_user = portal.REQUEST.get("AUTHENTICATED_USER")
    if original_auth_user:
        portal.REQUEST["AUTHENTICATED_USER"] = None

    oldsm = getSecurityManager()
    newSecurityManager(portal.REQUEST, member)
    return oldsm, original_auth_user


def teardown_user_in_the_name_of(portal, oldsm, original_auth_user):
    """ """
    setSecurityManager(oldsm)
    portal.REQUEST["AUTHENTICATED_USER"] = original_auth_user


def raiseMsg(msg):
    """ """
    logger.error(msg)
    raise ZSI.Fault(ZSI.Fault.Client, msg)


class SOAPView(BrowserView):
    """
      class delivering SOAP methods for Products.PloneMeeting
    """

    def testConnectionRequest(self, request, response):
        '''
          This is the accessed SOAP method for testing the connection to the webservices
          This method is usefull for SOAP clients
        '''
        response._connectionState, response._version = self._testConnection()
        return response

    def checkIsLinkedRequest(self, request, response):
        '''
          This is the accessed SOAP method for checking if an element as already a given externalIdentifier
          This perform an unrestritedSearchResutls that is why it only returns True or False
          Only a 'Manager' or 'MeetingManager' can do this request
        '''
        response._isLinked = self._checkIsLinked(request._meetingConfigId, request._externalIdentifier)
        return response

    def getConfigInfosRequest(self, request, response):
        '''
          This is the accessed SOAP method for getting informations about the configuration
          This will return a list of key elements of the config with the type of element
        '''
        response._configInfo, response._groupInfo = \
            self._getConfigInfos(request._showCategories, request._userToShowCategoriesFor)
        return response

    def getUserInfosRequest(self, request, response):
        '''
          This is the accessed SOAP method for getting informations about an existing user
        '''
        response._fullname, response._email, response._groups = self._getUserInfos(request._userId,
                                                                                   request._showGroups,
                                                                                   request._suffix)
        return response

    def searchItemsRequest(self, request, response):
        '''
          This is the accessed SOAP method for searching items
        '''
        params = dict(request.__dict__)
        # remove the '_inTheNameOf' from searchParams as it is not a search parameter
        inTheNameOf = None
        if '_inTheNameOf' in params:
            inTheNameOf = params['_inTheNameOf']
            params.pop('_inTheNameOf')
        response._itemInfo = self._getItemInfos(params, inTheNameOf=inTheNameOf)
        return response

    def getItemInfosRequest(self, request, response):
        '''
          This is the accessed SOAP method for getting informations about an existing item
          This is an helper method when you just need to access an item you know the UID of
        '''
        params = dict(request.__dict__)
        # remove params that are not search parameter
        if '_showExtraInfos' in params:
            params.pop('_showExtraInfos')
        if '_showAnnexes' in params:
            params.pop('_showAnnexes')
        if '_allowed_annexes_types' in params:
            params.pop('_allowed_annexes_types')
        if '_include_annex_binary' in params:
            params.pop('_include_annex_binary')
        if '_showAssembly' in params:
            params.pop('_showAssembly')
        if '_showTemplates' in params:
            params.pop('_showTemplates')
        showEmptyValues = True
        if '_showEmptyValues' in params:
            showEmptyValues = params.pop('_showEmptyValues')
        inTheNameOf = None
        if '_inTheNameOf' in params:
            inTheNameOf = params.pop('_inTheNameOf')

        infos = self._getItemInfos(
            params,
            request.__dict__.get('_showExtraInfos', False),
            request.__dict__.get('_showAnnexes', False),
            request.__dict__.get('_allowed_annexes_types', []),
            request.__dict__.get('_include_annex_binary', True),
            request.__dict__.get('_showAssembly', False),
            request.__dict__.get('_showTemplates', False),
            inTheNameOf)
        if infos and not showEmptyValues:
            # remove empty data
            for k, v in infos[0].__dict__.items():
                if not v:
                    delattr(infos[0], k)
        response._itemInfo = infos
        return response

    def getSingleItemInfosRequest(self, request, response):
        '''
          This is the accessed SOAP method for getting informations about an existing item
          This is an helper method when you just need to access an item you know the UID of
        '''
        params = dict(request.__dict__)

        # remove params that are not search parameter
        if '_showExtraInfos' in params:
            params.pop('_showExtraInfos')
        if '_showAnnexes' in params:
            params.pop('_showAnnexes')
        if '_allowed_annexes_types' in params:
            params.pop('_allowed_annexes_types')
        if '_include_annex_binary' in params:
            params.pop('_include_annex_binary')
        if '_showAssembly' in params:
            params.pop('_showAssembly')
        if '_showTemplates' in params:
            params.pop('_showTemplates')
        showEmptyValues = True
        if '_showEmptyValues' in params:
            showEmptyValues = params.pop('_showEmptyValues')
        inTheNameOf = None
        if '_inTheNameOf' in params:
            inTheNameOf = params.pop('_inTheNameOf')

        infos = self._getItemInfos(
            params,
            request.__dict__.get('_showExtraInfos', False),
            request.__dict__.get('_showAnnexes', False),
            request.__dict__.get('_allowed_annexes_types', []),
            request.__dict__.get('_include_annex_binary', True),
            request.__dict__.get('_showAssembly', False),
            request.__dict__.get('_showTemplates', False),
            inTheNameOf)
        if infos:
            if not showEmptyValues:
                # remove empty data
                for k, v in infos[0].__dict__.items():
                    if not v:
                        delattr(infos[0], k)
            response.__dict__ = infos[0].__dict__
        else:
            response.__dict__ = {}
        return response

    def getItemTemplateRequest(self, request, response):
        '''
          This is the accessed SOAP method for getting a generated version of a given template
        '''
        response._file = self._getItemTemplate(request._itemUID,
                                               request._templateId,
                                               request._inTheNameOf)
        return response

    def meetingsAcceptingItemsRequest(self, request, response):
        '''
          This is the accessed SOAP method for getting meetings that accept items in a given meeting config
        '''
        response._meetingInfo = self._meetingsAcceptingItems(request._meetingConfigId,
                                                             request._inTheNameOf)
        return response

    def createItemRequest(self, request, response):
        '''
          This is the accessed SOAP method for creating an item
        '''
        response._UID, response._warnings = self._createItem(request._meetingConfigId,
                                                             request._proposingGroupId,
                                                             request._creationData,
                                                             request._cleanHtml,
                                                             request._wfTransitions,
                                                             request._inTheNameOf)
        return response

    def _testConnection(self):
        '''
          Test current connection state
        '''
        portal = self.context

        # in case this method is accessed without valid credrentials, raise Unauthorized
        if api.user.is_anonymous():
            raise Unauthorized

        logger.info('Test connection SOAP made at "%s".' % portal.absolute_url_path())
        version = api.env.get_distribution('imio.pm.ws')._version
        return True, version

    def _checkIsLinked(self, meetingConfigId, externalIdentifier):
        '''
          Test if an element in PloneMeeting is linked to given meetingConfig/externalIdentifier
        '''
        portal = self.context

        # this is only available to 'Manager' and 'MeetingManager'
        if not self._mayAccessAdvancedFunctionnalities():
            raiseMsg(
                "You need to be 'Manager' or 'MeetingManager' to check if an element is linked to an item!")

        # perform the unrestrictedSearchResult
        tool = api.portal.get_tool('portal_plonemeeting')
        # if a meetingConfigId is given, check that it exists
        query = {}
        if meetingConfigId:
            mc = getattr(tool, meetingConfigId, None)
            if not mc or not mc.meta_type == 'MeetingConfig':
                raiseMsg("Unknown meetingConfigId : '%s'!" % meetingConfigId)
            query['portal_type'] = mc.getItemTypeName()
        query['externalIdentifier'] = externalIdentifier
        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog.unrestrictedSearchResults(**query)

        logger.info('checkIsLinked SOAP made at "%s".' % portal.absolute_url_path())
        if brains:
            return True
        return False

    def _getConfigInfos(self, showCategories=False, userToShowCategoriesFor=None):
        '''
          Returns key informations about the configuration : active Organizations and MeetingConfigs
          If p_showCategories is given, we return also available categories.  We return every available
          categories by default or categories available to the p_userToShowCategoriesFor userId.
          Ony a Manager/MeetingManager can give a userToShowCategoriesFor, by default it will be the currently
          connected user.
        '''
        portal = self.context
        member = api.user.get_current()
        tool = api.portal.get_tool('portal_plonemeeting')

        # passing a userToShowCategoriesFor is only available to 'Manager' and 'MeetingManager'
        if userToShowCategoriesFor:
            if not self._mayAccessAdvancedFunctionnalities():
                raiseMsg("You need to be 'Manager' or 'MeetingManager' to get available categories for a user!")
            # check that the passed userId exists...
            user = portal.acl_users.getUserById(userToShowCategoriesFor)
            if not user:
                raiseMsg("Trying to get avaialble categories for an unexisting user '%s'!" % userToShowCategoriesFor)

        # MeetingConfigs
        config_infos = []
        for cfg in tool.getActiveConfigs():
            configInfo = ConfigInfo()
            configInfo._UID = cfg.UID()
            configInfo._id = cfg.getId()
            configInfo._title = cfg.Title()
            configInfo._description = cfg.Description()
            configInfo._itemPositiveDecidedStates = cfg.getItemPositiveDecidedStates()
            # only return categories if the meetingConfig uses it
            if showCategories and 'category' in cfg.getUsedItemAttributes():
                for category in cfg.getCategories(userId=userToShowCategoriesFor):
                    basicInfo = BasicInfo()
                    basicInfo._UID = category.UID()
                    basicInfo._id = category.getId()
                    basicInfo._title = category.Title()
                    basicInfo._description = category.Description()
                    configInfo._categories.append(basicInfo)
            config_infos.append(configInfo)

        # organizations
        group_infos = []
        for org in get_organizations():
            groupInfo = GroupInfo()
            groupInfo._UID = org.UID()
            groupInfo._id = org.getId()
            groupInfo._title = org.Title()
            groupInfo._description = org.Description()
            group_infos.append(groupInfo)

        memberId = member.getId()
        logger.info('Configuration parameters at "%s" SOAP accessed by "%s".' %
                    (tool.absolute_url_path(), memberId))
        return config_infos, group_infos

    def _getUserInfos(self, userId, showGroups, suffix=None):
        '''
          Returns informations about the given userId.  If p_showGroups is True,
          it will also returns the list of organizations the user is member of.
        '''
        member = api.user.get_current()
        memberId = member.getId()

        # a member can get infos for himself
        # if we want to query informations for another user, the connected user
        # must have the 'MeetingManager' or 'Manager' role
        if not memberId == userId:
            if not self._mayAccessAdvancedFunctionnalities():
                raiseMsg("You need to be 'Manager' or 'MeetingManager' to get "
                         "user informations for another user than '%s'!" % memberId)

        # if getting user informations about the currently connected user
        # or the connected user is MeetingManager/Manager, proceed!
        user = api.user.get(userId)

        if not user:
            raiseMsg("Trying to get user informations for an unexisting user '%s'!" % userId)

        # show groups the user is member of if specified
        userGroups = []
        if showGroups:
            # if a particular suffix is defined, we use it, it will
            # returns only groups the user is member of with the defined
            # suffix, either it will returns every groups the user is member of
            tool = api.portal.get_tool('portal_plonemeeting')
            # backward compatibility,   _user received 'suffix' before but 'suffixes' now
            suffixes = suffix and [suffix] or []
            orgs = tool.get_orgs_for_user(user_id=userId, suffixes=suffixes, the_objects=True)
            for org in orgs:
                basicInfo = BasicInfo()
                basicInfo._UID = org.UID()
                basicInfo._id = org.getId()
                basicInfo._title = org.Title()
                basicInfo._description = org.Description()
                userGroups.append(basicInfo)

        return user.getProperty('fullname'), user.getProperty('email'), userGroups

    def _getItemInfos(self,
                      searchParams,
                      showExtraInfos=False,
                      showAnnexes=False,
                      allowed_annexes_types=[],
                      include_annex_binary=True,
                      showAssembly=False,
                      showTemplates=False,
                      inTheNameOf=None):
        '''
          Get an item with given searchParams dict.
          As the user is connected, the security in portal_catalog do the job.
        '''
        portal = self.context

        member = api.user.get_current()

        params = {}
        # remove leading '_' in searchParams
        for elt in searchParams.keys():
            searchParam = searchParams[elt]
            if searchParam:
                params[elt[1:]] = searchParam

        # check if we received at least one search parameter because calling the portal_catalog without search parameter
        # will return the entire catalog (even if we subforce using 'MeetingItem' meta_type here above)
        if not params:
            raiseMsg("Define at least one search parameter!")

        # if we specify in the request that we want to get infos about an item
        # for another user, we need to check that :
        # - user getting infos for another is 'MeetingManager' or 'Manager'
        # - the user we want to get informations for exists
        if inTheNameOf:
            if not self._mayAccessAdvancedFunctionnalities():
                raiseMsg("You need to be 'Manager' or 'MeetingManager' to get item informations 'inTheNameOf'!")
            # change considered member to inTheNameOf given userid
            member = portal.acl_users.getUserById(inTheNameOf)
            if not member:
                raiseMsg("Trying to get item informations 'inTheNameOf' an unexisting user '%s'!" % inTheNameOf)
        memberId = member.getId()

        tool = api.portal.get_tool('portal_plonemeeting')
        mc = None
        if 'meetingConfigId' in params and 'portal_type' not in params:
            # check that the given meetingConfigId exists
            meetingConfigId = params['meetingConfigId']
            mc = getattr(tool, meetingConfigId, None)
            if not mc or not mc.meta_type == 'MeetingConfig':
                raiseMsg("Unknown meetingConfigId : '%s'!" % meetingConfigId)
            params['portal_type'] = mc.getItemTypeName()

        # if we are getting item informations inTheNameOf, use this user for the rest of the process
        res = []
        try:
            if inTheNameOf:
                oldsm, original_auth_user = setup_user_in_the_name_of(portal, member)

            # force to use the 'MeetingItem' meta_type to be sure that attributes here above exist on found elements
            params['meta_type'] = 'MeetingItem'
            catalog = api.portal.get_tool('portal_catalog')
            params['sort_on'] = 'created'
            brains = catalog(**params)
            noDate = DateTime('1950/01/01 00:00:00 UTC')
            wfTool = api.portal.get_tool('portal_workflow')
            for brain in brains:
                # XXX for now we still need to wake up the item because we do not have the meeting's date
                # on the brain, this could be great to manage ticket http://trac.imio.be/trac/ticket/4176 so
                # we could avoid waking up the item if showExtraInfos is False
                item = brain.getObject()
                itemInfo = ItemInfo()
                itemInfo._UID = item.UID()
                itemInfo._id = item.getId()
                itemInfo._title = item.Title()
                itemInfo._creator = item.Creator()
                itemInfo._creation_date = localtime(item.created())
                itemInfo._modification_date = localtime(item.modified())
                # keep the original category/proposingGroup magic
                category_or_proposing_group = item.getCategory() and \
                    item.getCategory(theObject=True) or item.getProposingGroup(theObject=True)
                itemInfo._category = category_or_proposing_group.getId()
                itemInfo._description = item.getRawDescription()
                itemInfo._detailedDescription = item.getRawDetailedDescription()
                itemInfo._decision = item.getRawDecision(keepWithNext=False)
                preferred = item.getPreferredMeeting()
                itemInfo._preferredMeeting = not preferred == ITEM_NO_PREFERRED_MEETING_VALUE and preferred or ''
                preferredMeeting = None
                if itemInfo._preferredMeeting:
                    preferredMeeting = uuidToObject(preferred)
                itemInfo._preferred_meeting_date = \
                    preferredMeeting and preferredMeeting.date.utctimetuple() or localtime(noDate)
                itemInfo._review_state = wfTool.getInfoFor(item, 'review_state')
                meeting = item.hasMeeting() and item.getMeeting()
                itemInfo._meeting = meeting and meeting.UID() or None
                itemInfo._meeting_date = meeting and meeting.date.utctimetuple() or localtime(noDate)
                itemInfo._absolute_url = item.absolute_url()
                itemInfo._externalIdentifier = item.getField('externalIdentifier').getAccessor(item)()
                itemInfo._extraInfos = {}
                if showExtraInfos:
                    extraInfosFields = self._getExtraInfosFields(item)
                    # store every other informations in the 'extraInfos' dict
                    for field in extraInfosFields:
                        itemInfo._extraInfos[field.getName()] = field.getRaw(item)
                    # also add informations about the linked MeetingConfig
                    if not mc:
                        mc = tool.getMeetingConfig(item)
                    itemInfo._extraInfos['meeting_config_id'] = mc.getId()
                    itemInfo._extraInfos['meeting_config_title'] = mc.Title()
                    # add the review_state translated
                    itemInfo._extraInfos['review_state_translated'] = translate(msgid=itemInfo._review_state,
                                                                                domain='plone',
                                                                                context=portal.REQUEST)
                    # add the category title
                    itemInfo._extraInfos['category_title'] = category_or_proposing_group.Title()
                    # add the creator fullname
                    itemInfo._extraInfos['creator_fullname'] = get_user_fullname(itemInfo._creator)
                if showAnnexes:
                    for annex in get_annexes(item):
                        # filter on annexes types
                        if allowed_annexes_types and annex.content_category not in allowed_annexes_types:
                            continue
                        annexInfo = AnnexInfo()
                        annexInfo._id = annex.id
                        annexInfo._title = annex.Title()
                        annexInfo._annexTypeId = annex.content_category
                        annexInfo._filename = annex.file.filename
                        if include_annex_binary:
                            annexInfo._file = annex.file.data
                        itemInfo._annexes.append(annexInfo)
                if showAssembly and meeting:
                    # assembly or attendees?  Return a printed representation
                    assembly_lines = []
                    if item.getItemAssembly():
                        for field in item.Schema().filterFields(isMetadata=False):
                            field_name = field.getName()
                            if field_name.startswith('itemAssembly') and \
                               field_name != 'itemAssemblyGuests':
                                assembly_lines.append(field_name)
                                assembly_lines.append(field.getAccessor(item)())
                    else:
                        # contacts
                        # attendees
                        assembly_lines.append('Attendees')
                        attendees = item.get_attendees(the_objects=True)
                        attendees_lines = []
                        for attendee in attendees:
                            attendees_lines.append(attendee.get_short_title())
                        assembly_lines.append('\n'.join(attendees_lines))

                        # absents
                        assembly_lines.append('Absents')
                        absents = item.get_item_absents(the_objects=True)
                        absents_lines = []
                        for absent in absents:
                            absents_lines.append(absent.get_short_title())
                        assembly_lines.append('\n'.join(absents_lines))

                        # excused
                        assembly_lines.append('Excused')
                        excused = item.get_item_excused(the_objects=True)
                        excused_lines = []
                        for excused_contact in excused:
                            excused_lines.append(excused_contact.get_short_title())
                        assembly_lines.append('\n'.join(excused_lines))
                    # itemAssemblyGuests used for both
                    field = item.Schema()['itemAssemblyGuests']
                    assembly_lines.append('itemAssemblyGuests')
                    assembly_lines.append(field.getAccessor(item)())
                    itemInfo._item_assembly = '|'.join(assembly_lines)
                if showTemplates:
                    if not mc:
                        # we need the item's meetingConfig
                        mc = tool.getMeetingConfig(item)
                    templates = self._availablePodTemplates(item)
                    for template in templates:
                        for pod_format in template.pod_formats:
                            templateInfo = TemplateInfo()
                            templateInfo._title = template.Title()
                            templateInfo._templateFormat = pod_format
                            templateInfo._templateId = POD_TEMPLATE_ID_PATTERN.format(
                                template.getId(), pod_format)
                            # in case we are reusing another pod_file,
                            # use the get_file method that manages that
                            templateInfo._templateFilename = template.get_file().filename
                            itemInfo._templates.append(templateInfo)
                logger.info('Item at %s SOAP accessed by "%s".' %
                            (item.absolute_url_path(), memberId))
                res.append(itemInfo,)
        finally:
            # fallback to original user calling the SOAP method
            if inTheNameOf:
                teardown_user_in_the_name_of(portal, oldsm, original_auth_user)
        return res

    def _getItemTemplate(self, itemUID, templateId, inTheNameOf):
        '''
          Generates a POD template p_templateId on p_itemUID
        '''
        portal = self.context
        member = api.user.get_current()
        # if we specify in the request that we want to get a template of an item
        # for another user, we need to check that :
        # - user getting the template is 'MeetingManager' or 'Manager'
        # - the user we want to get informations for exists
        if inTheNameOf:
            if not self._mayAccessAdvancedFunctionnalities():
                raiseMsg("You need to be 'Manager' or 'MeetingManager' to get a template for an item 'inTheNameOf'!")
            # change considered member to inTheNameOf given userid
            member = portal.acl_users.getUserById(inTheNameOf)
            if not member:
                raiseMsg("Trying to create an item 'inTheNameOf' an unexisting user '%s'!" % inTheNameOf)

        # if we are creating an item inTheNameOf, use this user for the rest of the process
        try:
            if inTheNameOf:
                oldsm, original_auth_user = setup_user_in_the_name_of(portal, member)

            # search for the item, this will also check if the user can actually access it
            catalog = api.portal.get_tool('portal_catalog')
            brains = catalog(UID=itemUID)
            if not brains:
                raiseMsg("You can not access this item!")

            # check that the template is available to the member
            item = brains[0].getObject()
            templates = self._availablePodTemplates(item)
            theTemplate = None
            for template in templates:
                if template.getId() == templateId.split(POD_TEMPLATE_ID_PATTERN.format('', ''))[0]:
                    theTemplate = template
                    break
            if not theTemplate:
                raiseMsg("You can not access this template!")

            # we can access the item and the template, proceed!
            # generate the template and return the result
            logger.info('Template at "%s" for item at "%s" SOAP accessed by "%s".' %
                        (template.absolute_url_path(), item.absolute_url_path(), member.getId()))
            try:
                view = item.restrictedTraverse('@@document-generation')
                item.REQUEST.set('template_uid', theTemplate.UID())
                item.REQUEST.set('output_format', templateId.split(POD_TEMPLATE_ID_PATTERN.format('', ''))[1])
                res = view()
            except Exception, e:
                raiseMsg("Exception : %s" % e.message)
        finally:
            # fallback to original user calling the SOAP method
            if inTheNameOf:
                teardown_user_in_the_name_of(portal, oldsm, original_auth_user)
        return res

    def _getExtraInfosFields(self, item):
        """
          Returns fields considered as 'extraInfos' aka not main informations
        """
        res = []
        for field in item.schema.filterFields(isMetadata=False):
            if field.getName() not in MAIN_DATA_FROM_ITEM_SCHEMA:
                res.append(field)
        return res

    def _meetingsAcceptingItems(self, meetingConfigId, inTheNameOf=None):
        '''
        '''
        portal = self.context
        member = api.user.get_current()
        tool = api.portal.get_tool('portal_plonemeeting')

        # if we specify in the request that we want to get infos about an item
        # for another user, we need to check that :
        # - user getting infos for another is 'MeetingManager' or 'Manager'
        # - the user we want to get informations for exists
        if inTheNameOf:
            if not self._mayAccessAdvancedFunctionnalities():
                raiseMsg("You need to be 'Manager' or 'MeetingManager' to get item informations 'inTheNameOf'!")
            # change considered member to inTheNameOf given userid
            member = portal.acl_users.getUserById(inTheNameOf)
            if not member:
                raiseMsg("Trying to get meetings accepting items 'inTheNameOf' an unexisting user '%s'!" % inTheNameOf)
        memberId = member.getId()

        cfg = getattr(tool, meetingConfigId or '', None)
        if not cfg or not cfg.meta_type == 'MeetingConfig':
            raiseMsg("Unknown meetingConfigId : '%s'!" % meetingConfigId)

        # if we are getting item informations inTheNameOf, use this user for the rest of the process
        res = []
        try:
            if inTheNameOf:
                oldsm, original_auth_user = setup_user_in_the_name_of(portal, member)

            brains = cfg.getMeetingsAcceptingItems()
            for brain in brains:
                # XXX for now we still need to wake up the item because we do not have the meeting's date
                # on the brain, this could be great to manage ticket http://trac.imio.be/trac/ticket/4176 so
                # we could avoid waking up the item if showExtraInfos is False
                meeting = brain.getObject()
                meetingInfo = MeetingInfo()
                meetingInfo._UID = meeting.UID()
                meetingInfo._date = meeting.date.utctimetuple()
                res.append(meetingInfo,)
        finally:
            # fallback to original user calling the SOAP method
            if inTheNameOf:
                teardown_user_in_the_name_of(portal, oldsm, original_auth_user)

        logger.info('MeetingConfig at %s SOAP accessed by "%s" to get meetings accepting items.' %
                    (cfg.absolute_url_path(), memberId))
        return res

    def _createItem(self,
                    meetingConfigId,
                    proposingGroupId,
                    creationData,
                    cleanHtml=True,
                    wfTransitions=[],
                    inTheNameOf=None):
        '''
          Create an item with given parameters
        '''
        portal = self.context
        tool = api.portal.get_tool('portal_plonemeeting')

        warnings = []
        member = api.user.get_current()

        # if we specify in the request that we want to create an item
        # for another user, we need to check that :
        # - user creating for another is 'MeetingManager' or 'Manager'
        # - the user we want to create an item for exists
        if inTheNameOf:
            if not self._mayAccessAdvancedFunctionnalities():
                raiseMsg("You need to be 'Manager' or 'MeetingManager' to create an item 'inTheNameOf'!")
            # change considered member to inTheNameOf given userid
            member = portal.acl_users.getUserById(inTheNameOf)
            if not member:
                raiseMsg("Trying to create an item 'inTheNameOf' an unexisting user '%s'!" % inTheNameOf)
        memberId = member.getId()

        # check that the given meetingConfigId exists
        cfg = getattr(tool, meetingConfigId, None)
        if not cfg or not cfg.meta_type == 'MeetingConfig':
            raiseMsg("Unknown meetingConfigId : '%s'!" % meetingConfigId)

        # check that the user is a creator for given proposingGroupId
        # proposingGroupId may be an organization id (backward compatibility) or an organization UID
        # get the MeetingGroups for wich inTheNameOfMemberId is creator
        proposingGroupUID = org_id_to_uid(proposingGroupId, raise_on_error=False)
        if not proposingGroupUID:
            proposingGroupUID = proposingGroupId
        userOrgUids = tool.get_orgs_for_user(
            user_id=memberId, suffixes=['creators'], the_objects=False)
        if proposingGroupUID not in userOrgUids:
            raiseMsg("'%s' can not create items for the '%s' group!" % (memberId, proposingGroupId))

        # title is mandatory!
        if not creationData.__dict__['_title']:
            raiseMsg("A 'title' is mandatory!")

        # build creationData
        # creationData keys begin with an '_' (_title, _description, ...) so tranform them
        data = {}
        for elt in creationData.__dict__.keys():
            # do not take annexes into account
            if not elt == '_annexes':
                data[elt[1:]] = creationData.__dict__[elt]

        # category can not be None
        if data['category'] is None:
            data['category'] = ''

        # ignore boolean 'toDiscuss' that is None, it means it was not set
        # or if value is set during item present
        if data['toDiscuss'] is None:
            data.pop('toDiscuss')

        # raise if we pass an optional attribute that is not activated in this MeetingConfig
        optionalItemFields = cfg.listUsedItemAttributes()
        usedItemAttrs = cfg.getUsedItemAttributes()
        for field in data:
            # if the field is an optional field that is not used and that has a value (contains data), we raise
            if field in optionalItemFields and \
               field not in usedItemAttrs and \
               data[field]:
                raiseMsg("The optional field \"%s\" is not activated in this configuration!" % field)

        # raise if we pass a preferredMeeting that is not a meeting accepting items
        if not data['preferredMeeting']:
            data['preferredMeeting'] = ITEM_NO_PREFERRED_MEETING_VALUE
        if not data['preferredMeeting'] == ITEM_NO_PREFERRED_MEETING_VALUE and \
           not data['preferredMeeting'] in \
           [meetingBrain.UID for meetingBrain in cfg.getMeetingsAcceptingItems()]:
            raiseMsg("The given preferred meeting UID ({0}) is not a meeting accepting items!".format(
                data['preferredMeeting']))

        # validate passed associatedGroups
        associatedGroups = data['associatedGroups']
        if associatedGroups:
            vocab = get_vocab(cfg, 'Products.PloneMeeting.vocabularies.associatedgroupsvocabulary')
            ag_term_keys = vocab.by_token.keys()
            difference = tuple(set(associatedGroups).difference(ag_term_keys))
            if difference:
                raiseMsg("The \"associatedGroups\" data contains wrong values: \"{0}\"!".format(
                    ', '.join(difference)))

        # validate passed groupsInCharge
        groupsInCharge = data['groupsInCharge']
        if groupsInCharge:
            vocab = get_vocab(cfg, 'Products.PloneMeeting.vocabularies.groupsinchargevocabulary')
            gic_term_keys = vocab.by_token.keys()
            difference = tuple(set(groupsInCharge).difference(gic_term_keys))
            if difference:
                raiseMsg("The \"groupsInCharge\" data contains wrong values: \"{0}\"!".format(
                    ', '.join(difference)))

        # validate passed optionalAdvisers
        optionalAdvisers = data['optionalAdvisers']
        if optionalAdvisers:
            if not cfg.getUseAdvices():
                raiseMsg("The advices functionnality is not enabled for this configuration!")

            # advices are enabled, check if given values are correct
            vocab = get_vocab(cfg, 'Products.PloneMeeting.vocabularies.itemoptionaladvicesvocabulary',
                              **{'include_selected': False, 'include_not_selectable_values': False})
            oa_term_keys = vocab.by_token.keys()
            difference = tuple(set(optionalAdvisers).difference(oa_term_keys))
            if difference:
                raiseMsg("The \"optionalAdvisers\" data contains wrong values: \"{0}\"!".format(
                    ', '.join(difference)))

        # externalIdentifier is indexed, it can not be None
        if not data['externalIdentifier']:
            data['externalIdentifier'] = ''

        # manage extraAttrs, check if it exist, if so, add it to data
        # for now, we only accept TextFields
        for extraAttr in creationData._extraAttrs:
            key = extraAttr._key
            value = extraAttr._value
            # the given extraAttr must be in the item schema
            if key not in MeetingItem.schema:
                raiseMsg("The extraAttr '%s' was not found the the MeetingItem schema!" % key)
            field = MeetingItem.schema[key]
            # only support XHTML TextField at the moment, aka field using RichWidget
            # others will need validation
            if not isinstance(field.widget, RichWidget):
                raiseMsg("The extraAttr '%s' must correspond to a field using a "
                         "'RichWidget' in the MeetingItem schema!" % key)
            # avoid overriding a value
            if key not in data:
                data[key] = value

        try:
            # if we are creating an item inTheNameOf, use this user for the rest of the process
            if inTheNameOf:
                oldsm, original_auth_user = setup_user_in_the_name_of(portal, member)

            # get or create the meetingFolder the item will be created in
            # if the user does not have a memberArea
            # (never connected, then we raise an error)
            destFolder = tool.getPloneMeetingFolder(meetingConfigId, memberId)
            if destFolder.meta_type == 'Plone Site':
                raiseMsg("No member area for '%s'.  Never connected to PloneMeeting?" % memberId)

            type_name = cfg.getItemTypeName()
            data.update({'proposingGroup': proposingGroupUID,
                         'id': portal.generateUniqueId(type_name), })

            # find htmlFieldIds we will have to check/clean
            # RichText fields are not handled by invokeFactory so we
            # clean it then set it...
            htmlFieldIds = []
            managedFieldIds = data.keys()
            for field in MeetingItem.schema.fields():
                fieldName = field.getName()
                if fieldName in managedFieldIds and field.widget.getName() in ['RichWidget', 'VisualWidget', ]:
                    htmlFieldIds.append(fieldName)
            warnWrongHTML = False
            if cleanHtml:
                cleaner = Cleaner()
                for htmlFieldId in htmlFieldIds:
                    # BeautifulSoup does not deal with NoneType
                    if data[htmlFieldId] is None:
                        data[htmlFieldId] = ''
                    soup = BeautifulSoup(safe_unicode(data[htmlFieldId]))
                    # we need a surrounding <p></p> or the content is not generated by appy.pod
                    if not data[htmlFieldId].startswith('<p>') or not data[htmlFieldId].endswith('</p>'):
                        data[htmlFieldId] = '<p>%s</p>' % data[htmlFieldId]
                    if not soup.contents or not getattr(soup.contents[0], 'name', None) == u'p':
                        soup = BeautifulSoup(safe_unicode(data[htmlFieldId]))
                    renderedSoupContents = soup.renderContents()
                    if not isinstance(renderedSoupContents, unicode):
                        renderedSoupContents = unicode(renderedSoupContents, 'utf-8')
                    # clean HTML with HTMLParser, it will remove special entities like &#xa0;
                    renderedSoupContents = HTMLParser().unescape(renderedSoupContents)
                    # clean HTML with lxml Cleaner
                    renderedSoupContents = cleaner.clean_html(renderedSoupContents).encode('utf-8')
                    # clean_html surrounds the cleaned HTML with <div>...</div>... removes it!
                    if renderedSoupContents.startswith('<div>') and renderedSoupContents.endswith('</div>'):
                        renderedSoupContents = renderedSoupContents[5:-6]
                    if not renderedSoupContents == data[htmlFieldId]:
                        warnWrongHTML = True
                        data[htmlFieldId] = renderedSoupContents

            # check that if category is mandatory, it is given and that given category is available
            if 'category' in usedItemAttrs:
                availableCategories = [cat.getId() for cat in cfg.getCategories()] or ['', ]
                if data['category'] not in availableCategories:
                    # special message if category used not given
                    if not data['category']:
                        raiseMsg("In this config, category is mandatory!")
                    # we are using categories but the given one is not in availableCategories
                    else:
                        raiseMsg("'%s' is not available for the '%s' group!" % (
                            data['category'], proposingGroupId))

            # we create the item to be able to check the category here above...
            itemId = destFolder.invokeFactory(type_name, **data)
            item = getattr(destFolder, itemId)
            item.setCategory(data['category'])

            # add a record to the item workflow_history to specify that item was created thru SOAP WS
            add_event_to_wf_history(item,
                                    action=ITEM_SOAP_CREATED,
                                    actor=memberId,
                                    comments=ITEM_SOAP_CREATED + '_comments')

            # processForm calls at_post_create_script too
            # this is necessary before adding annexes
            item.at_post_create_script()

            # HTML fields were not set by invokeFactory, set it...
            for htmlFieldId in htmlFieldIds:
                # use 'text/x-html-safe' mimetype when creating the item
                field = item.getField(htmlFieldId)
                field.getMutator(item)(data[htmlFieldId], mimetype='text/x-html-safe')

            # manage externalIdentifier
            externalIdentifier = False
            field = item.getField(EXTERNAL_IDENTIFIER_FIELD_NAME)
            # can not be None as it is indexed
            externalIdentifier = data['externalIdentifier'] or ''
            if data['externalIdentifier']:
                # we received an externalIdentifier, use it!
                field.getMutator(item)(data['externalIdentifier'])
                externalIdentifier = True
            else:
                field.getMutator(item)(field.default)

            # manage annexes
            # call processForm before adding annexes because it calls at_post_create_script
            # where we set some usefull values regarding annexes
            item.processForm()
            # add warning message after processForm because the id of the item may be changed
            if warnWrongHTML:
                warning_message = translate(WRONG_HTML_WARNING,
                                            domain='imio.pm.ws',
                                            mapping={'item_path': item.absolute_url_path(),
                                                     'creator': memberId},
                                            context=portal.REQUEST)
                logger.warning(warning_message)
                warnings.append(warning_message)

            # existing annex types
            annexTypeIds = cfg.annexes_types.item_annexes.objectIds()
            for annex in creationData._annexes:
                annex_title = annex._title
                annex_type_id = annex._annexTypeId
                annex_filename = annex._filename
                validFileName = annex_filename and len(annex_filename.split('.')) == 2
                # if annex._file is None, we turn it to an empty string
                annex_file = annex._file or ''
                if not annex_type_id or annex_type_id not in annexTypeIds:
                    # take the first available annexType that is the default one
                    annex_type_id = annexTypeIds[0]
                annex_type = getattr(cfg.annexes_types.item_annexes, annex_type_id)
                # manage mimetype manually
                # as we receive base64 encoded binary, mimetypes registry can not handle this correctly...
                mr = self.context.mimetypes_registry
                mime = magic.Magic(mime=True)
                magic_mimetype = None
                try:
                    magic_mimetype = mime.from_buffer(annex_file)
                except MagicException:
                    # in case there is an error with magic trying to find annex mimetype, we pass
                    # we will have magic_mimetype=None and so will try to use file extension to
                    # determinate it here under
                    pass
                mr_mimetype = ()
                if magic_mimetype:
                    mr_mimetype = mr.lookup(magic_mimetype)
                else:
                    # if libmagic could not determine file mimetype (like in version 5.09 of the command 'file'
                    # where MS mimetypes (doc, xls, ...) are not recognized...), we use the file extension...
                    if validFileName:
                        # mr.lookup here above returns a tuple so we build a tuple also...
                        mr_mimetype = (mr.lookupExtension(annex_filename.split('.')[1]),)
                # check if a mimetype has been found and if a file extension was defined for it
                if not mr_mimetype:
                    warning_message = translate(MIMETYPE_NOT_FOUND_OF_ANNEX_WARNING,
                                                domain='imio.pm.ws',
                                                mapping={'annex_path': safe_unicode(annex_filename or annex_title),
                                                         'item_path': item.absolute_url_path()},
                                                context=portal.REQUEST)
                    logger.warning(warning_message)
                    warnings.append(warning_message)
                    continue
                elif not mr_mimetype[0].extensions:
                    warning_message = translate(NO_EXTENSION_FOR_MIMETYPE_OF_ANNEX_WARNING,
                                                domain='imio.pm.ws',
                                                mapping={'mime': mr_mimetype[0].normalized(),
                                                         'annex_path': unicode((annex_filename or annex_title),
                                                                               'utf-8'),
                                                         'item_path': item.absolute_url_path()},
                                                context=portal.REQUEST)
                    logger.warning(warning_message)
                    warnings.append(warning_message)
                    continue
                elif len(mr_mimetype[0].extensions) > 1:
                    if not validFileName:
                        # several extensions are proposed by mimetypes_registry
                        # and we have nothing to find out what is the extension to use
                        warning_message = translate(MULTIPLE_EXTENSION_FOR_MIMETYPE_OF_ANNEX_WARNING,
                                                    domain='imio.pm.ws',
                                                    mapping={'mime': mr_mimetype[0].normalized(),
                                                             'annex_path': unicode((annex_filename or annex_title),
                                                                                   'utf-8'),
                                                             'item_path': item.absolute_url_path()},
                                                    context=portal.REQUEST)
                        logger.warning(warning_message)
                        warnings.append(warning_message)
                        continue
                # now that we have the correct mimetype, we can handle the filename if necessary
                if not validFileName:
                    # we have the file extension, generate a filename
                    annex_filename = "annex.%s" % mr_mimetype[0].extensions[0]
                # now that we have everything we need, proceed with annex creation
                createContentInContainer(
                    container=item,
                    portal_type='annex',
                    title=annex_title,
                    file=namedfile.NamedBlobFile(annex_file,
                                                 filename=safe_unicode(annex_filename)),
                    content_category=calculate_category_id(annex_type),
                    to_print=False,
                    confidential=False)

            # manage wfTransitions
            if wfTransitions:
                # trigger transitions
                wfTool = api.portal.get_tool('portal_workflow')
                wf_comment = 'wf_transition_triggered_by_application'
                with api.env.adopt_roles(roles=['Manager']):
                    for tr in wfTransitions:
                        available_transitions = [t['id'] for t in wfTool.getTransitionsFor(item)]
                        if tr not in available_transitions:
                            warning_message = "While treating wfTransitions, could not " \
                                "trigger the '{0}' transition!".format(tr)
                            # additional info if failed to trigger the 'present' transition
                            if tr == 'present':
                                warning_message += " Make sure a meeting accepting items " \
                                    "exists in configuration '{0}'!".format(cfg.getId())
                            warnings.append(warning_message)
                            continue
                        # we are sure transition is available, trigger it
                        wfTool.doActionFor(item, tr, comment=wf_comment)

            # log finally
            logger.info('Item at "%s"%s SOAP created by "%s".' %
                        (item.absolute_url_path(),
                         (externalIdentifier and ' with externalIdentifier "%s"' %
                          item.externalIdentifier or ''), memberId))
        finally:
            # fallback to original user calling the SOAP method
            if inTheNameOf:
                teardown_user_in_the_name_of(portal, oldsm, original_auth_user)
            # if response status is 302, turn it back to 200 or the query fails
            # this happens when transitions are triggered and some code does a "redirect"
            if portal.REQUEST.RESPONSE.status == 302:
                portal.REQUEST.RESPONSE.status = 200
        return item.UID(), warnings

    def _mayAccessAdvancedFunctionnalities(self):
        '''
          This method will protect various advances functionnalities like the
          'inTheNameOf' functionnality.
          By default, the given user must be 'MeetingManager' for a
          MeetingConfig to be able to use 'inTheNameOf' or a 'Manager'.
        '''
        tool = api.portal.get_tool('portal_plonemeeting')
        if tool.userIsAmong(['meetingmanagers']) or tool.isManager(realManagers=True):
            return True

        return False

    def _availablePodTemplates(self, item):
        """ """
        viewlet = PMDocumentGeneratorLinksViewlet(item,
                                                  item.REQUEST,
                                                  None,
                                                  None)
        return viewlet.get_generable_templates()


class WS4PMWSDL(BrowserView):
    """
      This render the SOAP/WSDL depending on the current portal_url
    """

    def __call__(self, dump_wsdl=False):
        """ """
        if dump_wsdl:
            self._dump_wsdl()
        return self.index()

    def _dump_wsdl(self):
        """To generate ZSI client/server/types files, we need the WSDL
           to be stored on the filesystem.
           This will dump the WSDL under name dumpedWSDL.txt."""
        portal = api.portal.get()
        rendered = self.index()
        rendered = rendered.replace(portal.absolute_url(), 'http://ws4pm.imio.be')
        rendered = rendered.replace(
            '<?xml version="1.0" encoding="utf-8"?>\n',
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<!-- This file is generated by calling http://portal_url/@@ws4pm.wsdl?dump_wsdl:boolean=True -->\n')
        dumpedWSDL = open(os.path.dirname(__file__) + '/../dumpedWSDL.txt', 'wb')
        dumpedWSDL.write("" + rendered)
        dumpedWSDL.close()
