def to_unicode(str_or_unicode, encoding='utf8'):
    if type(str_or_unicode) == unicode:
        return str_or_unicode
    return unicode(str_or_unicode, encoding, errors='ignore')
