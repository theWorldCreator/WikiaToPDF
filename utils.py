#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import lxml.html
import urllib
import os
from urlparse import urlparse, urljoin


def unique(seq):
    # Remove all duplicates from list.

    seen = set()
    seen_add = seen.add
    return [x for x in seq if x not in seen and not seen_add(x)]


def html2pdf(html, pdf):
    # Call comand line utility to render pdf from html file.

    return os.system('wkhtmltopdf ' + html + ' ' + pdf)


def pdfjoin(pdf_list):
    # Call comand line utility to join list of pdf files.

    return os.system('pdfjoin ' + ' '.join(pdf_list) + ' --outfile output.pdf')


def clean_all_but(root, id_to_keep):
    # Clean all tags but with id_to_keep id
    # but leave allowed_tags.

    allowed_tags = ["script"]
    for child in root:
        if not (len(child.cssselect('#' + id_to_keep)) > 0 or
                child.tag in allowed_tags):
            child.drop_tree()


def clean_controls(root):
    # Clean all control elements form Wikia page tree.

    denied_classes = ['wikia-menu-button', 'comments',
                    'WikiaArticleCategories', 'editsection',
                    'printfooter']
    for cl in denied_classes:
        elements = root.cssselect('.' + cl)
        for el in elements:
            el.drop_tree()


def all_internal_links(base_url):
    # Get all intenal links from the Wikia page.

    url_struct = urlparse(base_url)
    base_loc = url_struct.netloc
    page = urllib.urlopen(base_url)
    doc = lxml.html.document_fromstring(page.read())
    page.close()

    # Remove Wikia irrelevant information (e.g. footer).
    content = doc.cssselect('body')[0].getchildren()
    clean_all_but(content, 'WikiaPage')
    article = doc.cssselect('div.WikiaPageContentWrapper')[0].getchildren()
    clean_all_but(article, 'WikiaMainContent')
    clean_controls(doc)

    links_obj = doc.cssselect('a')
    links = []
    for obj in links_obj:
        curr_url = urljoin(base_url, obj.get('href'))
        url_struct = urlparse(curr_url)
        member_link = ':' in url_struct.path
        control_link = url_struct.query.strip() != ''
        anchor_link = url_struct.fragment != ''
        internal_link = url_struct.netloc == base_loc
        if internal_link:
            if not member_link and not control_link and not anchor_link:
                links.append(curr_url)
    return unique(links)


def crawler(base_url, recursion_level=1):
    # Recursively get all internal links starting from base_url Wikia page.

    links = [base_url]
    to_parse_curr = [base_url]
    to_parse_next = []
    level = 1
    while level <= recursion_level:
        for url in to_parse_curr:
            new_links = all_internal_links(url)
            to_parse_next = to_parse_next + new_links
            links = links + new_links
        to_parse_curr = to_parse_next
        to_parse_next = []
        level += 1
    return links
