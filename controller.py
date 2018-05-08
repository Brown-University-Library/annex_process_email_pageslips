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

    ## end class Controller()


if __name__ == '__main__':
    c = Controller()
    c.process_requests()
    log.debug( 'complete' )
