# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import datetime, json, logging, os, pprint, smtplib, urllib, urllib2
from email.Header import Header
from email.mime.text import MIMEText

LOG_PATH = os.environ['EML_PGSLP__LOG_PATH']
LOG_LEVEL = os.environ['EML_PGSLP__LOG_LEVEL']  # 'DEBUG' or 'INFO'
log_level = { 'DEBUG': logging.DEBUG, 'INFO': logging.INFO }
logging.basicConfig(
    filename=LOG_PATH, level=log_level[LOG_LEVEL],
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S'
    )
log = logging.getLogger(__name__)
log.debug( 'START' )

from process_email_pageslips.lib.parser import Parser


class ItemListMaker( object ):
    """ Breaks pageslip file into list of requests, where each request is a list of lines. """

    def __init__( self ):
        self.items = []
        self.item = []
        self.last_line = ''
        self.two_lines_past = ''

    def make_item_list( self, text ):
        """ Turns utf8-text into list of requests, where each request is a list of lines. """
        unicode_lines = self.make_lines( text )
        for line in unicode_lines:
              if self.check_start( line ) == True:
                    self.items.append( self.item )  # copies current item to items
                    self.item = []  # clear item
              self.conditionally_append_line_to_item( line )
              self.two_lines_past = self.last_line
              self.last_line = line
        self.items.append( self.item )  # adds last item
        self.clean_items()
        return self.items

    def make_lines( self, text ):
        """ Turns text into lines.
            Called by make_item_list() """
        if type( text ) == str:
            text = text.decode( 'utf-8' )
        lines = text.split( '\n' )
        return lines

    def check_start( self, line ):
        """ Determines if line is beginning of an item.
            Called by make_item_list() """
        line = line.strip()
        return_val = False
        if line in ['Brown University', 'Brown University Library' ]:
                if ('AUTHOR' not in line) and ('AUTHOR' not in self.last_line):
                        if ('21236' not in self.two_lines_past and '2 1236' not in self.two_lines_past):
                                return_val = True
        elif line.strip()[0:3] in [ 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun' ] and len(self.item) < 1:
                return_val = True
        elif len(self.item) > 1 and self.item[-1].strip()[0:4] in [ '38:1', '38:2', '38:3', '38:4', '38:5', '38:6', '38:7', '38:8', '38:9', '38:0' ]:
                return_val = True
        return return_val

    def conditionally_append_line_to_item( self, line ):
        """ Appends line to item if it's not a blank start to a new item.
            Called by make_item_list() """
        if len(self.item) == 0 and line.strip() == '':
              pass
        elif 'ANNEX PAGE REQUEST' in line:
            pass
        else:
              # log.debug( 'conditionally appending line, ```%s```' % line )
              self.item.append( line )  # adds line to existing or new item
        return

    def clean_items( self ):
        """ Removes empty items and removes empty trailing lines from each item.
            Called by make_item_list() """
        new_items = []
        for item in self.items:
              if len(item) > 0:
                    item = self.remove_empty_lines( item )
                    new_items.append( item )
        self.items = new_items
        log.debug( 'self.items, ```%s```' % pprint.pformat(self.items) )
        return

    def remove_empty_lines( self, item ):
        """ Removes empty lines from end of page-slip.
            Called by clean_items() """
        item.reverse()  # switches line order for easy looping
        new_item = []
        check_flag = True
        for line in item:
          if line.strip() == '' and check_flag == True:  # doesn't copy empty line
                pass
          else:  # otherwise, copies and stops checking, since the trailing empty lines have been removed
                check_flag = False
                new_item.append( line )
        new_item.reverse()  # switches back to proper line order
        return new_item

    ## end class ItemListMaker()
