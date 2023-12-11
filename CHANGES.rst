Changelog
=========


3.9 (2023-12-11)
----------------

- Adapted code as `Products.PloneMeeting.utils.add_wf_history_action` was moved
  to `imio.history.utils.add_event_to_wf_history` and `ToolPloneMeeting.getUserName`
  is removed, we use `imio.helpers.content.get_user_fullname` instead.
  [gbastien]

3.8 (2023-10-19)
----------------

- Make sure `createItemRequest` returns a response status of `200` or
  it raises a `SOAPException` (even if item is created anyway?!).
  [gbastien]
- Fixed `SOAPView._getItemInfos` when computing `preferred_meeting_date`, it was
  always `None` because using the `uid_catalog` and Meeting is a DX content type.
  [gbastien]

3.7 (2023-03-06)
----------------

- Fixed `test_ws_getItemInfosWithShowAssembly` regarding changes in default
  contacts gender in PloneMeeting testing profile `import_data`.
  [gbastien]
- Completed `test_ws_meetingAcceptingItems` to check that it works when using
  `inTheNameOf` (was actually not working before `Products.PloneMeeting==4.2rc30`).
  [gbastien]
- Adapted code regarding removal of `MeetingConfig.useGroupsAsCategories`.
  [gbastien]

3.6 (2022-03-10)
----------------

- Whenever a `ZSI.Fault` error is raised, display also the message in the log manually
  because `z3c.soap` will not display the error string, only the traceback...
  [gbastien]

3.5 (2022-01-14)
----------------

- Fixed bug in `_createItem` where it could happen that user used `inTheNameOf`
  had cached `_listAllowedRolesAndUsers` resulting in seeing too much or not
  enough in the dashboard.  Accessing an item that should not be displayed ended
  in an Unauthorized though.
  Every method using inTheName of now use
  `setup_user_in_the_name_of`/`teardown_user_in_the_name_of` to handle it correctly.
  [gbastien]

3.4 (2022-01-07)
----------------

- Fixed call to `tool.isManager` and handle `utils.get_current_user_id`.
  [gbastien]

3.3 (2022-01-04)
----------------

- Fixed `SOAPView._mayAccessAdvancedFunctionnalities`, call
  `ToolPloneMeeting.isManager` with `ToolPloneMeeting` instance as first arg,
  required now for caching reasons.
  [gbastien]

3.2 (2021-11-26)
----------------

- Call `ToolPloneMeeting.get_orgs_for_user` with `the_objects=True/False`
  when relevant as default value changed in `Products.PloneMeeting`.
  [gbastien]

3.1 (2021-11-10)
----------------

- In `_meetingsAcceptingItems`, log only one time in the Zope log at the end or
  we have the impression that the method was called many times.
  [gbastien]

3.0 (2021-07-16)
----------------

- Fixed `test_ws_getItemInfosRequest` now that observers may access item since
  WF initial state, make sure we use a member that does not have access to item
  at all and fixed `test_ws_getConfigInfosItemPositiveDecidedStates`, field
  `MeetingConfig.itemPositiveDecidedStates` was removed and is now managed by
  `MeetingConfig.getItemPositiveDecidedStates` method.
  [gbastien]
- Fixed `getItemInfosRequest/getSingleItemInfosRequest` that was breaking when
  no result and `showEmptyValues=0`.
  [gbastien]
- Adapted tests and code regarding fact that Meeting was moved from AT to DX
  (`linkedMeetingUID` index is renamed to `meeting_uid`, `Meeting.date` attribute
  holds a `datetime` instead a `DateTime`, `attendees` related methods use
  snake_case instead camelCase on both `Meeting` and `MeetingItem`,
  every methods on Meeting use snake_case).
  [gbastien]
- Adapted code now that `MeetingItem.getCategory` does only return the real
  category and not the `proposingGroup` when category not used.
  [gbastien]

2.16 (2020-06-11)
-----------------

- When adding `wf_transition_triggered_by_application` comment to
  `workflow_history`, do not use a `zope.i18nmessageid.message.Message` or
  it is stored this way in workflow_history, use a simple string and
  it will be translated by `imio.history`.
  [gbastien]

2.15 (2020-05-28)
-----------------

- Fixed `test_ws_getItemInfosWithShowAssembly` as default value in
  `PloneMeeting` testing profile changed to test held position having a
  `&` character (non XHTML character).
  [gbastien]
- When library `chardet` is available, it wrongly detect utf-8 passed string to
  `BeautifulSoup` as being `iso-8859-1` leading to incorrect special characters.
  `chardet` is now availabe because a dependency of `collective.zamqp`.
  So pass `unicode` string to `BeautifulSoup` to avoid this.
  [gbastien]

2.14 (2020-03-17)
-----------------

- Added method `getSingleItemInfos` that return a single item informations,
  not a list of `ItemInfo` instances.
  Result and paramaters are exactly same as `getItemInfos`.
  [gbastien]
- Make most most of data returned by `getItemInfos` nillable.
  [gbastien]
- Added parameter `showEmptyValues=1` by default to `getItemInfos`,
  making it possible to remove empty values from returned result.
  [gbastien]

2.13 (2020-02-18)
-----------------

- Manage field `toDiscuss` while creating new item.
  [gbastien]
- Changed the way `wfTransitions` are managed in `createItem`: if a transition
  is not available, it is ignored and next transition is tried, this way it is
  easier to manage cases where item validation WF is different for proposing
  groups.
  [gbastien]

2.12 (2019-10-14)
-----------------

- Do not fail in 'getItemInfos' when returning POD templates if a POD template
  is using the odt_file of another POD template.
  [gbastien]

2.11 (2019-10-01)
-----------------

- Make it easier to detect if an item was created using the createItem SOAP WS
  by adding a specific line to the item workflow_history like it is the case
  when creating an item from an item template or from a recurring item.
  [gbastien]

2.10 (2019-09-30)
-----------------

- 'getItemInfos' returns 'meeting' containing the meeting UID if any.
  [gbastien]
- 'searchItems' now accepts an additional search parameter 'linkedMeetingUID'.
  [gbastien]

2.9 (2019-09-24)
----------------

- In 'getItemInfos' when 'showAssembly=True', changed separator between list of
  assembly members from '|' to '\n' so it is easier to parse as '|' is already
  the separator between types of attendees (attendees, absents, excused, ...).
  [gbastien]

2.8 (2019-09-23)
----------------

- In createItem, added possibility to define associatedGroups and
  groupsInCharge as lists of organization UIDs.
  [gbastien]
- Added parameter 'wfTransitions' to createItem making it possible to trigger
  given WF transitions on the newly created item.
  [gbastien]
- In createItem, added possibility to define optionalAdvisers.
  [gbastien]
- Force catalog query in getItemInfos to use 'sort_on=created'.
  [gbastien]
- In getItemInfos, added 'showAssembly=False' parameter making it possible to
  receive the item assembly in the _item_assembly attribute when item is in a
  meeting.
  [gbastien]
- Removed manual handling of currentWSDL.txt.  Now dumpedWSDL.txt is generated
  by calling 'http://portal_url/@@ws4pm.wsdl?dump_wsdl:boolean=True'.
  [gbastien]
- Added parameter 'allowed_annexes_types' and 'include_annex_binary' to 
  getItemInfos() method.
  [sdelcourt]
- Add attribute 'id' to the AnnexInfo data type.
  [sdelcourt]

2.7 (2019-05-16)
----------------

- Override plone.transformchain transformer to not apply on SOAP request.
  [gbastien]
- Jenkinsfile for CI [odelaere]
- Removed dependency on unittest2.
  [gbastien]

2.6 (2018-12-04)
----------------

- Adapted to changes in Products.PloneMeeting following integration of
  collective.contact.
  [gbastien]
- Manage 'category_title' using MeetingItem.getCategory(theObject=True).
  [gbastien]

2.5 (2018-01-15)
----------------

- Use a simpleType 'List' for the 'ConfigInfo.itemPositiveDecidedStates' data
  to avoid using a 'xsd:Array' type that is not recognized correctly by 'soapUI'.
  [gbastien]

2.4 (2017-10-24)
----------------

- testConnection.version now returns the distribution version (2.4) and not
  the GenericSetup version (2000) that only changes when an upgrade step is
  required.
  [gbastien]

2.3 (2017-10-13)
----------------

- Add preferred_meeting_date attribute on ItemInfos.
  [sdelcourt]

2.2 (2017-08-04)
----------------

- Fixed tests regarding new format used for annex.content_category.
  [gbastien]

2.1 (2017-03-27)
----------------

- Adapted code now that ToolPloneMeeting.userIsAmong receives a list of suffixes
  instead one single suffix before.
  [gbastien]
- Added parameter 'cleanHtml' to createItem method that is True by default and 
  that will enable or disable Html cleaning when item is created.
  [gbastien]
- getConfigInfos now returns also MeetingConfig.itemPositiveDecidedStates as an
  array.
  [gbastien]
- Refactored getConfigInfos to manage groups using GroupInfo complexType instead
  ConfigInfo complexType.
  [gbastien]

2.0 (2017-01-25)
----------------

- Adapted code regarding integration of imio.annex into Products.PloneMeeting

1.8 (2016-08-17)
----------------

- Make sure history is saved when we patch it to change the creation comment
- Do no more create the item before checking for category validity, this could lead
  to problem where item was not deletable (validated while created for example)

1.7 (2016-08-03)
----------------

- Added possibility to pass aribitraty extra attributes when creating an item,
  for now it must correspond to an existing RichText field

1.6 (2016-05-13)
----------------
- Adapted code regarding changes in Products.PloneMeeting 4

1.5 (2015-04-01)
----------------
- If no 'preferredMeeting' is provided when creating an item, use 'whatever'
  or created item is not consistent

1.4 (2015-03-06)
----------------
- Calling getItemInfos will now also return the 'detailedDescription'
  as it can be used when creating an item
- Added parameter 'attribute' to CreationData and ItemInfo so we can specify
  a preferredMeeting when creating an item and we get the preferredMeeting when
  using getItemInfos

1.3 (2015-03-05)
----------------
- Added item creation date and modification date in ItemInfo (getItemInfo and searchItems)
- Added package version in the testConnection call
- Added SOAP call to getMeetingsAcceptingItems

1.2 (2015-02-27)
----------------
- Use with Products.PloneMeeting 3.3+
- Adapted tests to use IAnnexable.getAnnexesInOrder as IAnnexable.getAnnexes was removed

1.1 (2014-02-12)
----------------
- Use with Products.PloneMeeting 3.2+
- Handle case where libmagic could not determinate annex mimetype correctly (and added test)

1.0 (2014-01-07)
-----------------
- Renamed package from communesplone.ws4plonemeeting to imio.pm.ws
- Moved to Plone 4.3
- Use ZSI 2.1a1
- Avoid error if item created without a description or a decision (empty HTML field)

0.1 (2012-10-15)
----------------
- Initial release
- Added methods to 'getItemInfos', 'createItem', 'getConfigInfos', 'searchItems'
