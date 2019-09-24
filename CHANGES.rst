Changelog
=========

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
