'''       glue code for gpg

Copyright (C) 2009 Justus Winter <justus.winter@informatik.uni-hamburg.de>

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
'''

import subprocess
import logging; log = logging.getLogger(__name__)

class GPG(object):
    def __init__(self, homedir = None, args = None, gpg = 'gpg'):
        self.gpg = gpg.split()
        self.args = args or []
        self.homedir = homedir
        if homedir:
            self.args.extend(['--homedir', self.homedir])

        def doShortCut(command):
            self.__dict__[command.replace('-', '_')] = lambda *args, **kwargs: self.execute('--' + command.lower(), *args, **kwargs)
        for command in 'sign lsign sign-key lsign-key Import export fingerprint recv-keys send-keys refresh-keys list-keys list-sigs'.split():
            doShortCut(command)

    def _execute(self, *args):
        command = self.gpg + self.args + list(args)
        log.info('Executing %s' % ' '.join("'%s'" % arg for arg in command))
        handle = subprocess.Popen(command,
                                  stdin = subprocess.PIPE,
                                  stdout = subprocess.PIPE,
                                  stderr = subprocess.PIPE)
        return handle

    def execute(self, *args, **kwargs):
        input = kwargs.get('input', None)
        out, err = self._execute(*args).communicate(input)
        return out, err
