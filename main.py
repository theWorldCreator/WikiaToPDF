#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import lxml.html
from lxml.html.clean import Cleaner
import urllib
import os
import shutil

tmp_folder = 'tmp/'

base_url = "http://ru.fcknvermodes.wikia.com/wiki/%D0%A2%D0%B5%D0%BE%D1%80%D0%B8%D1%8F_"
url_list = []
for k in range(1, 2):
    url_list.append(base_url + str(k))


def html2pdf(html, pdf):
    print 'wkhtmltopdf ' + html + ' ' + pdf
    return os.system('wkhtmltopdf ' + html + ' ' + pdf)

if os.path.exists(tmp_folder):
    shutil.rmtree(tmp_folder)
os.makedirs(tmp_folder)

i = 1
cleaner = Cleaner(scripts=False)
pdf_list = []
for url in url_list:
    print url
    page = urllib.urlopen(url)
    doc = lxml.html.document_fromstring(page.read())
    content = doc.xpath('/html/body/')
    for child in content:
        print child.tag
        if child.get('id') != 'WikiaPage':
            child.drop_tree()
    article = doc.cssselect('#WikiaPage')
    for child in article:
        if child.get('id') != 'WikiaMainContent':
            child.drop_tree()
    f = open('test.html', 'a')
    f.write(cleaner.clean_html(lxml.html.tostring(doc)))
    # article = doc.cssselect('.mw-headline')
    # for curr in article:
    #     html_filename = tmp_folder + str(i) + '.html'
    #     pdf_filename = tmp_folder + str(i) + '.pdf'
    #     f = open(html_filename, 'a')
    #     f.write('<meta http-equiv="Content-Type" content="text/html; charset=utf-8">')
    #     header = cleaner.clean_html(lxml.html.tostring(curr))
    #     f.write('<h2>' + header + '</h2>')

    #     curr = curr.getparent().getnext()
    #     while curr != None and curr.tag != 'h2' and (len(curr.cssselect('.mw-redirect')) == 0 or curr.cssselect('.mw-redirect')[0].text_content() != u'Предыдущий билет'):
    #         try:
    #             html = cleaner.clean_html(lxml.html.tostring(curr))
    #         except:
    #             pass
    #         f.write(html)
    #         curr = curr.getnext()
    #     f.close()

    #     html2pdf(html_filename, pdf_filename)
    #     pdf_list.append(pdf_filename)
    #     i = i + 1

# os.system('pdfjoin ' + ' '.join(pdf_list) + ' --outfile output.pdf')
# shutil.rmtree(tmp_folder)
