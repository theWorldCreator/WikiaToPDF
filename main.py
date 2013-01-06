#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import lxml.html
import urllib
import os
import shutil
from utils import crawler, clean_all_but, clean_controls, html2pdf, pdfjoin

tmp_folder = 'tmp/'

base_url = "http://pawnstarsthegame.wikia.com/"


if os.path.exists(tmp_folder):
    shutil.rmtree(tmp_folder)
os.makedirs(tmp_folder)

url_list = crawler(base_url)
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
