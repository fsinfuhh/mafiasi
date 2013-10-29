#!/usr/bin/env python

'''       parse output of gpg --fingerprint

This code borrows large parts of  the regular expressions from
gpg-key2ps written by Simon Richter, Thijs Kinkhorst and Christoph Berg.

Copyright (C) 2009 Justus Winter <justus.winter@informatik.uni-hamburg.de>

Licenced under the GNU General Public License, version 2 or later.
'''

import re

def reDict(parser, regexp, input, handler):
    match = regexp.match(input)
    if match:
        handler(parser, match)
        return True
    return False

def reReplace(parser, regexp, input, handler):
    match = regexp.match(input)
    if match:
        handler(parser, match, regexp, input)
        return True
    return False

class GPGFingerprintParser(object):
    getAlgorithm = {1: 'R', 2: 'r', 3: 's', 16: 'g', 20: 'G', 17: 'D'}
    displayAlgorithm = 'RrsgGD'

    def handlePub(self, match):
        if self.currentKey:
            self.handler(self.currentKey)
        self.currentKey = {'uids': [], 'sigs': []}
        self.currentKey.update(match.groupdict())
        self.currentKey['uids'].append(self.currentKey.pop('firstuid'))
        self.currentKey['length'] = int(self.currentKey['length'])
        self.currentKey['type_int'] = int(self.currentKey['type_int'])
        self.currentKey['type'] = self.getAlgorithm[self.currentKey['type_int']]

    def handleUid(self, match):
        self.currentKey['uids'].append('%s' % match.group('uid'))

    def handleSIG(self, match):
        self.currentKey['sigs'].append(match.group('id'))

    def handleFPR(self, match, regexp, input):
        bytes = []
        for b in match.groups():
            if len(b) == 2:
                bytes.append(int(b, 16))
            else:
                bytes.extend([int(b, 16) >> 8, int(b, 16) & 0xff])

        type = 0 if len(match.groups()) == 10 else 1
        replacement = (r'\1 \2 \3 \4 \5  \6 \7 \8 \9 \10',
                       r'\1 \2 \3 \4 \5 \6 \7 \8  \9 \10 \11 \12 \13 \14 \15 \16')[type]
        self.currentKey['fingerprint'] = regexp.sub(replacement, input)
        self.currentKey['fingerprint_raw'] = bytes

    handlers = dict(
        pub = (
            reDict,
            re.compile(r'''^pub:[^:]*:(?P<length>[^:]*):(?P<type_int>[0-9]*):.{8,8}(?P<id>.{8,8}):(?P<created>[^:]*):[^:]*:[^:]*:[^:]*:(?P<firstuid>[^:]*):[^:]*:[^:]*:.*$'''),
            handlePub),
        uid = (
            reDict,
            re.compile(r'''^uid:[^:r]*:[^:]*:[^:]*:[^:]*:[^:]*:[^:]*:[^:]*:[^:]*:(?P<uid>[^:]*):.*$'''),
            handleUid),
        fpr = (
            reReplace,
            (re.compile(r'''^.*(\w{4})(\w{4})(\w{4})(\w{4})(\w{4})(\w{4})(\w{4})(\w{4})(\w{4})(\w{4}).*$'''),
             re.compile(r'''^.*(\w{2})(\w{2})(\w{2})(\w{2})(\w{2})(\w{2})(\w{2})(\w{2})(\w{2})(\w{2})(\w{2})(\w{2})(\w{2})(\w{2})(\w{2})(\w{2}).*''')),
            handleFPR),
        sig = (
            reDict,
            re.compile(r'''^sig:[^:]*:[^:]*:(?P<type>[0-9]*):.{8,8}(?P<id>.{8,8}):(?P<created>[^:]*):[^:]*:[^:]*:[^:]*:(?P<uid>[^:]*):[^:]*:.*$'''),
            handleSIG),
    )

    def __init__(self, handler):
        self.currentKey = None
        self.handler = handler
        self.fragment = ''

    def parse(self, data):
        data = data + self.fragment
        self.fragment = ''
        lines = data.split('\n')
        if not data.endswith('\n'):
            self.fragment = lines.pop()
        for line in lines:
            for key, (method, regexp, handler) in self.handlers.items():
                if line.startswith(key):
                    if not isinstance(regexp, (tuple, list)):
                        regexp = (regexp, )
                    success = False
                    for rx in regexp:
                        if method(self, rx, line, handler):
                            success = True
                            break

                    if not success:
                        print '''couldn't handle line: %s''' % line
        if self.currentKey:
            self.handler(self.currentKey)

