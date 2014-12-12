"""
intervaltree: A mutable, self-balancing interval tree for Python 2 and 3.
Queries may be by point, by range overlap, or by range envelopment.

Test module: progress bar

Copyright 2013-2014 Chaim-Leib Halbert

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from __future__ import print_function
from __future__ import division
from time import time

import sys
from pprint import pprint, pformat

try:
    xrange
except NameError:
    xrange = range

def write(s):
    sys.stdout.write(s)
    sys.stdout.flush()


class ProgressBar(object):
    def __init__(self, total, width=80, format=r'\i/\t \p% \b \ss', time_throttle=0.05, dynamic_throttle=True):
        self.i = 0
        self.total = total

        # throttling
        self.enamble_dynamic_throttle = dynamic_throttle  # TODO: dynamic rate-based throttle
        self.time_throttle = time_throttle

        # time
        # clock starts ticking on first update call
        self.start_time = None
        self.now = None  # set later. make sure all numbers match, and for caching
        self.last_output_time = None

        # output string
        self.width = width
        self.outputters = {
            't': str(self.total),
            'i': lambda: str(self.i),
            'p': lambda: str(int(100 * self.i / self.total)),
            's': lambda: str(int(time() - self.start_time)),
            'b': self.make_progress_bar,
            'e': lambda: self.make_eta,
        }
        # stuff that fills the rest of the space
        self.resized = set([self.make_progress_bar])
        self.tokens = []
        self.format = format
        self.parse_format(format)

    def __call__(self, increment=1):
        should_output = False

        now = time()
        if not self.start_time:  # initialize clocks
            should_output = True
            self.last_output_time = self.start_time = now
        self.i += increment

        should_output |= now - self.last_output_time > self.time_throttle
        should_output |= self.i == self.total
        if should_output:
            self.last_output_time = now
            self.write()

    def parse_format(self, format):
        tokens = self.tokenize(format)
        self.tokens = self.join_tokens(tokens)

    def tokenize(self, format):
        """
        Splits format string into tokens. Used by parse_format.
        :returns: list of characters and outputter functions
        :rtype: list of (str or callable)
        """
        output = []
        last = None
        for c in format:
            if last != '\\':
                output.append(c)
                last = c
                continue
            #else:  last == '\\':
            if c not in self.outputters:
                output.append(c)
                last = c
                continue
            func = self.outputters[c]
            output.pop()  # discard the \
            output.append(func)
            last = func
        return output

    @staticmethod
    def join_tokens(tokens):
        """
        Join sequential strings among the tokens.
        :param tokens: list of (str or callable)
        :return: list of (str or callable)
        """
        output = []
        raw = []
        for s in tokens:
            if callable(s):
                if raw:
                    raw = ''.join(raw)
                    output.append(raw)
                    raw = []
                output.append(s)
                continue
            raw.append(s)
        if raw:
            raw = ''.join(raw)
            output.append(raw)
        return output

    def make_output_string(self):
        output = self.make_output_string_static(self.tokens)
        output = self.make_output_string_resized(output)
        output = ''.join(output)
        return output

    def make_output_string_static(self, tokens):
        output = []
        for token in self.tokens:
            if callable(token) and token not in self.resized:
                generated = token()
                output.append(generated)
            else:
                output.append(token)
        output = self.join_tokens(output)
        return output

    def make_output_string_resized(self, tokens):
        output = []
        size = sum(len(s) for s in tokens if hasattr(s, '__len__'))
        size = self.width - size #+ 1  # +1 is for the \r
        for token in tokens:
            if callable(token):
                token = token(size)
            output.append(token)
        output = self.join_tokens(output)
        return output

    def write(self):
        output = self.make_output_string()
        write('\r' + output)
        if self.i >= self.total:
            print()

    def make_progress_bar(self, size):
        size -= 2
        frac = self.i / self.total
        num_segs = int(frac * size)

        output = ''.join([
            '[',
            num_segs * '=',
            (size - num_segs) * ' ',
            ']'
        ])
        return output

    def make_eta(self):
        return str(int(self.eta))

    @property
    def fraction(self):
        return self.i / self.total

    @property
    def elapsed(self, now):
        return self.now - self.start_time

    @property
    def int_elapsed(self):
        return int(self.elapsed)

    @property
    def rate(self):
        return self.i / self.elapsed

    @property
    def eta(self):
        remaining_fraction = 1 - self.fraction
        return remaining_fraction / self.rate

    def __str__(self):
        d = {
            'i': self.i,
            'start_time': self.start_time,
            'last_output_time': self.last_output_time,
            'format': self.format,
            'tokens': self.tokens,
        }
        return pformat(d)


def _slow_test():
    from time import sleep
    total = 10
    pbar = ProgressBar(total)
    for i in xrange(total):
        pbar()
        sleep(0.5)


def _fast_test():
    from time import sleep
    total = 5 * 10**4
    pbar = ProgressBar(total)
    for i in xrange(total):
        pbar()
        sleep(0.0001)


if __name__ == "__main__":
    _slow_test()
    _fast_test()
