import ZSI
import logging
logger = logging.getLogger('WS4PM')
from AccessControl import Unauthorized
from AccessControl.SecurityManagement import getSecurityManager, setSecurityManager, newSecurityManager
from Products.Five import BrowserView
from imio.pm.ws.soap.basetypes import ItemInfo, ConfigInfo, AnnexInfo
from imio.pm.ws.config import EXTERNAL_IDENTIFIER_FIELD_NAME, \
                                                 MAIN_DATA_FROM_ITEM_SCHEMA
from time import localtime
from DateTime import DateTime
import magic

DEFAULT_NO_WARNING_MESSAGE = 'There was NO WARNING message during item creation.'
WRONG_HTML_WARNING = 'HTML used for creating item at "%s" by "%s" was not valid.  Used BeautifulSoup corrected HTML.'
MIMETYPE_NOT_FOUND_OF_ANNEX_WARNING = 'Mimetype could not be determined correctly for annex "%s" of item "%s", ' \
                                      'this annex was not added.'
NO_EXTENSION_FOR_MIMETYPE_OF_ANNEX_WARNING = 'No extensions available in mimetypes_registry for mimetype "%s" ' \
                                             'for annex "%s" of item "%s", this annex was not added.'
MULTIPLE_EXTENSION_FOR_MIMETYPE_OF_ANNEX_WARNING = "Could not determine an extension to use for mimetype '%s', ' \
                                                  'too many available, for annex '%s' of item '%s', ' \
                                                  'this annex was not added."


class SOAPView(BrowserView):
    """
      class delivering SOAP methods for Products.PloneMeeting
    """

    def testConnectionRequest(self, request, response):
        '''
          This is the accessed SOAP method for testing the connection to the webservices
          This method is usefull for SOAP clients
        '''
        response._connectionState = self._testConnection()
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
        response._configInfo = self._getConfigInfos()
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
        # remove the '_inTheNameOf' from searchParams as it is not a search parameter
        inTheNameOf = None
        if '_inTheNameOf' in params:
            inTheNameOf = params['_inTheNameOf']
            params.pop('_inTheNameOf')

        response._itemInfo = self._getItemInfos(params,
                                                request.__dict__.get('_showExtraInfos', False),
                                                request.__dict__.get('_showAnnexes', False),
                                                inTheNameOf)
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
        return True

    def _checkIsLinked(self, meetingConfigId, externalIdentifier):
        '''
          Test if an element in PloneMeeting is linked to given meetingConfig/externalIdentifier
        '''
        portal = self.context
        member = portal.portal_membership.getAuthenticatedMember()

        # this is only available to 'Manager' and 'MeetingManager'
        if not member.has_role('Manager') and not member.has_role('MeetingManager'):
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

    def _getConfigInfos(self):
        '''
          Returns key informations about the configuration : active MeetingGroups and MeetingConfigs
        '''
        portal = self.context

        member = portal.portal_membership.getAuthenticatedMember()
        memberId = member.getId()

        tool = portal.portal_plonemeeting

        res = []
        # MeetingConfigs
        for config in tool.getActiveConfigs():
            configInfo = ConfigInfo()
            configInfo._UID = config.UID()
            configInfo._id = config.getId()
            configInfo._title = config.Title()
            configInfo._description = config.Description()
            configInfo._type = config.portal_type
            res.append(configInfo)

        # MeetingGroups
        for group in tool.getActiveGroups():
            configInfo = ConfigInfo()
            configInfo._UID = group.UID()
            configInfo._id = group.getId()
            configInfo._title = group.Title()
            configInfo._description = group.Description()
            configInfo._type = group.portal_type
            res.append(configInfo)

        logger.info('Configuration parameters at "%s" SOAP accessed by "%s".' % \
                        (tool.absolute_url_path(), memberId))
        return res

    def _getItemInfos(self, searchParams, showExtraInfos=False, showAnnexes=False, inTheNameOf=None):
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
            if not member.has_role('Manager') and not member.has_role('MeetingManager'):
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
        if 'meetingConfigId' in params and not 'portal_type' in params:
            #check that the given meetingConfigId exists
            meetingConfigId = params['meetingConfigId']
            mc = getattr(tool, meetingConfigId, None)
            if not mc or not mc.meta_type == 'MeetingConfig':
                raise ZSI.Fault(ZSI.Fault.Client, "Unknown meetingConfigId : '%s'!" % meetingConfigId)
            params['portal_type'] = mc.getItemTypeName()

        # if we are getting item informations inTheNameOf, use this user for the rest of the process
        if inTheNameOf:
            oldsm = getSecurityManager()
            newSecurityManager(portal.REQUEST, member)

        # force to use the 'MeetingItem' meta_type to be sure that attributes here above exist on found elements
        params['meta_type'] = 'MeetingItem'
        brains = portal.portal_catalog(**params)
        res = []
        for brain in brains:
            # XXX for now we still need to wake up the item because we do not have the meeting's date
            # on the brain, this could be great to manage ticket http://trac.imio.be/trac/ticket/4176 so
            # we could avoid waking up the item
            item = brain.getObject()
            itemInfo = ItemInfo()
            itemInfo._UID = item.UID()
            itemInfo._id = item.getId()
            itemInfo._title = item.Title()
            itemInfo._category = item.getCategory()
            itemInfo._description = item.getRawDescription()
            itemInfo._decision = item.getRawDecision()
            itemInfo._review_state = portal.portal_workflow.getInfoFor(item, 'review_state')
            itemInfo._meeting_date = localtime(item.hasMeeting() and item.getMeeting().getDate() or \
                                     DateTime('1950/01/01 00:00:00 UTC'))
            itemInfo._absolute_url = item.absolute_url()
            itemInfo._externalIdentifier = item.getField('externalIdentifier').getAccessor(item)()
            itemInfo._extraInfos = {}
            if showExtraInfos:
                extraInfosFields = self._getExtraInfosFields(item)
                # store every other informations in the 'extraInfos' dict
                for field in extraInfosFields:
                    itemInfo._extraInfos[field.getName()] = field.getRaw(item)
                # also add informations about the linked MeetingConfig
                meetingConfig = tool.getMeetingConfig(item)
                itemInfo._extraInfos['meeting_config_id'] = meetingConfig.getId()
                itemInfo._extraInfos['meeting_config_title'] = meetingConfig.Title()
            if showAnnexes:
                for groupOfAnnexesByType in item.getAnnexesByType(realAnnexes=True):
                    for annex in groupOfAnnexesByType :
                        annexInfo = AnnexInfo()
                        annexInfo._title = annex.Title()
                        annexInfo._annexTypeId = annex.getMeetingFileType().getId()
                        annexInfo._filename = annex.getFile().filename
                        annexInfo._file = annex.getFile().data
                        itemInfo._annexes.append(annexInfo)
            logger.info('Item at %s SOAP accessed by "%s".' % \
                        (item.absolute_url_path(), memberId))
            res.append(itemInfo,)
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

    def createItemRequest(self, request, response):
        '''
          This is the accessed SOAP method for creating an item
        '''
        response._UID, response._warnings = self._createItem(request._meetingConfigId, request._proposingGroupId, \
                                                             request._creationData, request._inTheNameOf)
        return response

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
            if not member.has_role('Manager') and not member.has_role('MeetingManager'):
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
        userGroups = tool.getGroups(userId=memberId, suffix="creators")
        proposingGroup = [group for group in userGroups if group.getId() == proposingGroupId]
        if not proposingGroup:
            raise ZSI.Fault(ZSI.Fault.Client,
                            "'%s' can not create items for the '%s' group!" % (memberId, proposingGroupId))

        # if we are creating an item inTheNameOf, use this user for the rest of the process
        if inTheNameOf:
            oldsm = getSecurityManager()
            newSecurityManager(portal.REQUEST, member)

        # get or create the meetingFolder the item will be created in
        # if the user does not have a memberArea
        # (never connected, then we raise an error)
        destFolder = tool.getPloneMeetingFolder(meetingConfigId, memberId)
        if destFolder.meta_type == 'Plone Site':
            # fallback to original user calling the SOAP method
            if inTheNameOf:
                setSecurityManager(oldsm)
            raise ZSI.Fault(ZSI.Fault.Client, \
            "No member area for '%s'.  Never connected to PloneMeeting?" % memberId)

        # now that every checks pass, we can create the item
        # creationData keys begin with an '_' (_title, _description, ...) so tranform them
        data = {}
        for elt in creationData.__dict__.keys():
            #do not take annexes into account
            if not elt == '_annexes':
                data[elt[1:]] = creationData.__dict__[elt]

        type_name = mc.getItemTypeName()
        data.update(
                    {
                     'proposingGroup': proposingGroupId,
                     'id': portal.generateUniqueId(type_name),
                    }
                   )

        # we create the item to be able to check the category here above...
        itemId = destFolder.invokeFactory(type_name, **data)
        item = getattr(destFolder, itemId)
        # processForm calls at_post_create_script too
        # this is necessary before adding annexes
        item.at_post_create_script()

        # check that the given category is really available
        if not mc.getUseGroupsAsCategories() and not data['category'] in item.listCategories().keys():
            #if the category is not available, delete the created item and raise an error
            item.aq_inner.aq_parent.manage_delObjects(ids=[itemId, ])
            # fallback to original user calling the SOAP method
            if inTheNameOf:
                setSecurityManager(oldsm)
            raise ZSI.Fault(ZSI.Fault.Client,
                            "In this config, category is mandatory.  '%s' is not available for the '%s' group!" %
                            (data['category'], proposingGroupId))
        item.setCategory(data['category'])

        # make sure we have html here, and as clean as possible...
        from BeautifulSoup import BeautifulSoup
        # find htmlFieldIds we will have to check/clean
        htmlFieldIds = []
        managedFieldIds = data.keys()
        for field in item.Schema().fields():
            fieldName = field.getName()
            if fieldName in managedFieldIds and field.widget.getName() in ['RichWidget', 'VisualWidget', ]:
                    htmlFieldIds.append(fieldName)
        warnWrongHTML = False
        for htmlFieldId in htmlFieldIds:
            soup = BeautifulSoup(data[htmlFieldId])
            # we need a surrounding <p></p> or the content is not generated by appy.pod
            if not data[htmlFieldId].startswith('<p>') or not data[htmlFieldId].endswith('</p>'):
                data[htmlFieldId] = unicode('<p>%s</p>' % data[htmlFieldId], 'utf-8')
            if not soup.contents or not getattr(soup.contents[0], 'name', None) == u'p':
                soup = BeautifulSoup(data[htmlFieldId])
            # check that we have valid HTML or we use the transformed HTML by BeautifulSoup
            # compare unicode as data[htmlFieldId] is unicode...
            renderedSoupContents = soup.renderContents()
            if isinstance(data[htmlFieldId], unicode):
                renderedSoupContents = unicode(renderedSoupContents, 'utf-8')
            if not renderedSoupContents == data[htmlFieldId]:
                warnWrongHTML = True
                data[htmlFieldId] = renderedSoupContents
            # use 'text/x-html-safe' mimetype when creating the item
            field = item.getField(htmlFieldId)
            field.getMutator(item)(data[htmlFieldId], mimetype='text/x-html-safe')

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
            warning_message = WRONG_HTML_WARNING % (item.absolute_url_path(), memberId)
            logger.warning(warning_message)
            warnings.append(warning_message)
        # existing annex types
        fileTypes = mc.getFileTypes()
        for annex in creationData._annexes:
            annex_title = annex._title
            annex_type_id = annex._annexTypeId
            annex_filename = annex._filename
            validFileName = annex_filename and len(annex_filename.split('.')) == 2
            annex_file = annex._file
            # we have an annex_type_id, find relevant MeetingFileType object
            if not annex_type_id or not annex_type_id in [fileType.id for fileType in fileTypes]:
                # take the first available annex fileType that is the default one
                annex_type = fileTypes[0]
            else:
                annex_type = getattr(mc.meetingfiletypes, annex_type_id)
            # manage mimetype manually
            # as we receive base64 encoded binary, mimetypes registry can not handle this correctly...
            mime = magic.Magic(mime=True)
            mr = self.context.mimetypes_registry
            annex_mimetype = mime.from_buffer(annex_file)
            if annex_mimetype:
                mr_mimetype = mr.lookup(annex_mimetype)
            else:
                # if libmagic could not determine file mimetype (like in version 5.09 of the command 'file'
                # where MS mimetypes (doc, xls, ...) are not recognized...), we use the file extension...
                mr_mimetype = ()
                if validFileName:
                    # mr.lookup here above returns a tuple so we build a tuple also...
                    mr_mimetype = (mr.lookupExtension(annex_filename.split('.')[1]),)
            # check if a mimetype has been found and if a file extension was defined for it
            if not mr_mimetype:
                warning_message = MIMETYPE_NOT_FOUND_OF_ANNEX_WARNING % ((annex_filename or annex_title),
                                                                          item.absolute_url_path())
                logger.warning(warning_message)
                warnings.append(warning_message)
                continue
            elif not mr_mimetype[0].extensions:
                warning_message = NO_EXTENSION_FOR_MIMETYPE_OF_ANNEX_WARNING % (mr_mimetype[0].normalized(),
                                                                                (annex_filename or annex_title),
                                                                                item.absolute_url_path())
                logger.warning(warning_message)
                warnings.append(warning_message)
                continue
            elif len(mr_mimetype[0].extensions) > 1:
                if not validFileName:
                    # several extensions are proposed by mimetypes_registry
                    # and we have nothing to find out what is the extension to use
                    warning_message = MULTIPLE_EXTENSION_FOR_MIMETYPE_OF_ANNEX_WARNING % \
                                                    (mr_mimetype[0].normalized(),
                                                    (annex_filename or annex_title),
                                                    item.absolute_url_path())
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
            item.addAnnex(annex_filename, annex_type, annex_title, annex_file, False, annex_type, **kwargs)
            itemAnnexes = item.objectValues('MeetingFile')
            lastInsertedAnnex = itemAnnexes[-1]
            lastInsertedAnnex.getFile().setContentType(annex_mimetype)

        logger.info('Item at "%s"%s SOAP created by "%s".' % \
                    (item.absolute_url_path(),
                     (externalIdentifier and ' with externalIdentifier "%s"' \
                      % item.externalIdentifier or ''), memberId))
        if not warnings:
            # make the user aware that warnings are displayed in the response
            warnings.append(DEFAULT_NO_WARNING_MESSAGE)

        # fallback to original user calling the SOAP method
        if inTheNameOf:
            setSecurityManager(oldsm)
        return item.UID(), warnings


class WS4PMWSDL(BrowserView):
    """
      This render the SOAP/WSDL depending on the current portal_url
    """
