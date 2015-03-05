import ZSI
import logging
logger = logging.getLogger('WS4PM')
import magic
from magic import MagicException
from BeautifulSoup import BeautifulSoup
from HTMLParser import HTMLParser
from lxml.html.clean import Cleaner
from AccessControl import Unauthorized
from AccessControl.SecurityManagement import getSecurityManager, setSecurityManager, newSecurityManager
from zope.i18n import translate
from Products.Five import BrowserView
from Products.PloneMeeting import PloneMeetingError
from Products.PloneMeeting.interfaces import IAnnexable
from Products.PloneMeeting.MeetingItem import MeetingItem
from imio.pm.ws.soap.basetypes import AnnexInfo
from imio.pm.ws.soap.basetypes import BasicInfo
from imio.pm.ws.soap.basetypes import ConfigInfo
from imio.pm.ws.soap.basetypes import ItemInfo
from imio.pm.ws.soap.basetypes import MeetingInfo
from imio.pm.ws.soap.basetypes import TemplateInfo
from imio.pm.ws.config import EXTERNAL_IDENTIFIER_FIELD_NAME, MAIN_DATA_FROM_ITEM_SCHEMA
from time import localtime
from DateTime import DateTime

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
ITEM_SOAP_CREATED_COMMENT = "This item has been created using the Webservice."


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
        response._configInfo = self._getConfigInfos(request._showCategories,
                                                    request._userToShowCategoriesFor)
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
        # remove the '_showExtraInfos' from searchParams as it is not a search parameter
        if '_showExtraInfos' in params:
            params.pop('_showExtraInfos')
        # remove the '_showAnnexes' from searchParams as it is not a search parameter
        if '_showAnnexes' in params:
            params.pop('_showAnnexes')
        # remove the '_showTemplates' from searchParams as it is not a search parameter
        if '_showTemplates' in params:
            params.pop('_showTemplates')
        # remove the '_inTheNameOf' from searchParams as it is not a search parameter
        inTheNameOf = None
        if '_inTheNameOf' in params:
            inTheNameOf = params['_inTheNameOf']
            params.pop('_inTheNameOf')

        response._itemInfo = self._getItemInfos(params,
                                                request.__dict__.get('_showExtraInfos', False),
                                                request.__dict__.get('_showAnnexes', False),
                                                request.__dict__.get('_showTemplates', False),
                                                inTheNameOf)
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
                                                             request._inTheNameOf)
        return response

    def _testConnection(self):
        '''
          Test current connection state
        '''
        portal = self.context
        isAnon = portal.portal_membership.isAnonymousUser()

        # in case this method is accessed without valid credrentials, raise Unauthorized
        if isAnon:
            raise Unauthorized

        logger.info('Test connection SOAP made at "%s".' % portal.absolute_url_path())
        version = portal.portal_setup.getVersionForProfile('imio.pm.ws:default')
        return True, version

    def _checkIsLinked(self, meetingConfigId, externalIdentifier):
        '''
          Test if an element in PloneMeeting is linked to given meetingConfig/externalIdentifier
        '''
        portal = self.context

        # this is only available to 'Manager' and 'MeetingManager'
        if not self._mayAccessAdvancedFunctionnalities():
            raise ZSI.Fault(ZSI.Fault.Client,
                            "You need to be 'Manager' or 'MeetingManager' to check if an element is linked to an item!")

        # perform the unrestrictedSearchResult
        tool = portal.portal_plonemeeting
        # if a meetingConfigId is given, check that it exists
        query = {}
        if meetingConfigId:
            mc = getattr(tool, meetingConfigId, None)
            if not mc or not mc.meta_type == 'MeetingConfig':
                raise ZSI.Fault(ZSI.Fault.Client, "Unknown meetingConfigId : '%s'!" % meetingConfigId)
            query['portal_type'] = mc.getItemTypeName()
        query['externalIdentifier'] = externalIdentifier
        brains = portal.portal_catalog.unrestrictedSearchResults(**query)

        logger.info('checkIsLinked SOAP made at "%s".' % portal.absolute_url_path())
        if brains:
            return True
        return False

    def _getConfigInfos(self, showCategories=False, userToShowCategoriesFor=None):
        '''
          Returns key informations about the configuration : active MeetingGroups and MeetingConfigs
          If p_showCategories is given, we return also available categories.  We return every available
          categories by default or categories available to the p_userToShowCategoriesFor userId.
          Ony a Manager/MeetingManager can give a userToShowCategoriesFor, by default it will be the currently
          connected user.
        '''
        portal = self.context
        member = portal.portal_membership.getAuthenticatedMember()
        tool = portal.portal_plonemeeting

        # passing a userToShowCategoriesFor is only available to 'Manager' and 'MeetingManager'
        if userToShowCategoriesFor:
            if not self._mayAccessAdvancedFunctionnalities():
                raise ZSI.Fault(ZSI.Fault.Client,
                                "You need to be 'Manager' or 'MeetingManager' to get available categories for a user!")
            # check that the passed userId exists...
            user = portal.acl_users.getUserById(userToShowCategoriesFor)
            if not user:
                raise ZSI.Fault(ZSI.Fault.Client,
                                "Trying to get avaialble categories for an unexisting user '%s'!" %
                                userToShowCategoriesFor)

        res = []
        # MeetingConfigs
        for config in tool.getActiveConfigs():
            configInfo = ConfigInfo()
            configInfo._UID = config.UID()
            configInfo._id = config.getId()
            configInfo._title = config.Title()
            configInfo._description = config.Description()
            configInfo._type = config.portal_type
            # only return categories if the meetingConfig uses it
            if showCategories and not config.getUseGroupsAsCategories():
                for category in config.getCategories(userId=userToShowCategoriesFor):
                    basicInfo = BasicInfo()
                    basicInfo._UID = category.UID()
                    basicInfo._id = category.getId()
                    basicInfo._title = category.Title()
                    basicInfo._description = category.Description()
                    configInfo._categories.append(basicInfo)
            res.append(configInfo)

        # MeetingGroups
        for group in tool.getMeetingGroups():
            configInfo = ConfigInfo()
            configInfo._UID = group.UID()
            configInfo._id = group.getId()
            configInfo._title = group.Title()
            configInfo._description = group.Description()
            configInfo._type = group.portal_type
            res.append(configInfo)

        memberId = member.getId()
        logger.info('Configuration parameters at "%s" SOAP accessed by "%s".' %
                    (tool.absolute_url_path(), memberId))
        return res

    def _getUserInfos(self, userId, showGroups, suffix=None):
        '''
          Returns informations about the given userId.  If p_showGroups is True,
          it will also returns the list of groups the user is part of
        '''
        portal = self.context
        member = portal.portal_membership.getAuthenticatedMember()
        memberId = member.getId()

        # a member can get infos for himself
        # if we want to query informations for another user, the connected user
        # must have the 'MeetingManager' or 'Manager' role
        if not memberId == userId:
            if not self._mayAccessAdvancedFunctionnalities():
                raise ZSI.Fault(
                    ZSI.Fault.Client,
                    "You need to be 'Manager' or 'MeetingManager' to get "
                    "user informations for another user than '%s'!" % memberId)

        # if getting user informations about the currently connected user
        # or the connected user is MeetingManager/Manager, proceed!
        user = portal.portal_membership.getMemberById(userId)

        if not user:
            raise ZSI.Fault(ZSI.Fault.Client,
                            "Trying to get user informations for an unexisting user '%s'!"
                            % userId)

        # show groups the user is member of if specified
        userGroups = []
        if showGroups:
            # if a particular suffix is defined, we use it, it will
            # returns only groups the user is member of with the defined
            # suffix, either it will returns every groups the user is member of
            tool = portal.portal_plonemeeting
            groups = tool.getGroupsForUser(userId=userId, suffix=suffix)
            for group in groups:
                basicInfo = BasicInfo()
                basicInfo._UID = group.UID()
                basicInfo._id = group.getId()
                basicInfo._title = group.Title()
                basicInfo._description = group.Description()
                userGroups.append(basicInfo)

        return user.getProperty('fullname'), user.getProperty('email'), userGroups

    def _getItemInfos(self,
                      searchParams,
                      showExtraInfos=False,
                      showAnnexes=False,
                      showTemplates=False,
                      inTheNameOf=None):
        '''
          Get an item with given searchParams dict.  As the user is connected, the security in portal_catalog do the job
        '''
        portal = self.context

        member = portal.portal_membership.getAuthenticatedMember()

        params = {}
        # remove leading '_' in searchParams
        for elt in searchParams.keys():
            searchParam = searchParams[elt]
            if searchParam:
                params[elt[1:]] = searchParam

        # check if we received at least one search parameter because calling the portal_catalog without search parameter
        # will return the entire catalog (even if we subforce using 'MeetingItem' meta_type here above)
        if not params:
            raise ZSI.Fault(ZSI.Fault.Client, "Define at least one search parameter!")

        # if we specify in the request that we want to get infos about an item
        # for another user, we need to check that :
        # - user getting infos for another is 'MeetingManager' or 'Manager'
        # - the user we want to get informations for exists
        if inTheNameOf:
            if not self._mayAccessAdvancedFunctionnalities():
                raise ZSI.Fault(ZSI.Fault.Client,
                                "You need to be 'Manager' or 'MeetingManager' to get item informations 'inTheNameOf'!")
            # change considered member to inTheNameOf given userid
            member = portal.acl_users.getUserById(inTheNameOf)
            if not member:
                raise ZSI.Fault(ZSI.Fault.Client,
                                "Trying to get item informations 'inTheNameOf' an unexisting user '%s'!"
                                % inTheNameOf)
        memberId = member.getId()

        tool = portal.portal_plonemeeting
        mc = None
        if 'meetingConfigId' in params and not 'portal_type' in params:
            #check that the given meetingConfigId exists
            meetingConfigId = params['meetingConfigId']
            mc = getattr(tool, meetingConfigId, None)
            if not mc or not mc.meta_type == 'MeetingConfig':
                raise ZSI.Fault(ZSI.Fault.Client, "Unknown meetingConfigId : '%s'!" % meetingConfigId)
            params['portal_type'] = mc.getItemTypeName()

        # if we are getting item informations inTheNameOf, use this user for the rest of the process
        res = []
        try:
            if inTheNameOf:
                oldsm = getSecurityManager()
                newSecurityManager(portal.REQUEST, member)

            # force to use the 'MeetingItem' meta_type to be sure that attributes here above exist on found elements
            params['meta_type'] = 'MeetingItem'
            brains = portal.portal_catalog(**params)
            noDate = DateTime('1950/01/01 00:00:00 UTC')
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
                itemInfo._category = item.getCategory()
                itemInfo._description = item.getRawDescription()
                itemInfo._decision = item.getRawDecision(keepWithNext=False)
                itemInfo._review_state = portal.portal_workflow.getInfoFor(item, 'review_state')
                itemInfo._meeting_date = localtime(item.hasMeeting() and item.getMeeting().getDate() or noDate)
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
                    itemInfo._extraInfos['category_title'] = item.displayValue(item.listCategories(),
                                                                               item.getCategory())
                    # add the creator fullname
                    itemInfo._extraInfos['creator_fullname'] = tool.getUserName(itemInfo._creator)
                if showAnnexes:
                    for groupOfAnnexesByType in IAnnexable(item).getAnnexesByType(relatedTo='item',
                                                                                  realAnnexes=True):
                        for annex in groupOfAnnexesByType:
                            annexInfo = AnnexInfo()
                            annexInfo._title = annex.Title()
                            annexInfo._annexTypeId = annex.getMeetingFileType(theRealObject=True).getId()
                            annexInfo._filename = annex.getFile().filename
                            annexInfo._file = annex.getFile().data
                            itemInfo._annexes.append(annexInfo)
                if showTemplates:
                    if not mc:
                        # we need the item's meetingConfig
                        mc = tool.getMeetingConfig(item)
                    templates = mc.getAvailablePodTemplates(item)
                    for template in templates:
                        templateInfo = TemplateInfo()
                        templateInfo._title = template.Title()
                        templateInfo._templateFormat = template.getPodFormat()
                        templateInfo._templateId = template.getId()
                        templateInfo._templateFilename = template._getFileName(item)
                        itemInfo._templates.append(templateInfo)
                logger.info('Item at %s SOAP accessed by "%s".' %
                            (item.absolute_url_path(), memberId))
                res.append(itemInfo,)
        finally:
            # fallback to original user calling the SOAP method
            if inTheNameOf:
                setSecurityManager(oldsm)
        return res

    def _getItemTemplate(self, itemUID, templateId, inTheNameOf):
        '''
          Generates a POD template p_templateId on p_itemUID
        '''
        portal = self.context
        member = portal.portal_membership.getAuthenticatedMember()

        # if we specify in the request that we want to get a template of an item
        # for another user, we need to check that :
        # - user getting the template is 'MeetingManager' or 'Manager'
        # - the user we want to get informations for exists
        if inTheNameOf:
            if not self._mayAccessAdvancedFunctionnalities():
                raise ZSI.Fault(
                    ZSI.Fault.Client,
                    "You need to be 'Manager' or 'MeetingManager' to get a template for an item 'inTheNameOf'!")
            # change considered member to inTheNameOf given userid
            member = portal.acl_users.getUserById(inTheNameOf)
            if not member:
                raise ZSI.Fault(ZSI.Fault.Client,
                                "Trying to create an item 'inTheNameOf' an unexisting user '%s'!" % inTheNameOf)

        # if we are creating an item inTheNameOf, use this user for the rest of the process
        try:
            if inTheNameOf:
                oldsm = getSecurityManager()
                newSecurityManager(portal.REQUEST, member)

            # search for the item, this will also check if the user can actually access it
            brains = portal.portal_catalog(UID=itemUID)
            if not brains:
                raise ZSI.Fault(ZSI.Fault.Client, "You can not access this item!")

            # check that the template is available to the member
            item = brains[0].getObject()
            mc = portal.portal_plonemeeting.getMeetingConfig(item)
            templates = mc.getAvailablePodTemplates(item)
            theTemplate = None
            for template in templates:
                if template.getId() == templateId:
                    theTemplate = template
                    break
            if not theTemplate:
                raise ZSI.Fault(ZSI.Fault.Client, "You can not access this template!")

            # we can access the item and the template, proceed!
            # generate the template and return the result
            member = portal.portal_membership.getAuthenticatedMember()
            logger.info('Template at "%s" for item at "%s" SOAP accessed by "%s".' %
                        (template.absolute_url_path(), item.absolute_url_path(), member.getId()))
            try:
                res = theTemplate.generateDocument(item, forBrowser=False)
            except PloneMeetingError, e:
                raise ZSI.Fault(ZSI.Fault.Client, "PloneMeetingError : %s" % e.message)
        finally:
            # fallback to original user calling the SOAP method
            if inTheNameOf:
                setSecurityManager(oldsm)
        return res

    def _getExtraInfosFields(self, item):
        """
          Returns fields considered as 'extraInfos' aka not main informations
        """
        res = []
        for field in item.Schema().filterFields(isMetadata=False):
            if not field.getName() in MAIN_DATA_FROM_ITEM_SCHEMA:
                res.append(field)
        return res

    def _meetingsAcceptingItems(self, meetingConfigId, inTheNameOf=None):
        '''
        '''
        portal = self.context
        member = portal.portal_membership.getAuthenticatedMember()
        tool = portal.portal_plonemeeting

        # if we specify in the request that we want to get infos about an item
        # for another user, we need to check that :
        # - user getting infos for another is 'MeetingManager' or 'Manager'
        # - the user we want to get informations for exists
        if inTheNameOf:
            if not self._mayAccessAdvancedFunctionnalities():
                raise ZSI.Fault(ZSI.Fault.Client,
                                "You need to be 'Manager' or 'MeetingManager' to get item informations 'inTheNameOf'!")
            # change considered member to inTheNameOf given userid
            member = portal.acl_users.getUserById(inTheNameOf)
            if not member:
                raise ZSI.Fault(ZSI.Fault.Client,
                                "Trying to get meetings accepting items 'inTheNameOf' an unexisting user '%s'!"
                                % inTheNameOf)
        memberId = member.getId()

        tool = portal.portal_plonemeeting
        cfg = getattr(tool, meetingConfigId or '', None)
        if not cfg or not cfg.meta_type == 'MeetingConfig':
            raise ZSI.Fault(ZSI.Fault.Client, "Unknown meetingConfigId : '%s'!" % meetingConfigId)

        # if we are getting item informations inTheNameOf, use this user for the rest of the process
        res = []
        try:
            if inTheNameOf:
                oldsm = getSecurityManager()
                newSecurityManager(portal.REQUEST, member)

            brains = cfg.getMeetingsAcceptingItems()
            for brain in brains:
                # XXX for now we still need to wake up the item because we do not have the meeting's date
                # on the brain, this could be great to manage ticket http://trac.imio.be/trac/ticket/4176 so
                # we could avoid waking up the item if showExtraInfos is False
                meeting = brain.getObject()
                meetingInfo = MeetingInfo()
                meetingInfo._UID = meeting.UID()
                meetingInfo._date = localtime(meeting.getDate())

                logger.info('MeetingConfig at %s SOAP accessed by "%s" to get meetings accepting items.' %
                            (cfg.absolute_url_path(), memberId))
                res.append(meetingInfo,)
        finally:
            # fallback to original user calling the SOAP method
            if inTheNameOf:
                setSecurityManager(oldsm)
        return res

    def _createItem(self, meetingConfigId, proposingGroupId, creationData, inTheNameOf=None):
        '''
          Create an item with given parameters
        '''
        portal = self.context
        tool = portal.portal_plonemeeting

        warnings = []
        member = portal.portal_membership.getAuthenticatedMember()

        # if we specify in the request that we want to create an item
        # for another user, we need to check that :
        # - user creating for another is 'MeetingManager' or 'Manager'
        # - the user we want to create an item for exists
        if inTheNameOf:
            if not self._mayAccessAdvancedFunctionnalities():
                raise ZSI.Fault(ZSI.Fault.Client,
                                "You need to be 'Manager' or 'MeetingManager' to create an item 'inTheNameOf'!")
            # change considered member to inTheNameOf given userid
            member = portal.acl_users.getUserById(inTheNameOf)
            if not member:
                raise ZSI.Fault(ZSI.Fault.Client,
                                "Trying to create an item 'inTheNameOf' an unexisting user '%s'!" % inTheNameOf)
        memberId = member.getId()

        # check that the given meetingConfigId exists
        mc = getattr(tool, meetingConfigId, None)
        if not mc or not mc.meta_type == 'MeetingConfig':
            raise ZSI.Fault(ZSI.Fault.Client, "Unknown meetingConfigId : '%s'!" % meetingConfigId)

        # check that the user is a creator for given proposingGroupId
        # get the MeetingGroups for wich inTheNameOfMemberId is creator
        userGroups = tool.getGroupsForUser(userId=memberId, suffix="creators")
        proposingGroup = [group for group in userGroups if group.getId() == proposingGroupId]
        if not proposingGroup:
            raise ZSI.Fault(ZSI.Fault.Client,
                            "'%s' can not create items for the '%s' group!" % (memberId, proposingGroupId))

        # title is mandatory!
        if not creationData.__dict__['_title']:
            raise ZSI.Fault(ZSI.Fault.Client, "A 'title' is mandatory!")

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

        # raise if we pass an optional attribute that is not activated in this MeetingConfig
        optionalItemFields = mc.listUsedItemAttributes()
        activatedOptionalItemFields = mc.getUsedItemAttributes()
        for field in data:
            # if the field is an optional field that is not used and that has a value (contains data), we raise
            if field in optionalItemFields and not \
               field in activatedOptionalItemFields and \
               data[field]:
                raise ZSI.Fault(ZSI.Fault.Client,
                                "The optional field '%s' is not activated in this configuration!" % field)

        try:
            # if we are creating an item inTheNameOf, use this user for the rest of the process
            if inTheNameOf:
                oldsm = getSecurityManager()
                newSecurityManager(portal.REQUEST, member)

            # get or create the meetingFolder the item will be created in
            # if the user does not have a memberArea
            # (never connected, then we raise an error)
            destFolder = tool.getPloneMeetingFolder(meetingConfigId, memberId)
            if destFolder.meta_type == 'Plone Site':
                raise ZSI.Fault(ZSI.Fault.Client,
                                "No member area for '%s'.  Never connected to PloneMeeting?" % memberId)

            type_name = mc.getItemTypeName()
            data.update({'proposingGroup': proposingGroupId,
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
            cleaner = Cleaner()
            for htmlFieldId in htmlFieldIds:
                # BeautifulSoup does not deal with NoneType
                if data[htmlFieldId] is None:
                    data[htmlFieldId] = ''
                soup = BeautifulSoup(data[htmlFieldId])
                # we need a surrounding <p></p> or the content is not generated by appy.pod
                if not data[htmlFieldId].startswith('<p>') or not data[htmlFieldId].endswith('</p>'):
                    data[htmlFieldId] = '<p>%s</p>' % data[htmlFieldId]
                if not soup.contents or not getattr(soup.contents[0], 'name', None) == u'p':
                    soup = BeautifulSoup(data[htmlFieldId])
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

            # we create the item to be able to check the category here above...
            itemId = destFolder.invokeFactory(type_name, **data)
            item = getattr(destFolder, itemId)
            # processForm calls at_post_create_script too
            # this is necessary before adding annexes
            item.at_post_create_script()

            # HTML fields were not set by invokeFactory, set it...
            for htmlFieldId in htmlFieldIds:
                # use 'text/x-html-safe' mimetype when creating the item
                field = item.getField(htmlFieldId)
                field.getMutator(item)(data[htmlFieldId], mimetype='text/x-html-safe')

            # check that if category is mandatory (getUseGroupsAsCategories is False), it is given
            # and that given category is available
            # if we are not using categories, just ensure that we received an empty category
            availableCategories = not mc.getUseGroupsAsCategories() and item.listCategories().keys() or ['', ]
            if not data['category'] in availableCategories:
                # delete the created item and raise an error
                item.aq_inner.aq_parent.manage_delObjects(ids=[itemId, ])
                # special message if category mandatory and not given
                if not mc.getUseGroupsAsCategories() and not data['category']:
                    raise ZSI.Fault(ZSI.Fault.Client, "In this config, category is mandatory!")
                elif mc.getUseGroupsAsCategories() and data['category']:
                    raise ZSI.Fault(ZSI.Fault.Client, "This config does not use categories, the given '%s' category "
                                                      "can not be used!" % data['category'])
                # we are using categories but the given one is not in availableCategories
                elif not mc.getUseGroupsAsCategories():
                    raise ZSI.Fault(ZSI.Fault.Client, "'%s' is not available for the '%s' group!" %
                                    (data['category'], proposingGroupId))
            item.setCategory(data['category'])

            # manage externalIdentifier
            externalIdentifier = False
            field = item.getField(EXTERNAL_IDENTIFIER_FIELD_NAME)
            if data['externalIdentifier']:
                #we received an externalIdentifier, use it!
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
            fileTypes = mc.getFileTypes()
            for annex in creationData._annexes:
                annex_title = annex._title
                annex_type_id = annex._annexTypeId
                annex_filename = annex._filename
                validFileName = annex_filename and len(annex_filename.split('.')) == 2
                # if annex._file is None, we turn it to an empty string
                annex_file = annex._file or ''
                # we have an annex_type_id, find relevant MeetingFileType object
                # getFileTypes returns a dict with as 'id' the fileType UID
                fileTypeIds = [fileType['absolute_url'].split('/')[-1] for fileType in fileTypes]
                if not annex_type_id or not annex_type_id in fileTypeIds:
                    # take the first available annex fileType that is the default one
                    annex_type = fileTypes[0]['meetingFileTypeObjectUID']
                else:
                    annex_type = getattr(mc.meetingfiletypes, annex_type_id).UID()
                # manage mimetype manually
                # as we receive base64 encoded binary, mimetypes registry can not handle this correctly...
                mr = self.context.mimetypes_registry
                mime = magic.Magic(mime=True)
                magic_mimetype = None
                try:
                    magic_mimetype = mime.from_buffer(annex_file)
                except MagicException:
                    # in case there is an error with magic trying to find annex mimetype, we pass
                    # we will have magic_mimetype=None and so will try to use file extension to determinate it here under
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
                                                mapping={'annex_path': (annex_filename or annex_title),
                                                         'item_path': item.absolute_url_path()},
                                                context=portal.REQUEST)
                    logger.warning(warning_message)
                    warnings.append(warning_message)
                    continue
                elif not mr_mimetype[0].extensions:
                    warning_message = translate(NO_EXTENSION_FOR_MIMETYPE_OF_ANNEX_WARNING,
                                                domain='imio.pm.ws',
                                                mapping={'mime': mr_mimetype[0].normalized(),
                                                         'annex_path': (annex_filename or annex_title),
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
                                                             'annex_path': (annex_filename or annex_title),
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
                kwargs = {}
                kwargs['filename'] = annex_filename
                IAnnexable(item).addAnnex(annex_filename, annex_title, annex_file, False, annex_type, **kwargs)
                itemAnnexes = item.objectValues('MeetingFile')
                lastInsertedAnnex = itemAnnexes[-1]
                lastInsertedAnnex.getFile().setContentType(mr_mimetype[0].normalized())

            # change the comment in the item's add a line in the item's history
            review_history = item.workflow_history[item.getWorkflowName()]
            review_history[0]['comments'] = translate(ITEM_SOAP_CREATED_COMMENT,
                                                      domain='imio.pm.ws',
                                                      context=portal.REQUEST)

            logger.info('Item at "%s"%s SOAP created by "%s".' %
                        (item.absolute_url_path(),
                         (externalIdentifier and ' with externalIdentifier "%s"' %
                          item.externalIdentifier or ''), memberId))
        finally:
            # fallback to original user calling the SOAP method
            if inTheNameOf:
                setSecurityManager(oldsm)
        return item.UID(), warnings

    def _mayAccessAdvancedFunctionnalities(self):
        '''
          This method will protect various advances functionnalities like the
          'inTheNameOf' functionnality.
          By default, the given user must be 'MeetingManager' for a
          MeetingConfig to be able to use 'inTheNameOf' or a 'Manager'.
        '''
        if self.context.portal_plonemeeting.userIsAmong('meetingmanagers') or \
           self.context.portal_membership.getAuthenticatedMember().has_role('Manager'):
            return True

        return False


class WS4PMWSDL(BrowserView):
    """
      This render the SOAP/WSDL depending on the current portal_url
    """
