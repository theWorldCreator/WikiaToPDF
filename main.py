#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import lxml.html
import urllib
import os
import shutil
import getopt
from sys import exit, argv
from utils import crawler, clean_all_but, clean_controls, html2pdf, pdfjoin

tmp_folder = "tmp/"


def usage():
    print """
NAME
       wikia_to_pdf.py - compile given Wikia page to pdf file

SYNOPSIS
       wikia_to_pdf.py -u url_to_parse [options]

DESCRIPTION
       Compile given Wikia page to pdf file. The options below may be used
       to select whether to use crawler (it will add to pdf not only  base
       page, but all pages that linked by this) and it's recursion deph.

       -u, --url
              base page url

       -c, --crawler
              whether to use crawler [false by default]

       -r, --recursion-deph
              recursion deph [1 by default]

       -h, --help
              display this help and exit
"""

options = "u:cr:h"
long_options = ["url", "crawler", "recursion-deph=", "help", "url="]
try:
    optlist, args = getopt.getopt(argv[1:], options, long_options)
except getopt.GetoptError as err:
    # Print help information and exit.
    print str(err)
    usage()
    exit(2)

# Default options
use_crawler = False
recursion_deph = 1
base_url = None
for o, a in optlist:
    if o in ("-u", "url"):
        base_url = a
    elif o in ("-c", "--crawler"):
        use_crawler = True
    elif o in ("-r", "recursion-deph"):
        recursion_deph = int(a)
    elif o in ("-h", "--help"):
        usage()
        exit()
    else:
        usage()
        exit()
if base_url is None:
    print "You must provide url to parse from"
    usage()
    exit(2)

if not os.path.exists(tmp_folder):
    os.makedirs(tmp_folder)

if use_crawler:
    url_list = crawler(base_url, recursion_deph)
else:
    url_list = [base_url]

i = 1
pdf_list = []
for url in url_list:
    page = urllib.urlopen(url)
    doc = lxml.html.document_fromstring(page.read())
    page.close()
    html_filename = tmp_folder + str(i) + '.html'
    pdf_filename = tmp_folder + str(i) + '.pdf'
    content = doc.cssselect('body')[0].getchildren()
    clean_all_but(content, 'WikiaPage')
    # article = doc.cssselect('div.WikiaPageContentWrapper')[0].getchildren()
    # clean_all_but(article, 'WikiaMainContent')

    clean_controls(doc)

    f = open(html_filename, 'w')
    f.write(lxml.html.tostring(doc))
    f.close()

    html2pdf(html_filename, pdf_filename)
    pdf_list.append(pdf_filename)
    i = i + 1

pdfjoin(pdf_list)
shutil.rmtree(tmp_folder)
