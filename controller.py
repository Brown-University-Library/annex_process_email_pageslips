# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime, logging, os, pprint, shutil, smtplib, string, sys
from email.Header import Header
from email.mime.text import MIMEText
sys.path.append( os.environ['EML_PGSLP__ENCLOSING_PROJECT_PATH'] )

from process_email_pageslips.lib import utility_code
from process_email_pageslips.lib.utility_code import Mailer


logging.basicConfig(
    filename=os.environ['EML_PGSLP__LOG_PATH'],
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S',
    )
log = logging.getLogger(__name__)
log.debug( '\n\nstarting log\n============' )


class Controller(object):
    """ Manages steps. """

    def __init__( self ):
        self.PATH_TO_ARCHIVES_ORIGINALS_DIRECTORY = os.environ['EML_PGSLP__PATH_TO_ARCHIVES_ORIGINALS_DIRECTORY']
        self.PATH_TO_ARCHIVES_PARSED_DIRECTORY = os.environ['EML_PGSLP__PATH_TO_ARCHIVES_PARSED_DIRECTORY']
        self.PATH_TO_PARSED_ANNEX_COUNT_DIRECTORY = os.environ['EML_PGSLP__PATH_TO_PARSED_ANNEX_COUNT_DIRECTORY']
        self.PATH_TO_PARSED_ANNEX_DATA_DIRECTORY = os.environ['EML_PGSLP__PATH_TO_PARSED_ANNEX_DATA_DIRECTORY']
        self.PATH_TO_SOURCE_FILE = os.environ['EML_PGSLP__PATH_TO_SOURCE_FILE']
        self.PATH_TO_SOURCE_FILE_DIRECTORY = os.environ['EML_PGSLP__PATH_TO_SOURCE_FILE_DIRECTORY']

    def process_requests( self ):
        """ Steps caller.
            Called by ```if __name__ == '__main__':``` """
        log.debug( 'starting process_requests()' )
        self.check_paths()
        data = self.file_check()
        if data:
            date_stamp = utility_code.prepareDateTimeStamp( datetime.datetime.now() )
            self.copy_original_to_archives( date_stamp )
            self.post_original_to_db( data, date_stamp )
            pageslips_list = self.make_pageslips_list( data )
            gaf_list = self.make_gaf_list( pageslips_list )
            unicode_string_data = self.post_parsed_to_db( gaf_list, date_stamp )
            self.save_parsed_to_archives( date_stamp, unicode_string_data )
            count = self.determine_count( pageslips_list )
            self.save_count_and_data_to_gfa_dirs( count, pageslips_list )
            self.delete_original()
        log.debug( 'processing completed' )

    def check_paths( self ):
        """ Ensures all paths are correct.
            Called by process_requests() """
        check_a = utility_code.checkDirectoryExistence( self.PATH_TO_SOURCE_FILE_DIRECTORY )
        check_b = utility_code.checkDirectoryExistence( self.PATH_TO_ARCHIVES_ORIGINALS_DIRECTORY )
        check_c = utility_code.checkDirectoryExistence( self.PATH_TO_ARCHIVES_PARSED_DIRECTORY )
        check_d = utility_code.checkDirectoryExistence( self.PATH_TO_PARSED_ANNEX_DATA_DIRECTORY )
        check_e = utility_code.checkDirectoryExistence( self.PATH_TO_PARSED_ANNEX_COUNT_DIRECTORY )
        if check_a == 'exists' and check_b == 'exists' and check_c == 'exists' and check_d == 'exists' and check_e == 'exists':
          log.debug( 'path check passed' )
        else:
          message='path check failed; quitting'
          log.error( message )
          sys.exit( message )
        return

    def file_check( self ):
        """ Sees if there is a file waiting; returns unicode-text if so.
            Called by process_requests() """
        try:
          file_handler = open( self.PATH_TO_SOURCE_FILE )
          log.info( 'annex requests found' )
        except Exception, e:
          message = 'no annex requests found; quitting'
          log.debug( message )
          sys.exit( message )
        utf8_data = file_handler.read()
        data = utf8_data.encode( 'utf-8' )
        return data

    def copy_original_to_archives( self, date_stamp ):
        """ Copies original file to archives.
            Called by process_requests() """
        original_archive_file_path = '%s/REQ-ORIG_%s.dat' % ( self.PATH_TO_ARCHIVES_ORIGINALS_DIRECTORY, date_stamp )   # i.e. '/path/REQ-ORIG_2005-05-19T15/08/09.dat'
        try:
          shutil.copyfile( self.PATH_TO_SOURCE_FILE, original_archive_file_path )
          os.chmod( original_archive_file_path, 0640 )
          log.debug( 'source file copied to original archives' )
        except Exception, e:
          message = 'copy of original file from "%s" to "%s" unsuccessful; exception is: %s' % ( self.PATH_TO_SOURCE_FILE, original_archive_file_path, e )
          log.error( message )
          sys.exit( message )
        copy_check = utility_code.checkFileExistence( original_archive_file_path )
        if copy_check == 'exists':
          log.info( 'original file copied to: %s' % original_archive_file_path )
        else:
          message = 'copy of original file from "%s" to "%s" unsuccessful; exception is: %s' % ( self.PATH_TO_SOURCE_FILE, original_archive_file_path, copy_check )
          log.error( message )
          sys.exit( message )
        return

    def post_original_to_db( self, data, date_stamp ):
        """ Posts original file to annex-processor-viewer.
            Called by process_requests() """
        post_result = 'init'
        try:
            post_result = utility_code.postFileData( identifier=date_stamp, file_data=data, update_type='original_file' )
            log.info( 'original_file post_result, `%s`' % post_result )
        except Exception, e:
            log.error( 'original_file post_result exception is: %s' % e )
        if not post_result == 'success':
            log.debug( 'post_result not "success"; but continuing' )
        return

    def make_pageslips_list( self, data ):
        """ Returns list of pageslips, where each pageslip is a list of lines.
            Called by process_requests() """
        item_list_maker = utility_code.ItemListMaker()
        item_list = item_list_maker.make_item_list( data )
        log.info( 'item_list prepared' )
        return item_list

    def make_gaf_list( self, pageslips_list ):
        """ Converts list of pageslips into list of items for gfa software.
            TODO: call parser.process_all() here instead of individual elements.
            Called by process_requests() """
        new_item_list = []
        pageslip_count = 0
        for item in pageslips_list:
            try:
                parser = utility_code.Parser()
                record_number = utility_code.parseRecordNumber(item)
                book_barcode = parser.parse_bookbarcode( item )
                las_delivery_stop = utility_code.parseJosiahPickupAtCode(item)
                las_customer_code = parser.parse_josiah_location_code( item )
                patron_name = utility_code.parsePatronName(item)
                patron_barcode = utility_code.parsePatronBarcode(item)
                title = parser.parse_title( item )
                las_date = utility_code.prepareLasDate()
                note = parser.parse_note( item )
                full_line = '''"%s","%s","%s","%s","%s","%s","%s","%s","%s"''' % ( record_number, book_barcode, las_delivery_stop, las_customer_code, patron_name, patron_barcode, title, las_date, note )
                new_item_list.append( full_line )
                pageslip_count = pageslip_count + 1
                if pageslip_count % 10 == 0:
                    log.debug( '`%s` pageslips processed so far...' % pageslip_count )
            except Exception, e:
                subject = 'annex process pageslips problem'
                message = 'iterating through item_list; problem with item "%s"; exception is: %s' % ( item, unicode(repr(e)) )
                logger.error( message )
                m = Mailer( subject, message )
                m.send_email()
        log.info( '`%s` items parsed' % pageslip_count )
        log.debug( 'new_item_list, ```%s```' % pprint.pformat(new_item_list) )
        return new_item_list

    def post_parsed_to_db( self, gaf_list, date_stamp ):
        """ Posts parsed data to annex-processor-viewer.
            Called by process_requests() """
        unicode_string_data = ''
        count = 0
        for line in gaf_list:
            if count == 0:
                unicode_string_data = line
            else:
                unicode_string_data = unicode_string_data + '\n' + line
            count = count + 1
        unicode_string_data = unicode_string_data + '\n'   # the final newline is likely not necessary but unixy, and exists in old system
        post_result = 'init'
        try:
            post_result = utility_code.postFileData( identifier=date_stamp, file_data=unicode_string_data, update_type='parsed_file' )
            log.info( 'parsed_file post_result is: %s' % post_result )
        except Exception, e:
            log.error( 'parsed_file post_result exception is: %s' % unicode(repr(e)) )
        if not post_result == 'success':
            log.debug( 'post_result of parsed file not "success"; but continuing' )
        return unicode_string_data

    def save_parsed_to_archives( self, date_stamp, unicode_string_data ):
        try:
          parsed_file_name = 'REQ-PARSED_%s.dat' % date_stamp
          parsed_file_archive_path = '%s/%s' % ( self.PATH_TO_ARCHIVES_PARSED_DIRECTORY, parsed_file_name )
          f = open( parsed_file_archive_path, 'w' )
          f.write( unicode_string_data )
          f.close()
          copy_check = utility_code.checkFileExistence( parsed_file_archive_path )
          os.chmod( parsed_file_archive_path, 0640 )   # rw-/r--/---
          if copy_check == 'exists':
            utility_code.updateLog( message='- parsed file archived to: %s' % parsed_file_archive_path )
          else:
            message = '- write of parsed file to "%s" unsuccessful' % parsed_file_archive_path
            utility_code.updateLog( message=message, message_importance='high' )
            sys.exit( message )
        except Exception, e:
          message='- problem on save of parsed file; quitting; exception is: %s' % e
          utility_code.updateLog( message=message, message_importance='high' )
          sys.exit( message )

    ## end class Controller()


if __name__ == '__main__':
    c = Controller()
    c.process_requests()
    log.debug( 'complete' )
