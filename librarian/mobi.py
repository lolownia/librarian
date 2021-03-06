# -*- coding: utf-8 -*-
#
# This file is part of Librarian, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from copy import deepcopy
import os
import subprocess
from tempfile import NamedTemporaryFile

from librarian import OutputFile
from librarian.cover import DefaultEbookCover
from librarian import get_resource


def transform(wldoc, verbose=False,
              sample=None, cover=None, flags=None):
    """ produces a MOBI file

    wldoc: a WLDocument
    sample=n: generate sample e-book (with at least n paragraphs)
    cover: a cover.Cover factory overriding default
    flags: less-advertising,
    """

    document = deepcopy(wldoc)
    del wldoc
    book_info = document.book_info

    # provide a cover by default
    if not cover:
        cover = DefaultEbookCover
    cover_file = NamedTemporaryFile(suffix='.png', delete=False)
    bound_cover = cover(book_info)
    bound_cover.save(cover_file)

    if bound_cover.uses_dc_cover:
        if document.book_info.cover_by:
            document.edoc.getroot().set('data-cover-by', document.book_info.cover_by)
        if document.book_info.cover_source:
            document.edoc.getroot().set('data-cover-source', document.book_info.cover_source)

    if not flags:
        flags = []
    flags = list(flags) + ['with-full-fonts']
    epub = document.as_epub(verbose=verbose, sample=sample, html_toc=True,
            flags=flags, style=get_resource('epub/style.css'))

    if verbose:
        kwargs = {}
    else:
        devnull = open("/dev/null", 'w')
        kwargs = {"stdout": devnull, "stderr": devnull}

    output_file = NamedTemporaryFile(prefix='librarian', suffix='.mobi', delete=False)
    output_file.close()
    subprocess.check_call(['ebook-convert', epub.get_filename(), output_file.name,
            '--no-inline-toc', '--mobi-file-type=both', '--subset-embedded-fonts', '--mobi-ignore-margins', '--cover=%s' % cover_file.name], **kwargs)
    os.unlink(cover_file.name)
    return OutputFile.from_filename(output_file.name)
