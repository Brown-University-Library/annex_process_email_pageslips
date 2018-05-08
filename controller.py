# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime, logging, os, shutil, smtplib, string, sys
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
        """ Calls steps.
            Called by ```if __name__ == '__main__':``` """
        log.debug( 'starting process_requests()' )
        self.check_paths()
        file_handler = self.file_check()
        if file_handler():
            date_stamp = utility_code.prepareDateTimeStamp( datetime.datetime.now() )
            self.copy_original_to_archives()
            self.post_original_to_db()
            pageslips_list = self.make_pageslips_list()
            gaf_list = self.make_gaf_list( pageslips_list )
            self.post_parsed_to_db( gaf_list )
            self.save_parsed_to_archives( gaf_list )
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
        try:
          file_handler = open( self.PATH_TO_SOURCE_FILE )
          log.info( 'annex requests found' )
          return file_handler
        except Exception, e:
          message = 'no annex requests found; quitting'
          log.debug( message )
          sys.exit( message )



    ## end class Controller()


if __name__ == '__main__':
    c = Controller()
    c.process_requests()
    log.debug( 'complete' )
