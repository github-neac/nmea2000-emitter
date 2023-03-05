'''
Support for proprietary messages from FURUNO.
'''
# pylint: disable=wildcard-import,unused-wildcard-import
from decimal import Decimal
import re

from ... import nmea
from ...nmea_utils import *


class FEC(nmea.ProprietarySentence):
    '''
    Generic Furuno Response Message
    '''
    sentence_types = {}
    def __new__(_cls, manufacturer, data):
        '''
        Return the correct sentence type based on the first field
        '''
        sentence_type = data[1].upper()
        name = manufacturer + 'R' + sentence_type
        if name not in _cls.sentence_types:
            # GPATT does not have a sentence type
            if FECRGPATT.match(data):
                return super(FEC, FECRGPATT).__new__(FECRGPATT)
        cls = _cls.sentence_types.get(name, FEC)
        return super(FEC, cls).__new__(cls)


class FECRGPATT(FEC):
    '''
    FURUNO proprietary Pitch/Roll sentence
    '''
    @staticmethod
    def match(data):
        return re.match(r'^\d{6}\.\d{2,3}$', data[1])

    def __init__(self, *args, **kwargs):
        self.subtype = 'GPATT'
        super(FECRGPATT, self).__init__(*args, **kwargs)

    fields = (
        ('Heading Angle', 'true_heading', float),
        ('Roll Angle', 'roll', float),
        ('Pitch Angle', 'pitch', float),
    )


class FECRGPHVE(FEC):
    '''
    FURUNO HVE Message
    '''
 
    @staticmethod
    def match(data):
        return re.match(r'^\d{6}\.\d{2,3}$', data[1])

    def __init__(self, *args, **kwargs):
        self.subtype = 'GPHVE'
        super(FECRGPHVE, self).__init__(*args, **kwargs)

    fields = (
        ('Heave in meters and decimals', 'gphve', float),
        ('Status', 'status'),
    )

