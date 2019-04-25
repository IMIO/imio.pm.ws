# -*- coding: utf-8 -*-

from plone.transformchain.transformer import Transformer
from z3c.soap.interfaces import ISOAPRequest


class SoapAwareTransformer(Transformer):
    """Do not apply transform on SOAP requests."""

    def __call__(self, request, result, encoding):
        # Don't transform SOAP requests
        if ISOAPRequest.providedBy(request):
            return None

        return super(SoapAwareTransformer, self).__call__(request, result, encoding)
