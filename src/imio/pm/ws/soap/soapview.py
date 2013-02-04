import ZSI
from Products.Five import BrowserView
import logging
logger = logging.getLogger('WS4PM')
from imio.pm.ws.soap.basetypes import ItemInfo, ConfigInfo, AnnexInfo
from imio.pm.ws.config import EXTERNAL_IDENTIFIER_FIELD_NAME, \
                                                 MAIN_DATA_FROM_ITEM_SCHEMA
from time import localtime
from DateTime import DateTime
import magic

DEFAULT_NO_WARNING_MESSAGE = 'There was NO WARNING message during item creation.'
WRONG_HTML_WARNING = 'HTML used for creating item at "%s" by "%s" was not valid.  Used BeautifulSoup corrected HTML.'
MIMETYPE_NOT_FOUND_OF_ANNEX_WARNING = 'Mimetype could not be determined correctly for annex "%s" of item "%s", this annex was not added.'
NO_EXTENSION_FOR_MIMETYPE_OF_ANNEX_WARNING = 'No extensions available in mimetypes_registry for mimetype "%s" for annex "%s" of item "%s", this annex was not added.'
MULTIPLE_EXTENSION_FOR_MIMETYPE_OF_ANNEX_WARNING = "Could not determine an extension to use for mimetype '%s', too many available, for annex '%s' of item '%s', this annex was not added."


class SOAPView(BrowserView):
    """
      class delivering SOAP methods for Products.PloneMeeting
    """

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
        response._itemInfo = self._getItemInfos(request.__dict__)
        return response

    def getItemInfosRequest(self, request, response):
        '''
          This is the accessed SOAP method for getting informations about an existing item
          This is an helper method when you just need to access an item you know the UID of
        '''
        params = dict(request.__dict__)
        #remove the '_showExtraInfos' from searchParams as it is not a search parameter
        try:
            params.pop('_showExtraInfos')
        except KeyError:
            pass
        #remove the '_showAnnexes' from searchParams as it is not a search parameter
        try:
            params.pop('_showAnnexes')
        except KeyError:
            pass
        response._itemInfo = self._getItemInfos(params, request.__dict__.get('_showExtraInfos', False), request.__dict__.get('_showAnnexes', False))
        return response

    def _getConfigInfos(self):
        '''
          Returns key informations about the configuration : active MeetingGroups and MeetingConfigs
        '''
        portal = self.context

        member = portal.portal_membership.getAuthenticatedMember()
        memberId = member.getId()

        tool = portal.portal_plonemeeting

        res = []
        #MeetingConfigs
        for config in tool.getActiveConfigs():
            configInfo = ConfigInfo()
            configInfo._UID = config.UID()
            configInfo._id = config.getId()
            configInfo._title = config.Title()
            configInfo._description = config.Description()
            configInfo._type = config.portal_type
            res.append(configInfo)

        #MeetingGroups
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

    def _getItemInfos(self, searchParams, showExtraInfos=False, showAnnexes=False):
        '''
          Get an item with given searchParams dict.  As the user is connected, the security in portal_catalog do the job
        '''
        portal = self.context

        member = portal.portal_membership.getAuthenticatedMember()
        memberId = member.getId()

        params = {}
        #remove leading '_' in searchParams
        for elt in searchParams.keys():
            #one given searchParams is not a search parameter: '_showExtraInfos' will return every available infos of the item
            if elt == '_showExtraInfos':
                continue
            searchParam = searchParams[elt]
            if searchParam:
                params[elt[1:]] = searchParam

        #check if we received at least one search parameter because calling the portal_catalog without search parameter
        #will return the entire catalog (even if we subforce using 'MeetingItem' meta_type here above)
        if not params:
            raise ZSI.Fault(ZSI.Fault.Client, "Define at least one search parameter!")

        if 'meetingConfigId' in params and not 'portal_type' in params:
            #check that the given meetingConfigId exists
            tool = portal.portal_plonemeeting
            meetingConfigId = params['meetingConfigId']
            mc = getattr(tool, meetingConfigId, None)
            if not mc or not mc.meta_type == 'MeetingConfig':
                raise ZSI.Fault(ZSI.Fault.Client, "Unknown meetingConfigId : '%s'!" % meetingConfigId)
            params['portal_type'] = mc.getItemTypeName()

        #force to use the 'MeetingItem' meta_type to be sure that attributes here above exist on found elements
        params['meta_type'] = 'MeetingItem'
        brains = portal.portal_catalog(**params)
        if not brains:
            return []

        res = []
        for brain in brains:
            item = brain.getObject()
            itemInfo = ItemInfo()
            itemInfo._UID = item.UID()
            itemInfo._id = item.getId()
            itemInfo._title = item.Title()
            itemInfo._category = item.getCategory()
            itemInfo._description = item.getRawDescription()
            itemInfo._decision = item.getRawDecision()
            itemInfo._review_state = portal.portal_workflow.getInfoFor(item, 'review_state')
            itemInfo._meeting_date = localtime(item.hasMeeting() and item.getMeeting().getDate() or DateTime('1950/01/01 00:00:00 UTC'))
            itemInfo._absolute_url = item.absolute_url()
            itemInfo._externalIdentifier = item.getField('externalIdentifier').getAccessor(item)()
            itemInfo._extraInfos = {}
            if showExtraInfos:
                extraInfosFields = self._getExtraInfosFields(item)
                #store every other informations in the 'extraInfos' dict
                for field in extraInfosFields:
                    itemInfo._extraInfos[field.getName()] = field.getRaw(item)
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
        response._UID, response._warnings = self._createItem(request._meetingConfigId, request._proposingGroupId, request._creationData)
        return response

    def _createItem(self, meetingConfigId, proposingGroupId, creationData):
        '''
          Create an item with given parameters
        '''
        portal = self.context
        tool = portal.portal_plonemeeting

        warnings = []

        member = portal.portal_membership.getAuthenticatedMember()
        memberId = member.getId()

        #check that the given meetingConfigId exists
        mc = getattr(tool, meetingConfigId, None)
        if not mc or not mc.meta_type == 'MeetingConfig':
            raise ZSI.Fault(ZSI.Fault.Client, "Unknown meetingConfigId : '%s'!" % meetingConfigId)

        #get or create the meetingFolder the item will be created in
        #if the user does not have a memberArea
        #(never connected, then we raise an error)
        destFolder = tool.getPloneMeetingFolder(meetingConfigId, memberId)
        if destFolder.meta_type == 'Plone Site':
            raise ZSI.Fault(ZSI.Fault.Client, \
            "No member area for '%s'.  Never connected to PloneMeeting?" % memberId)

        #check that the user is a creator for given proposingGroupId
        #get the MeetingGroups for wich memberId is creator
        userGroups = tool.getGroups(userId=memberId, suffix="creators")
        proposingGroup = [group for group in userGroups if group.getId() == proposingGroupId]
        if not proposingGroup:
            raise ZSI.Fault(ZSI.Fault.Client, "'%s' can not create items for the '%s' group!" % (memberId, proposingGroupId))

        #now that every checks pass, we can create the item
        #creationData keys begin with an '_' (_title, _description, ...) so tranform them
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

        #we create the item to be able to check the category here above...
        itemId = destFolder.invokeFactory(type_name, **data)
        item = getattr(destFolder, itemId)
        #processForm calls at_post_create_script too
        item.processForm()
        #check that the given category is really available
        if not mc.getUseGroupsAsCategories() and not data['category'] in item.listCategories().keys():
            #if the category is not available, delete the created item and raise an error
            item.aq_inner.aq_parent.manage_delObjects(ids=[itemId, ])
            raise ZSI.Fault(ZSI.Fault.Client, "In this config, category is mandatory.  '%s' is not available for the '%s' group!" % (data['category'], proposingGroupId))
        item.setCategory(data['category'])

        #manage annexes
        #existing annex types
        fileTypes = mc.getFileTypes()
        for annex in creationData._annexes:
            annex_title = annex._title
            annex_type_id = annex._annexTypeId
            annex_filename = annex._filename
            validFileName = annex_filename and len(annex_filename.split('.')) == 2
            annex_file = annex._file
            #we have an annex_type_id, find relevant MeetingFileType object
            if not annex_type_id or not annex_type_id in [fileType.id for fileType in fileTypes]:
                # take the first available annex fileType that is the default one
                annex_type = fileTypes[0]
            else:
                annex_type = getattr(mc.meetingfiletypes, annex_type_id)
            #manage mimetype manually
            #as we receive base64 encoded binary, mimetypes registry can not handle this correctly...
            mime = magic.Magic(mime=True)
            mr = self.context.mimetypes_registry
            annex_mimetype = mime.from_buffer(annex_file)
            if annex_mimetype:
                mr_mimetype = mr.lookup(annex_mimetype)
            else:
                #if libmagic could not determine file mimetype (like in version 5.09 of the command 'file'
                #where MS mimetypes (doc, xls, ...) are not recognized...), we use the file extension...
                mr_mimetype = ()
                if validFileName:
                    #mr.lookup here above returns a tuple so we build a tuple also...
                    mr_mimetype = (mr.lookupExtension(annex_filename.split('.')[1]),)
            #check if a mimetype has been found and if a file extension was defined for it
            if not mr_mimetype:
                warning_message = MIMETYPE_NOT_FOUND_OF_ANNEX_WARNING % ((annex_filename or annex_title), item.absolute_url_path())
                logger.warning(warning_message)
                warnings.append(warning_message)
                continue
            elif not mr_mimetype[0].extensions:
                warning_message = NO_EXTENSION_FOR_MIMETYPE_OF_ANNEX_WARNING % (mr_mimetype[0].normalized(), (annex_filename or annex_title), item.absolute_url_path())
                logger.warning(warning_message)
                warnings.append(warning_message)
                continue
            elif len(mr_mimetype[0].extensions) > 1:
                if not validFileName:
                    #several extensions are proposed by mimetypes_registry and we have nothing to find out what is the extension to use
                    warning_message = MULTIPLE_EXTENSION_FOR_MIMETYPE_OF_ANNEX_WARNING % (mr_mimetype[0].normalized(), (annex_filename or annex_title), item.absolute_url_path())
                    logger.warning(warning_message)
                    warnings.append(warning_message)
                    continue
            #now that we have the correct mimetype, we can handle the filename if necessary
            if not validFileName:
                #we have the file extension, generate a filename
                annex_filename = "annex.%s" % mr_mimetype[0].extensions[0]
            #now that we have everything we need, proceed with annex creation
            kwargs = {}
            kwargs['filename'] = annex_filename
            item.addAnnex(annex_filename, annex_type, annex_title, annex_file, False, annex_type, **kwargs)
            itemAnnexes = item.objectValues('MeetingFile')
            lastInsertedAnnex = itemAnnexes[-1]
            lastInsertedAnnex.getFile().setContentType(annex_mimetype)

        #make sure we have html here, and as clean as possible...
        from BeautifulSoup import BeautifulSoup
        #find htmlFieldIds we will have to check/clean
        htmlFieldIds = []
        managedFieldIds = data.keys()
        for field in item.Schema().fields():
            fieldName = field.getName()
            if fieldName in managedFieldIds and field.widget.getName() in ['RichWidget', 'VisualWidget',]:
                    htmlFieldIds.append(fieldName)
        warnWrongHTML = False
        for htmlFieldId in htmlFieldIds:
            soup = BeautifulSoup(data[htmlFieldId])
            #we need a surrounding <p></p> or the content is not generated by appy.pod
            data[htmlFieldId] = unicode('<p>%s</p>' % data[htmlFieldId], 'utf-8')
            if not soup.contents or not getattr(soup.contents[0], 'name', None) == u'p':
                soup = BeautifulSoup(data[htmlFieldId])
            #check that we have valid HTML or we use the transformed HTML by BeautifulSoup
            #compare unicode as data[htmlFieldId] is unicode...
            renderedSoupContents = unicode(soup.renderContents(), 'utf-8')
            if not renderedSoupContents == data[htmlFieldId]:
                warnWrongHTML = True
                data[htmlFieldId] = renderedSoupContents
            #use 'text/x-html-safe' mimetype when creating the item
            field = item.getField(htmlFieldId)
            field.getMutator(item)(data[htmlFieldId], mimetype='text/x-html-safe')

        #manage externalIdentifier
        externalIdentifier = False
        field = item.getField(EXTERNAL_IDENTIFIER_FIELD_NAME)
        if data['externalIdentifier']:
            #we received an externalIdentifier, use it!
            field.getMutator(item)(data['externalIdentifier'])
            externalIdentifier = True
        else:
            field.getMutator(item)(field.default)

        if warnWrongHTML:
            warning_message = WRONG_HTML_WARNING % (item.absolute_url_path(), memberId)
            logger.warning(warning_message)
            warnings.append(warning_message)
        logger.info('Item at "%s"%s SOAP created by "%s".' % \
                    (item.absolute_url_path(), (externalIdentifier and ' with externalIdentifier "%s"' % item.externalIdentifier or ''), memberId))
        if not warnings:
            #make the user aware that warnings are displayed in the response
            warnings.append(DEFAULT_NO_WARNING_MESSAGE)
        return item.UID(), warnings


class WS4PMWSDL(BrowserView):
    """
      This render the SOAP/WSDL depending on the current portal_url
    """
