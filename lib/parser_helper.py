# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import logging, os, pprint, sys


log = logging.getLogger(__name__)
if not logging._handlers:  # true when module accessed by queue-jobs
    LOG_PATH = os.environ['EML_PGSLP__LOG_PATH']
    LOG_LEVEL = os.environ['EML_PGSLP__LOG_LEVEL']  # 'DEBUG' or 'INFO'
    log_level = { 'DEBUG': logging.DEBUG, 'INFO': logging.INFO }
    logging.basicConfig(
        filename=LOG_PATH, level=log_level[LOG_LEVEL],
        format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
        datefmt='%d/%b/%Y %H:%M:%S'
        )
    log.debug( 'handler set' )
log.debug( 'START' )

cwd = os.getcwd()  # so this assumes the cron call has cd-ed into the project directory
if cwd not in sys.path:
    sys.path.append( cwd )
project_parent = os.environ['EML_PGSLP__ENCLOSING_PROJECT_PATH']
if project_parent not in sys.path:
    sys.path.append( project_parent )


import utility_code


class Parser( object ):
    """ Parses data-fields from a single pageslip's lines.
      TODO: - refactor rest of parsing functions into here.
            - refactor code to call this new parse_all() function from the controller (now for testing only) """

    def parse_all( self, single_pageslip_lines ):
        data_dct = self.prep_data_dct( single_pageslip_lines )
        full_line = '''"%s","%s","%s","%s","%s","%s","%s","%s","%s"''' % (
            data_dct['record_number'],
            data_dct['book_barcode'],
            data_dct['las_delivery_stop'],
            data_dct['las_customer_code'],
            data_dct['patron_name'],
            data_dct['patron_barcode'],
            data_dct['title'],
            data_dct['las_date'],
            data_dct['note'] )
        log.debug( 'full_line, ```%s```' % full_line )
        return full_line

    def prep_data_dct( self, single_pageslip_lines ):
        """ Calls individual parser functions.
            Called by: we'll see. """
        dct = {}
        dct['record_number'] = utility_code.parseRecordNumber( single_pageslip_lines )
        dct['book_barcode'] = self.parse_bookbarcode( single_pageslip_lines )
        dct['las_delivery_stop'] = utility_code.parseJosiahPickupAtCode(single_pageslip_lines)
        dct['las_customer_code'] = self.parse_josiah_location_code( single_pageslip_lines )
        dct['patron_name'] = utility_code.parsePatronName( single_pageslip_lines )
        dct['patron_barcode'] = utility_code.parsePatronBarcode( single_pageslip_lines )
        dct['title'] = self.parse_title( single_pageslip_lines )
        dct['las_date'] = utility_code.prepareLasDate()
        dct['note'] = self.parse_note( single_pageslip_lines )
        log.debug( 'data_dct, ```%s```' % pprint.pformat(dct) )
        return dct

    def parse_note( self, single_pageslip_lines ):
        """ Extracts possible note from lines of a single pageslip.
            Called by controller.py """
        initial_note = self.grab_note( single_pageslip_lines )
        cleaned_note = self.clean_note( initial_note )
        return cleaned_note

    def grab_note( self, pageslip_lines ):
        """ Grabs initial note string.
            Called by parse_note() """
        note = ''
        ready_flag = 'red'
        for line in pageslip_lines:
          if 'PICKUP AT:' in line:
            ready_flag = 'yellow'
          elif 'NOTE:' in line and ready_flag == 'yellow':
            ready_flag = 'green'
            note = line.replace( 'NOTE:', '' ).strip()
          elif ready_flag == 'green' and len( line.strip() ) > 0 and '38' not in line:
            note = note + ' ' + line.strip()
        return note

    def clean_note( self, initial_note ):
        """ Removes spaces from note, or sets default note.
            Called by parse_note() """
        cleaned_note = initial_note.replace( '  ', ' ' )
        cleaned_note = cleaned_note.replace( '"', u"'" )
        cleaned_note = cleaned_note.replace( 'OPACMSG:', '' )
        cleaned_note = cleaned_note.strip()
        if len( cleaned_note.strip() ) == 0:
          cleaned_note = 'no_note'
        return cleaned_note

    # def clean_note( self, initial_note ):
    #     """ Removes spaces from note, or sets default note.
    #         Called by parse_note() """
    #     cleaned_note = initial_note.replace( '  ', ' ' )
    #     cleaned_note = cleaned_note.replace( '"', u"'" )
    #     if len( cleaned_note.strip() ) == 0:
    #       cleaned_note = 'no_note'
    #     return cleaned_note

    def parse_bookbarcode( self, single_page_slip ):
        """ Parses book-barcode from lines of a single pageslip.
            Called by controller.py """
        book_barcode = 'init'
        for line in single_page_slip:
            stripped_line = line.strip()
            if 'BARCODE:' in stripped_line:
                temp_string = stripped_line[8:]   # gets everything after 'BARCODE:'
                temp_string = temp_string.strip()   # removes outside whitespace, leaving barcode possibly containing space-characters
                book_barcode = temp_string.replace( ' ', '' )
                break
        log.debug( 'book-barcode, `%s`' % book_barcode )
        return book_barcode

    # def parse_bookbarcode( self, single_page_slip ):
    #     """ Parses book-barcode from lines of a single pageslip.
    #         Called by controller.py """
    #     book_barcode = 'init'
    #     for line in single_page_slip:
    #         stripped_line = line.strip()
    #         if 'BARCODE:' in stripped_line:
    #             temp_string = stripped_line[8:]   # gets everything after 'BARCODE:'
    #             temp_string = temp_string.strip()   # removes outside whitespace, leaving barcode possibly containing space-characters
    #             return_val = temp_string.replace( ' ', '' )
    #             break
    #     log.debug( 'book-barcode, `%s`' % return_val )
    #     return return_val

    def parse_josiah_location_code( self, single_page_slip ):
        '''
        - Purpose: to extract an las 'customer-code' from a page-slip's josiah 'location-code'.
        - Called by: opac_to_las_python_parser_code.controller
        '''
        return_val = '?'
        for line in single_page_slip:
            stripped_line = line.strip()
            if 'LOCATION:' in stripped_line:
                temp_string = stripped_line[9:]   # gets everything after 'LOCATION:'
                temp_string = temp_string.strip()   # removes outside whitespace, leaving Josiah location
                if not temp_string == '':
                    return_val = utility_code.convertJosiahLocationCode( temp_string )
                break
        return return_val

    def parse_title( self, pageslip_lines ):
        """ Extracts item title from lines of a pageslip.
            Called by: opac_to_las_python_parser_code.controller() """
        counter = 0
        title_line = ''
        for line in pageslip_lines:
            if 'TITLE:' in line:
                title_line = line.replace( 'TITLE:', '' )
                break
            elif 'PUB DATE:' in line:   # means that the title was too long to have a label
                title_line = pageslip_lines[ counter - 2 ]   # two lines above 'PUB DATE:'
                break
            counter = counter + 1
        stripped_title = title_line.strip()
        dequoted_title = stripped_title.replace( '"', "'" )
        return dequoted_title

    ## end class Parser()
