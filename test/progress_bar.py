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
from functools import partial
import sys

try:
    xrange
except NameError:
    xrange = range


def write(s):
    sys.stdout.write(s)
    sys.stdout.flush()


class ProgressBar(object):
    class Formats(object):
        basic = '[%b] %p%%'
        fraction = '|%b| %i/%t'
        timer = basic + ' %es'
        predictive = '(%b) %p%% %es elapsed, ETA %Es'
        speed = '[%b] %v/s %p%%'
        advanced = '%r/%t remaining %p%% [%b] ETA %Es @ %v/s %es elapsed'
        items_remaining = '{%b} %r/%t remaining'
        stats_only = '%p%%, %r/%t remaining, %i done %_ ETA %Es @ %v/s %es elapsed'

    def __init__(self,
                 total,
                 width=80,
                 fmt='%i/%t %p%% %b %es',
                 time_throttle=0.05,
                 custom_outputters=None):
        # cache the values calculated during the self.i-th iteration
        self.i = 0
        self.total = total

        # throttling
        self.time_throttle = time_throttle
        self.should_output = self.should_output_first

        # time
        # clock starts ticking on first update call
        self.start_time = None
        self.last_output_time = None

        # output string
        self.width = width
        self.last_output_width = 0
        self.outputters = {
            't': str(self.total),
            'i': lambda: str(self.i),
            'b': self.make_progress_bar,
            '_': self.make_expanding_space,
            'p': lambda: self.float_formatter(100 * self.fraction),
            'r': lambda: str(self.remaining),
            'e': lambda: self.float_formatter(self.elapsed),
            'E': lambda: self.float_formatter(self.eta),
            'v': lambda: self.float_formatter(self.rate),
        }
        if custom_outputters:
            bound_outputters = {}
            for k, v in custom_outputters.items():
                if not callable(v):
                    # test concatenation early, let it raise if it fails
                    '' + v
                else:
                    v = partial(v, self)
                bound_outputters[k] = v
            self.outputters.update(bound_outputters)

        # stuff that fills the rest of the space
        self.resized = [
            self.make_progress_bar,
            self.make_expanding_space,
        ]
        self.tokens = []
        self.format = fmt
        self.parse_format(fmt)

    def __call__(self, increment=1):
        """
        Update the ProgressBar state.
        :param increment: how much to increase self.i
        """
        self.i += increment
        if self.should_output():
            self.last_output_time = time()
            self.write()

    def should_output_first(self):
        """
        Initializes throttle control
        :return: bool
        """
        self.last_output_time = self.start_time = time()
        self.should_output = self.should_output_middle
        return True

    def should_output_middle(self):
        """
        Implements throttle control
        :return: bool
        """
        systems_go = (
            time() - self.last_output_time > self.time_throttle or
            self.i == self.total
        )
        return systems_go

    def parse_format(self, fmt):
        tokens = self.tokenize(fmt)
        self.tokens = self.join_tokens(tokens)

    def tokenize(self, fmt):
        """
        Splits format string into tokens. Used by parse_format.
        :returns: list of characters and outputter functions
        :rtype: list of (str or callable)
        """
        output = []
        hot_char = '%'
        in_code = []
        for c in fmt:
            if not in_code:
                if c == hot_char:
                    in_code.append(c)
                else:
                    output.append(c)
                continue
            #else:  in_code:
            if c == hot_char:
                output.append(c)
                in_code = []
                continue
            if c in self.outputters:
                func_or_str = self.outputters[c]
                output.append(func_or_str)
                in_code = []
                continue

            output.append(c)
            in_code = []

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
        tokens = self.make_output_string_static(self.tokens)
        tokens = self.make_output_string_resized(tokens)
        output = ''.join(tokens)
        return output

    def make_output_string_static(self, tokens):
        output = []
        for token in tokens:
            if callable(token) and token not in self.resized:
                generated = token()
                output.append(generated)
            else:
                output.append(token)
        output = self.join_tokens(output)
        return output

    def make_output_string_resized(self, tokens):
        output = []
        static_size = sum(len(s) for s in tokens if hasattr(s, '__len__'))
        remaining_width = self.width - static_size
        for token in tokens:
            if callable(token):
                token = token(remaining_width)
            output.append(token)
        output = self.join_tokens(output)
        return output

    def write(self):
        output = self.make_output_string()
        underrun = self.last_output_width - len(output)
        self.last_output_width = len(output.rstrip())
        output += underrun*' '  # completely erase last line with spaces

        write('\r' + output)
        if self.i >= self.total:
            print()

    def make_progress_bar(self, size):
        frac = self.i / self.total
        num_segs = int(frac * size)

        output = ''.join([
            num_segs * '=',
            (size - num_segs) * ' ',
        ])
        return output

    def make_expanding_space(self, size):
        return size*' '

    @staticmethod
    def float_formatter(f):
        if f > 10:
            return str(int(f))
        if f > 1:
            return "%0.1f" % f
        return "%0.2f" % f

    @property
    def fraction(self):
        return self.i / self.total

    @property
    def elapsed(self):
        return time() - self.start_time

    @property
    def rate(self):
        if not self.elapsed:
            return 0
        return self.i / self.elapsed

    @property
    def remaining(self):
        return self.total - self.i

    @property
    def eta(self):
        if not self.rate:
            return 1
        return self.remaining / self.rate

    def __str__(self):
        return self.make_output_string()


def _slow_test():
    from time import sleep
    total = 10
    pbar = ProgressBar(total)
    for i in xrange(total):
        pbar()
        sleep(0.5)


def _fast_test():
    total = 5 * 10**7
    pbar = ProgressBar(
        total,
        fmt=ProgressBar.Formats.stats_only,
    )
    for i in xrange(total):
        pbar()


def _profile():
    import cProfile
    cProfile.run('_fast_test()', sort='cumulative')

if __name__ == "__main__":
    # _slow_test()
    _profile()
