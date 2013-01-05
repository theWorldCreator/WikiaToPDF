#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import lxml.html
from lxml.html.clean import Cleaner
import urllib
import os
import shutil
from urlparse import urlparse

tmp_folder = 'tmp/'

base_url = "http://ru.fcknvermodes.wikia.com/wiki/"


def unique(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if x not in seen and not seen_add(x)]


def html2pdf(html, pdf):
    return os.system('wkhtmltopdf ' + html + ' ' + pdf)


def clean_all_but(tree, id_to_keep):
    # Clean all tags but with id_to_keep id
    # Also leave allowed_tags

    allowed_tags = ["script"]
    for child in tree:
        if not (len(child.cssselect('#' + id_to_keep)) > 0 or child.tag in allowed_tags):
            child.drop_tree()


def clean_controls(root):
    # Clean all control elements form Wikia page
    denied_classes = ['wikia-menu-button', 'comments',
                    'WikiaArticleCategories', 'editsection',
                    'printfooter']
    for cl in denied_classes:
        elements = root.cssselect('.' + cl)
        for el in elements:
            el.drop_tree()


def parent_in_tag(element, tag):
    # Find parent of element which is direct child of tag
    parent = element
    while parent.getparent().tag != tag:
        parent = element.getparent()
    return parent


def all_internal_links(url):
    # Get all intenal links from the page

    o = urlparse(url)
    base_loc = o.netloc
    page = urllib.urlopen(url)
    doc = lxml.html.document_fromstring(page.read())
    page.close()

    content = doc.cssselect('body')[0].getchildren()
    clean_all_but(content, 'WikiaPage')
    article = doc.cssselect('div.WikiaPageContentWrapper')[0].getchildren()
    clean_all_but(article, 'WikiaMainContent')

    clean_controls(doc)
    links_obj = doc.cssselect('a')
    links = []
    for obj in links_obj:
        curr_url = obj.get('href')
        o = urlparse(curr_url)
        if o.netloc == '':
            if curr_url[0] != '/':
                curr_url = '/' + curr_url
            curr_url = 'http://' + base_loc + curr_url
            o = urlparse(curr_url)
        if o.netloc == base_loc and o.fragment == '' and o.query == '' and ':' not in o.path:
            links.append(curr_url)
            # print curr_url
    return unique(links)

if os.path.exists(tmp_folder):
    shutil.rmtree(tmp_folder)
os.makedirs(tmp_folder)

url_list = all_internal_links(base_url)
print url_list
i = 1
cleaner = Cleaner(comments=True, page_structure=False, scripts=False)
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

os.system('pdfjoin ' + ' '.join(pdf_list) + ' --outfile output.pdf')
shutil.rmtree(tmp_folder)
