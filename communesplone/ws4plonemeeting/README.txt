WSDL management :
-----------------

The files WS4PM_server.py, WS4PM_services.py and WS4PM_services_types.py are created using the following command :

bin/wsdl2py --file src/communesplone.ws4plonemeeting/communesplone/ws4plonemeeting/currentWSDL.txt -o src/communesplone.ws4plonemeeting/communesplone/ws4plonemeeting -b

bin/wsdl2py is available when the egg "ZSI" is installed.

The WSDL describing the SOAP service is available when the package is installed in a Plone Site by accessing "http://my_plone_site_url/ws4pm.wsdl"

For more informations about the webservice itself, read the docs/README.txt at the root of the communesplone.ws4plonemeeting egg