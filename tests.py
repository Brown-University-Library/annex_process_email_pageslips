# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import logging, os, pprint, sys, unittest


## settings from env/activate
LOG_PATH = os.environ['EML_PGSLP__LOG_PATH']
LOG_LEVEL = os.environ['EML_PGSLP__LOG_LEVEL']  # 'DEBUG' or 'INFO'


## logging
log_level = { 'DEBUG': logging.DEBUG, 'INFO': logging.INFO }
logging.basicConfig(
    filename=LOG_PATH, level=log_level[LOG_LEVEL],
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S'
    )
log = logging.getLogger(__name__)
log.debug( 'log setup' )


## set up environment ##

sys.path.append( os.environ['EML_PGSLP__ENCLOSING_PROJECT_PATH'] )
from process_email_pageslips import utility_code

TEST_FILES_DIR_PATH = os.environ['EML_PGSLP__TEST_FILES_DIR_PATH']


class ItemListMakerTest( unittest.TestCase ):

    def setUp( self ):
        self.item_list_maker = utility_code.ItemListMaker()

    def test_make_lines( self ):
        with open( '%s/%s' % (TEST_FILES_DIR_PATH, 'testFile04_longNotes.txt') ) as f:
          text = f.read()
        lines = self.item_list_maker.make_lines( text )
        self.assertEqual(
          list,
          type(lines) )
        self.assertEqual(
          unicode,
          type(lines[0]) )

    ## test clean_lines()

    def test_clean_items_simple_good( self ):
        self.item_list_maker.items = [ [], ['a', 'b'], ['c', 'd'] ]
        self.item_list_maker.clean_items()
        self.assertEqual(
          [ ['a', 'b'], ['c', 'd'] ],  # initial empty list gone
          self.item_list_maker.items
          )

    def test_clean_items_single_extra_space( self ):
        self.item_list_maker.items = [ [], ['a', 'b', ''], ['c', 'd'] ]
        self.item_list_maker.clean_items()
        self.assertEqual(
          [ ['a', 'b'], ['c', 'd'] ],  # missing '' gone
          self.item_list_maker.items
          )

    def test_clean_items_multiple_extra_spaces( self ):
        self.item_list_maker.items = [ [], ['a', 'b', '', ''], ['c', 'd'] ]
        self.item_list_maker.clean_items()
        self.assertEqual(
          [ ['a', 'b'], ['c', 'd'] ],  # missing '' gone
          self.item_list_maker.items
          )

    ## test make_item_list()

    def test_single_pageslip( self ):
        with open( '%s/%s' % (TEST_FILES_DIR_PATH, 'testFile01_singleEntry.txt') ) as f:
          text = f.read()
        processed_data = self.item_list_maker.make_item_list( text )
        self.assertEqual( 1, len(processed_data) )  # 1 page-slip
        self.assertEqual( 39, len(processed_data[0]) )  # 39 lines in the first (and only) page-slip

    def test_single_short_pageslip( self ):
        with open( '%s/%s' % (TEST_FILES_DIR_PATH, 'testFile02_incorrectSciPickup.txt') ) as f:
          text = f.read()
        processed_data = self.item_list_maker.make_item_list( text )
        self.assertEqual( 1, len(processed_data) )  # 1 page-slip
        self.assertEqual( 35, len(processed_data[0]) )  # lines in the first (and only) page-slip

    def test_single_pageslip_no38( self ):
        with open( '%s/%s' % (TEST_FILES_DIR_PATH, 'testFile11_singleNo38.txt') ) as f:
          text = f.read()
        processed_data = self.item_list_maker.make_item_list( text )
        self.assertEqual( 1, len(processed_data) )  # 1 page-slip
        self.assertEqual( 39, len(processed_data[0]) )  # lines in the first (and only) page-slip

    def test_multiple_pageslips( self ):
        with open( '%s/%s' % (TEST_FILES_DIR_PATH, 'testFile03_itemNumberAddition.txt') ) as f:
          text = f.read()
        processed_data = self.item_list_maker.make_item_list( text )
        self.assertEqual( 6, len(processed_data) )  # page-slips
        self.assertEqual( 39, len(processed_data[0]) )  # lines

    def test_multiple_pageslips_one_missing_38( self ):
        with open( '%s/%s' % (TEST_FILES_DIR_PATH, 'testFile04_longNotes.txt') ) as f:
          text = f.read()
        processed_data = self.item_list_maker.make_item_list( text )
        # pprint.pprint( processed_data )
        self.assertEqual( 7, len(processed_data) )  # page-slips
        self.assertEqual( 39, len(processed_data[0]) )  # lines
        self.assertEqual( 'today. Thanks.', processed_data[1][-1].strip() )  # last line of second page-slip

    def test_multiple_pageslips_missing_brown_university_start( self ):
        with open( '%s/%s' % (TEST_FILES_DIR_PATH, 'testFile12_missing_brown_address.txt') ) as f:
          text = f.read()
        processed_data = self.item_list_maker.make_item_list( text )
        self.assertEqual( 6, len(processed_data) )  # page-slips

    def test_BrownU_in_author( self ):
        with open( '%s/%s' % (TEST_FILES_DIR_PATH, 'testFile14_BrownU_auth_confusion.txt') ) as f:
          text = f.read()
        processed_data = self.item_list_maker.make_item_list( text )
        # log.debug( 'processed_data, `%s`' % pprint.pprint(processed_data) )
        self.assertEqual( 5, len(processed_data) )  # 1 page-slip
        self.assertEqual( 39, len(processed_data[0]) )  # lines in the first (and only) page-slip

    def test_BrownU_in_title( self ):
        with open( '%s/%s' % (TEST_FILES_DIR_PATH, 'testFile13_BrownU_title_confusion.txt') ) as f:
          text = f.read()
        processed_data = self.item_list_maker.make_item_list( text )
        self.assertEqual( 1, len(processed_data) )  # 1 page-slip

    def test_BrownU_in_address( self):
        with open( '%s/%s' % (TEST_FILES_DIR_PATH, 'testFile15_BrownU_in_address.txt') ) as f:
            text = f.read()
        processed_data = self.item_list_maker.make_item_list( text )
        # pprint.pprint( processed_data )
        self.assertEqual( 3, len(processed_data) )

    ## end class ItemListMakerTest()


class InputOutputTest( unittest.TestCase ):
    """ Loops through source and lists output expectation. """

    def setUp(self):
        self.test_lst = [
            {'source': 'test_mail_01.txt',
                'explanation': 'single entry',
                'expected': [
                    u'foo'
                    ]
                },
        ]

    def test_processor(self):
        """ Checks processed-output of multiple files. """
        for source_dct in self.test_lst:
            filepath = '%s/%s' % ( TEST_FILES_DIR_PATH, source_dct['source'] )
            log.debug( 'testing source_file, ```%s```' % filepath )
            self.assertEqual( source_dct['expected'], utility_code.processor_wrapper( filepath ) )

    ## end class InputOutputTest()


class ParserTest( unittest.TestCase ):

    def setUp( self ):
        self.parser = utility_code.Parser()

    def test_parseNote(self):
        """ Tests note-parsing from lines of single pageslip. """
        ## with note
        single_pageslip = [
            '   Brown University', '   Gateway Services, Rockefeller Library', '   10 Prospect Street - Box A', '   Providence, RI 02912', '', '   05-27-05', '', '', '', '', '          barcode abc', '          name', '          BROWN UNIVERSITY', '          U LIBR-WEB SERV - BOX A', '          PROVIDENCE, RI 02912-9101', '', '', '   Please page this material and', '   forward to the circulation unit.', '', '', '   AUTHOR:  Darlington, Marwood,', '   Irish Orpheus, the life of Patrick S. Gilmore, ba', '   IMPRINT: Philadelphia, Olivier-Maney-Klein', '   PUB DATE: [1950]', '   DESC:    130 p. illus., ports. 21 cm', '   CALL NO: ML422.G48 D3', '   VOLUME:  ', '   BARCODE: 3 1236 07030 3881', '   STATUS: AVAILABLE', '   REC NO:  .i10295297', '   LOCATION: ANNEX', '   PICKUP AT: ROCK',
            '   NOTE: four score and ', '        seven years ago', '        something interesting happened', '', '', '   38' ]
        self.assertEqual(
            'four score and seven years ago something interesting happened',
            self.parser.parse_note( single_pageslip )
            )
        ## without note
        single_pageslip = [
            '   Brown University', '   Gateway Services, Rockefeller Library', '   10 Prospect Street - Box A', '   Providence, RI 02912', '', '   05-27-05', '', '', '', '', '          barcode abc', '          name', '          BROWN UNIVERSITY', '          U LIBR-WEB SERV - BOX A', '          PROVIDENCE, RI 02912-9101', '', '', '   Please page this material and', '   forward to the circulation unit.', '', '', '   AUTHOR:  Darlington, Marwood,', '   Irish Orpheus, the life of Patrick S. Gilmore, ba', '   IMPRINT: Philadelphia, Olivier-Maney-Klein', '   PUB DATE: [1950]', '   DESC:    130 p. illus., ports. 21 cm', '   CALL NO: ML422.G48 D3', '   VOLUME:  ', '   BARCODE: 3 1236 07030 3881', '   STATUS: AVAILABLE', '   REC NO:  .i10295297', '   LOCATION: ANNEX', '   PICKUP AT: ROCK',
            '   ', '', '', '', '', '   38' ]
        self.assertEqual(
            'no_note',
            self.parser.parse_note( single_pageslip )
            )
        ## if note contains quotes
        single_pageslip = [
            '   Brown University', '   Gateway Services, Rockefeller Library', '   10 Prospect Street - Box A', '   Providence, RI 02912', '', '   05-27-05', '', '', '', '', '          barcode abc', '          name', '          BROWN UNIVERSITY', '          U LIBR-WEB SERV - BOX A', '          PROVIDENCE, RI 02912-9101', '', '', '   Please page this material and', '   forward to the circulation unit.', '', '', '   AUTHOR:  Darlington, Marwood,', '   Irish Orpheus, the life of Patrick S. Gilmore, ba', '   IMPRINT: Philadelphia, Olivier-Maney-Klein', '   PUB DATE: [1950]', '   DESC:    130 p. illus., ports. 21 cm', '   CALL NO: ML422.G48 D3', '   VOLUME:  ', '   BARCODE: 3 1236 07030 3881', '   STATUS: AVAILABLE', '   REC NO:  .i10295297', '   LOCATION: ANNEX', '   PICKUP AT: ROCK',
            '   NOTE: four score and ', '        seven years ago', '        something "interesting" happened', '', '', '   38' ]
        self.assertEqual(
            "four score and seven years ago something 'interesting' happened",
            self.parser.parse_note( single_pageslip )
            )

    def test_parseBookBarcode(self):
        """ Tests book-barcode parsing from lines of single pageslip. """
        ## numeric barcode with spaces
        single_pageslip = ['   Brown University', '   Gateway Services, Rockefeller Library', '   10 Prospect Street - Box A', '   Providence, RI 02912', '', '   05-27-05', '', '', '', '', '          barcod', '          name', '          BROWN UNIVERSITY', '          U LIBR-WEB SERV - BOX A', '          PROVIDENCE, RI 02912-9101', '', '', '   Please page this material and', '   forward to the circulation unit.', '', '', '   AUTHOR:  Darlington, Marwood,', '   Irish Orpheus, the life of Patrick S. Gilmore, ba', '   IMPRINT: Philadelphia, Olivier-Maney-Klein', '   PUB DATE: [1950]', '   DESC:    130 p. illus., ports. 21 cm', '   CALL NO: ML422.G48 D3', '   VOLUME:  ', '   BARCODE: 3 1236 07030 3881', '   STATUS: AVAILABLE', '   REC NO:  .i10295297', '   LOCATION: ANNEX', '   PICKUP AT: ROCK', '   OPACMSG: ', '', '', '', '', '   38']
        self.assertEqual(
            '31236070303881',
            self.parser.parse_bookbarcode( single_pageslip )
            )
        ## 'JH' barcode
        single_pageslip = ['   Brown University', '   Gateway Services, Rockefeller Library', '   10 Prospect Street - Box A', '   Providence, RI 02912', '', '   Tue Nov 22 2005', '', '', '', '', '          barcode', '          name', '          BROWN UNIVERSITY', '          BOX 1234', '          PROVIDENCE, RI 02912-3198', '', '', '   Please page this material and', '   forward to the circulation unit.', '', '', '   AUTHOR:  Breggin, Peter Roger,', '   Toxic psychiatry : why therapy, empathy, and love', "   IMPRINT: New York : St. Martin's Press,", '   PUB DATE: 1991', '   DESC:    464 p. ; 24 cm', '   CALL NO: ', '   VOLUME:  ', '   BARCODE: JH16TV', '   STATUS: AVAILABLE', '   REC NO:  .i12345189', '   LOCATION: ANNEX HAY', '   PICKUP AT: Rockefeller Library', '', '', '', '', '', '   38:4']
        self.assertEqual(
            'JH16TV',
            self.parser.parse_bookbarcode( single_pageslip )
            )

    def test_parse_josiah_location_code(self):
        '''input page-slip; output Josiah location code (annex 'customer_code')'''
        ## 'ANNEX'
        single_pageslip = ['   Brown University', '   Gateway Services, Rockefeller Library', '   10 Prospect Street - Box A', '   Providence, RI 02912', '', '   05-27-05', '', '', '', '', '          barcod', '          name', '          BROWN UNIVERSITY', '          U LIBR-WEB SERV - BOX A', '          PROVIDENCE, RI 02912-9101', '', '', '   Please page this material and', '   forward to the circulation unit.', '', '', '   AUTHOR:  Darlington, Marwood,', '   Irish Orpheus, the life of Patrick S. Gilmore, ba', '   IMPRINT: Philadelphia, Olivier-Maney-Klein', '   PUB DATE: [1950]', '   DESC:    130 p. illus., ports. 21 cm', '   CALL NO: ML422.G48 D3', '   VOLUME:  ', '   BARCODE: 3 1236 07030 3881', '   STATUS: AVAILABLE', '   REC NO:  .i10295297', '   LOCATION: ANNEX', '   PICKUP AT: ROCK', '   OPACMSG: ', '', '', '', '', '   38']
        self.assertEqual(
            'QS',
            self.parser.parse_josiah_location_code( single_pageslip )
            )
        ## empty
        single_pageslip = ['   Brown University', '   Gateway Services, Rockefeller Library', '   10 Prospect Street - Box A', '   Providence, RI 02912', '', '   05-27-05', '', '', '', '', '          barcod', '          name', '          BROWN UNIVERSITY', '          U LIBR-WEB SERV - BOX A', '          PROVIDENCE, RI 02912-9101', '', '', '   Please page this material and', '   forward to the circulation unit.', '', '', '   AUTHOR:  Darlington, Marwood,', '   Irish Orpheus, the life of Patrick S. Gilmore, ba', '   IMPRINT: Philadelphia, Olivier-Maney-Klein', '   PUB DATE: [1950]', '   DESC:    130 p. illus., ports. 21 cm', '   CALL NO: ML422.G48 D3', '   VOLUME:  ', '   BARCODE: 3 1236 07030 3881', '   STATUS: AVAILABLE', '   REC NO:  .i10295297', '   LOCATION:', '   PICKUP AT: ROCK', '   OPACMSG: ', '', '', '', '', '   38']
        self.assertEqual(
            '?',
            self.parser.parse_josiah_location_code( single_pageslip )
            )
        ## no match
        single_pageslip = ['   Brown University', '   Gateway Services, Rockefeller Library', '   10 Prospect Street - Box A', '   Providence, RI 02912', '', '   05-27-05', '', '', '', '', '          barcod', '          name', '          BROWN UNIVERSITY', '          U LIBR-WEB SERV - BOX A', '          PROVIDENCE, RI 02912-9101', '', '', '   Please page this material and', '   forward to the circulation unit.', '', '', '   AUTHOR:  Darlington, Marwood,', '   Irish Orpheus, the life of Patrick S. Gilmore, ba', '   IMPRINT: Philadelphia, Olivier-Maney-Klein', '   PUB DATE: [1950]', '   DESC:    130 p. illus., ports. 21 cm', '   CALL NO: ML422.G48 D3', '   VOLUME:  ', '   BARCODE: 3 1236 07030 3881', '   STATUS: AVAILABLE', '   REC NO:  .i10295297', '   LOCATION: abc', '   PICKUP AT: ROCK', '   OPACMSG: ', '', '', '', '', '   38']
        self.assertEqual(
            'unknown_location',
            self.parser.parse_josiah_location_code( single_pageslip )
            )

    def test_parse_title(self):
        '''input pageslip lines; output item title'''
        ## with 'TITLE' prefix
        single_pageslip = ['   Brown University', '   Gateway Services, Rockefeller Library', '   10 Prospect Street - Box A', '   Providence, RI 02912', '', '   05-27-05', '', '', '', '', '          barcode abc', '          name', '          BROWN UNIVERSITY', '          U LIBR-WEB SERV - BOX A', '          PROVIDENCE, RI 02912-9101', '', '', '   Please page this material and', '   forward to the circulation unit.', '', '', '   AUTHOR:  Darlington, Marwood,', '   TITLE:   Draft resistance and social change', '   IMPRINT: Philadelphia, Olivier-Maney-Klein', '   PUB DATE: [1950]', '   DESC:    130 p. illus., ports. 21 cm', '   CALL NO: ML422.G48 D3', '   VOLUME:  ', '   BARCODE: 3 1236 07030 3881', '   STATUS: AVAILABLE', '   REC NO:  .i10295297', '   LOCATION: ANNEX', '   PICKUP AT: ROCK', '   OPACMSG: ', '', '', '', '', '   38']
        self.assertEqual(
            'Draft resistance and social change',
            self.parser.parse_title( single_pageslip )
            )
        ## without 'TITLE' prefix (happens when title is long) or even AUTHOR or IMPRINT as sometimes happens
        single_pageslip = ['   Brown University', '   Gateway Services, Rockefeller Library', '   10 Prospect Street - Box A', '   Providence, RI 02912', '', '   05-27-05', '', '', '', '', '          barcode abc', '          name', '          BROWN UNIVERSITY', '          U LIBR-WEB SERV - BOX A', '          PROVIDENCE, RI 02912-9101', '', '', '   Please page this material and', '   forward to the circulation unit.', '', '', '   no_a-u-t-h-or:  Darlington, Marwood,', '   Irish Orpheus, the life of Patrick S. Gilmore, ba', '   no_i-m-p-r-i-n-t: Philadelphia, Olivier-Maney-Klein', '   PUB DATE: [1950]', '   DESC:    130 p. illus., ports. 21 cm', '   CALL NO: ML422.G48 D3', '   VOLUME:  ', '   BARCODE: 3 1236 07030 3881', '   STATUS: AVAILABLE', '   REC NO:  .i10295297', '   LOCATION: ANNEX', '   PICKUP AT: ROCK', '   OPACMSG: ', '', '', '', '', '   38']
        self.assertEqual(
            'Irish Orpheus, the life of Patrick S. Gilmore, ba',
            self.parser.parse_title( single_pageslip )
            )
        ## title contains quotes
        single_pageslip = ['   Brown University', '   Gateway Services, Rockefeller Library', '   10 Prospect Street - Box A', '   Providence, RI 02912', '', '   05-27-05', '', '', '', '', '          barcode abc', '          name', '          BROWN UNIVERSITY', '          U LIBR-WEB SERV - BOX A', '          PROVIDENCE, RI 02912-9101', '', '', '   Please page this material and', '   forward to the circulation unit.', '', '', '   AUTHOR:  Darlington, Marwood,', '   TITLE:   Draft resistance "and" social change', '   IMPRINT: Philadelphia, Olivier-Maney-Klein', '   PUB DATE: [1950]', '   DESC:    130 p. illus., ports. 21 cm', '   CALL NO: ML422.G48 D3', '   VOLUME:  ', '   BARCODE: 3 1236 07030 3881', '   STATUS: AVAILABLE', '   REC NO:  .i10295297', '   LOCATION: ANNEX', '   PICKUP AT: ROCK', '   OPACMSG: ', '', '', '', '', '   38']
        self.assertEqual(
            "Draft resistance 'and' social change",
            self.parser.parse_title( single_pageslip )
            )
        ## strange BrownU title
        single_pageslip = [u'   Brown University', u'   Gateway Services, Rockefeller Library', u'   10 Prospect Street - Box A', u'   Providence, RI 02912', u'', u'   Thu Jul 23 2015', u'', u'', u'', u'', u'          21234567890125', u'          HAY ARCHIVES STAFF', u'          JOHN HAY LIBRARY', u'          BOX A', u'', u'', u'', u'   Please page this material and', u'   forward to the circulation unit.', u'', u'', u'   Brown University. Office of Aaaaaaaaaa Bbbbbbbbb', u"   Brown University honors theses, 1959. Vol. 14,", u'   IMPRINT:', u'   PUB DATE:', u'   DESC:    87.25 linear feet (209 document boxes)', u'   CALL NO: OF-1X-1 Box 1', u'   VOLUME:  Box 1', u'   BARCODE: 3 1234 12345 1234', u'   STATUS: AVAILABLE', u'   REC NO:  .i12345678', u'   LOCATION: ANNEX HAY', u'   PICKUP AT: John Hay Library', u'   NOTE: HH hhhhhhhh', u'', u'', u'', u'', u'   38:3']
        self.assertEqual(
            'Brown University honors theses, 1959. Vol. 14,',
            self.parser.parse_title( single_pageslip )
            )

    # end class ParserTest


class MiscellaneousFunctionTester(unittest.TestCase):

  def test_convertJosiahLocationCode(self):
    '''input page-slip; output Annex customer-code (josiah 'location-code')'''

    josiah_location = 'ANNEX'
    expected = 'QS'
    result = utility_code.convertJosiahLocationCode( josiah_location )
    self.assertEqual( expected, result, '\n- expected is: %s\n  - result is: %s' % (expected, result) )

    # end def test_convertJosiahLocationCode()

  def test_convertJosiahPickupAtCode(self):
    """ Takes the josiah `pickup-at` code; returns the annex `delivery-stop` code."""
    self.assertEqual(
      'RO',
      utility_code.convertJosiahPickupAtCode('ROCK') )
    self.assertEqual(
      'HA',
      utility_code.convertJosiahPickupAtCode('John Hay Library') )
    self.assertEqual(
      'ED',
      utility_code.convertJosiahPickupAtCode('Elec. Delivery (Annex Articles)') )

  def test_determineCount(self):

    TEST_FILES_DIR_PATH = os.environ['EML_PGSLP__TEST_FILES_DIR_PATH']

    # single pageslip
    number_of_parsed_items = 1
    # file_reference = open( 'test_files/testFile01_singleEntry.txt' )
    file_reference = open( '%s/%s' % (TEST_FILES_DIR_PATH, 'testFile01_singleEntry.txt') )
    data = file_reference.read()
    lines = data.split( '\n' )
    expected = 1
    result = utility_code.determineCount( number_of_parsed_items, lines )
    self.assertEqual( expected, result, '\n- expected is: %s\n  - result is: %s' % (expected, result) )

    # single short pageslip
    number_of_parsed_items = 5
    # file_reference = open( 'test_files/testFile02_incorrectSciPickup.txt' )
    file_reference = open( '%s/%s' % (TEST_FILES_DIR_PATH, 'testFile02_incorrectSciPickup.txt') )
    data = file_reference.read()
    lines = data.split( '\n' )
    expected = 5
    result = utility_code.determineCount( number_of_parsed_items, lines )
    self.assertEqual( expected, result, '\n- expected is: %s\n  - result is: %s' % (expected, result) )

    # single pageslip, no '38...'
    number_of_parsed_items = 1
    # file_reference = open( 'test_files/testFile11_singleNo38.txt' )
    file_reference = open( '%s/%s' % (TEST_FILES_DIR_PATH, 'testFile11_singleNo38.txt') )
    data = file_reference.read()
    lines = data.split( '\n' )
    expected = 1
    result = utility_code.determineCount( number_of_parsed_items, lines )
    self.assertEqual( expected, result, '\n- expected is: %s\n  - result is: %s' % (expected, result) )

    # multiple pageslips
    number_of_parsed_items = 6
    # file_reference = open( 'test_files/testFile03_itemNumberAddition.txt' )
    file_reference = open( '%s/%s' % (TEST_FILES_DIR_PATH, 'testFile03_itemNumberAddition.txt') )
    data = file_reference.read()
    lines = data.split( '\n' )
    expected = 6
    result = utility_code.determineCount( number_of_parsed_items, lines )
    self.assertEqual( expected, result, '\n- expected is: %s\n  - result is: %s' % (expected, result) )

    # multiple pageslips, one missing last '38...' line
    number_of_parsed_items = 7
    # file_reference = open( 'test_files/testFile04_longNotes.txt' )
    file_reference = open( '%s/%s' % (TEST_FILES_DIR_PATH, 'testFile04_longNotes.txt') )
    data = file_reference.read()
    lines = data.split( '\n' )
    expected = 7
    result = utility_code.determineCount( number_of_parsed_items, lines )
    self.assertEqual( expected, result, '\n- expected is: %s\n  - result is: %s' % (expected, result) )

    # multiple pageslips, first two without the usual 'Brown University' four address lines
    number_of_parsed_items = 6
    # file_reference = open( 'test_files/testFile12_missing_brown_address.txt' )
    file_reference = open( '%s/%s' % (TEST_FILES_DIR_PATH, 'testFile12_missing_brown_address.txt') )
    data = file_reference.read()
    lines = data.split( '\n' )
    expected = 6
    result = utility_code.determineCount( number_of_parsed_items, lines )
    self.assertEqual( expected, result, '\n- expected is: %s\n  - result is: %s' % (expected, result) )

    # end def test_determineCount()

  def test_parseJosiahPickupAtCode(self):
    """ Takes lines list, returns josiah `pickup-at` code (the annex `delivery-stop` code). """
    # 'PICKUP AT: ROCK'
    lines = ['   Brown University', '   Gateway Services, Rockefeller Library', '   10 Prospect Street - Box A', '   Providence, RI 02912', '', '   05-27-05', '', '', '', '', '          barcod', '          name', '          BROWN UNIVERSITY', '          U LIBR-WEB SERV - BOX A', '          PROVIDENCE, RI 02912-9101', '', '', '   Please page this material and', '   forward to the circulation unit.', '', '', '   AUTHOR:  Darlington, Marwood,', '   Irish Orpheus, the life of Patrick S. Gilmore, ba', '   IMPRINT: Philadelphia, Olivier-Maney-Klein', '   PUB DATE: [1950]', '   DESC:    130 p. illus., ports. 21 cm', '   CALL NO: ML422.G48 D3', '   VOLUME:  ', '   BARCODE: 3 1236 07030 3881', '   STATUS: AVAILABLE', '   REC NO:  .i10295297', '   LOCATION: ANNEX', '   PICKUP AT: ROCK', '   OPACMSG: ', '', '', '', '', '   38']
    self.assertEqual( 'RO', utility_code.parseJosiahPickupAtCode(lines) )
    # 'PICKUP AT: Elec. Delivery (Annex Articles)'
    lines = ['   Brown University', '   Gateway Services, Rockefeller Library', '   10 Prospect Street - Box A', '   Providence, RI 02912', '', '   Mon Jan 26 2015', '', '', '', '', '          2 1236 00801 6417', '          KYLE DAVID GION', '          BROWN UNIVERSITY', '          BOX 2851', '          PROVIDENCE, RI 02912-2851', '', '', '   Please page this material and', '   forward to the circulation unit.', '', '', '   AUTHOR:', '   Journal of social and personal relationships', '   IMPRINT: London : Sage Publications,', '   PUB DATE: c1984-', '   DESC:    v. ; 22 cm', '   CALL NO: HM132 .J86x 14 (1997)', '   VOLUME:  14 (1997)', '   BARCODE: 3 1236 09014 6286', '   STATUS: AVAILABLE', '   REC NO:  .i11901707', '   LOCATION: ANNEX', '   PICKUP AT: Elec. Delivery (Annex Articles)', '', '', '', '', '', '   38:16']
    self.assertEqual( 'ED', utility_code.parseJosiahPickupAtCode(lines) )
    # 'PICKUP AT:'
    lines = ['   Brown University', '   Gateway Services, Rockefeller Library', '   10 Prospect Street - Box A', '   Providence, RI 02912', '', '   Tue Nov 22 2005', '', '', '', '', '          1 1234 12345 1234', '          name', '          BROWN UNIVERSITY', '          BOX 1234', '          PROVIDENCE, RI 02912-3198', '', '', '   Please page this material and', '   forward to the circulation unit.', '', '', '   AUTHOR:  Breggin, Peter Roger,', '   Toxic psychiatry : why therapy, empathy, and love', "   IMPRINT: New York : St. Martin's Press,\n", '   PUB DATE: 1991', '   DESC:    464 p. ; 24 cm', '   CALL NO: ', '   VOLUME:  ', '   BARCODE: JH16TV', '   STATUS: AVAILABLE', '   REC NO:  .i12345189', '   LOCATION: ANNEX', '   PICKUP AT:', '', '', '', '', '', '   38:4']
    self.assertEqual( '?', utility_code.parseJosiahPickupAtCode(lines) )

  def test_parsePatronBarcode(self):
    '''input pageslip lines; output item barcode'''

    single_pageslip = ['   Brown University', '   Gateway Services, Rockefeller Library', '   10 Prospect Street - Box A', '   Providence, RI 02912', '', '   05-27-05', '', '', '', '', '          barcode abc', '          name', '          BROWN UNIVERSITY', '          U LIBR-WEB SERV - BOX A', '          PROVIDENCE, RI 02912-9101', '', '', '   Please page this material and', '   forward to the circulation unit.', '', '', '   AUTHOR:  Darlington, Marwood,', '   Irish Orpheus, the life of Patrick S. Gilmore, ba', '   IMPRINT: Philadelphia, Olivier-Maney-Klein', '   PUB DATE: [1950]', '   DESC:    130 p. illus., ports. 21 cm', '   CALL NO: ML422.G48 D3', '   VOLUME:  ', '   BARCODE: 3 1236 07030 3881', '   STATUS: AVAILABLE', '   REC NO:  .i10295297', '   LOCATION: ANNEX', '   PICKUP AT: ROCK', '   OPACMSG: ', '', '', '', '', '   38']
    expected = 'barcodeabc'
    result = utility_code.parsePatronBarcode( single_pageslip )
    self.assertEqual( expected, result, '\n- expected is: %s\n  - result is: %s' % (expected, result) )

    # blank barcode
    single_pageslip = ['   Brown University', '   Gateway Services, Rockefeller Library', '   10 Prospect Street - Box A', '   Providence, RI 02912', '', '   05-27-05', '', '', '', '', '', '          name', '          BROWN UNIVERSITY', '          U LIBR-WEB SERV - BOX A', '          PROVIDENCE, RI 02912-9101', '', '', '   Please page this material and', '   forward to the circulation unit.', '', '', '   AUTHOR:  Darlington, Marwood,', '   Irish Orpheus, the life of Patrick S. Gilmore, ba', '   IMPRINT: Philadelphia, Olivier-Maney-Klein', '   PUB DATE: [1950]', '   DESC:    130 p. illus., ports. 21 cm', '   CALL NO: ML422.G48 D3', '   VOLUME:  ', '   BARCODE: 3 1236 07030 3881', '   STATUS: AVAILABLE', '   REC NO:  .i10295297', '   LOCATION: ANNEX', '   PICKUP AT: ROCK', '   OPACMSG: ', '', '', '', '', '   38']
    expected = '?'
    result = utility_code.parsePatronBarcode( single_pageslip )
    self.assertEqual( expected, result, '\n- expected is: %s\n  - result is: %s' % (expected, result) )

    # end def test_parsePatronBarcode()

  def test_parsePatronName(self):
    '''input pageslip lines; output patron name'''

    single_pageslip = ['   Brown University', '   Gateway Services, Rockefeller Library', '   10 Prospect Street - Box A', '   Providence, RI 02912', '', '   05-27-05', '', '', '', '', '          barcod', '          name', '          BROWN UNIVERSITY', '          U LIBR-WEB SERV - BOX A', '          PROVIDENCE, RI 02912-9101', '', '', '   Please page this material and', '   forward to the circulation unit.', '', '', '   AUTHOR:  Darlington, Marwood,', '   Irish Orpheus, the life of Patrick S. Gilmore, ba', '   IMPRINT: Philadelphia, Olivier-Maney-Klein', '   PUB DATE: [1950]', '   DESC:    130 p. illus., ports. 21 cm', '   CALL NO: ML422.G48 D3', '   VOLUME:  ', '   BARCODE: 3 1236 07030 3881', '   STATUS: AVAILABLE', '   REC NO:  .i10295297', '   LOCATION: ANNEX', '   PICKUP AT: ROCK', '   OPACMSG: ', '', '', '', '', '   38']
    expected = 'name'
    result = utility_code.parsePatronName( single_pageslip )
    self.assertEqual( expected, result, '\n- expected is: %s\n  - result is: %s' % (expected, result) )

    # end def test_parsePatronName()

  def test_parseRecordNumber(self):
    '''input page-slip; output record-number'''

    single_pageslip = ['   Brown University', '   Gateway Services, Rockefeller Library', '   10 Prospect Street - Box A', '   Providence, RI 02912', '', '   05-27-05', '', '', '', '', '          barcod', '          name', '          BROWN UNIVERSITY', '          U LIBR-WEB SERV - BOX A', '          PROVIDENCE, RI 02912-9101', '', '', '   Please page this material and', '   forward to the circulation unit.', '', '', '   AUTHOR:  Darlington, Marwood,', '   Irish Orpheus, the life of Patrick S. Gilmore, ba', '   IMPRINT: Philadelphia, Olivier-Maney-Klein', '   PUB DATE: [1950]', '   DESC:    130 p. illus., ports. 21 cm', '   CALL NO: ML422.G48 D3', '   VOLUME:  ', '   BARCODE: 3 1236 07030 3881', '   STATUS: AVAILABLE', '   REC NO:  .i10295297', '   LOCATION: ANNEX', '   PICKUP AT: ROCK', '   OPACMSG: ', '', '', '', '', '   38']

    expected = '.i10295297'
    result = utility_code.parseRecordNumber( single_pageslip )
    self.assertEqual( expected, result, '\n- expected is: %s\n  - result is: %s' % (expected, result) )

    # end def test_parseRecordNumber()

  def test_prepareDateTimeStamp(self):
    '''sending a known time to check formatting'''

    from datetime import datetime
    test_date = datetime(2005, 7, 13, 13, 41, 39, 48634)   # 'Wed Jul 13 13:41:39 EDT 2005'

    expected = '2005-07-13T13:41:39'
    result = utility_code.prepareDateTimeStamp( test_date )
    self.assertEqual( expected, result, '\n- expected is: %s\n  - result is: %s' % (expected, result) )

    expected = 19
    date_time_stamp = utility_code.prepareDateTimeStamp( test_date )
    result = len( date_time_stamp )
    self.assertEqual( expected, result, '\n- expected is: %s\n  - result is: %s' % (expected, result) )

    # end def test_prepareDateTimeStamp()

  def test_prepareLasDate(self):
    '''sending a known time to check formatting'''

    from datetime import datetime

    # with date
    test_date = datetime(2005, 7, 13, 13, 41, 39, 48634)   # 'Wed Jul 13 13:41:39 EDT 2005'
    expected = 'Wed Jul 13 2005'
    result = utility_code.prepareLasDate( test_date )
    self.assertEqual( expected, result, '\n- expected is: %s\n  - result is: %s' % (expected, result) )

    # without date
    returned_date_string = utility_code.prepareLasDate()
    expected = 15
    result = len( returned_date_string )
    self.assertEqual( expected, result, '\n- expected is: %s\n  - result is: %s' % (expected, result) )

    # end def test_prepareLasDate()

  # end class MiscellaneousFunctionTester



if __name__ == "__main__":
  unittest.main()
