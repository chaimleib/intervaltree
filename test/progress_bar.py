"""
intervaltree: A mutable, self-balancing interval tree for Python 2 and 3.
Queries may be by point, by range overlap, or by range envelopment.

Test module: progress bar

Copyright 2013-2018 Chaim Leib Halbert

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
    """
    See how far a process has gone.

    Example:
        from progress_bar import ProgressBar

        big_list = ...

        pbar = ProgressBar(len(big_list))
        for item in big_list:
            process_item(item)
            pbar()

    You can increment by different amounts by calling
    `pbar(increment)` instead of just `pbar()`.

    ## Creating a `ProgressBar`
    You can customize the format for the output using arguments to
    the initializer.

    `width`:
        how many characters wide
    `fmt`:
        a format string. Choose from ProgressBar.Formats.* or create
        your own. Available predesigned formats:

            class Formats(object):
                basic = '[%=] %p%%'
                fraction = '|%=| %i/%t'
                timer = basic + ' %es'
                predictive = '(%=) %p%% %es elapsed, ETA %Es'
                speed = '[%=] %R/s %p%%'
                advanced = '%r/%t remaining [%=] %p%% ETA %Es @ %R/s %es elapsed'
                items_remaining = '{%=} %r/%t remaining'
                stats_only = '%p%% %r/%t remaining %_ ETA %Es @ %R/s %es elapsed'

    `time_throttle`:
        minimum time in seconds before updating the display
    `custom_outputter`:
        a dict mapping character strings to strings or callables that
        generate strings. The callable will be invoked with the
        `ProgressBar` instance as its first argument. Example:

            def kbytes_copied(pbar):
                kbytes = pbar.i / 1024
                return pbar.float_formatter(kbytes) + 'KB'

            pbar = ProgressBar(max_val,
                fmt='%p%% %[%=] %k copied',    # '%k' turns into kbytes_copied()
                custom_outputters={'k': kbytes_copied})

    `custom_expanding_outputters`:
        Like `custom_outputter`, but for output that expands to fill
        available space. These are invoked with two arguments: the
        `ProgressBar` instance, and the calculated remaining width
        for your outputter. Example:

            def hash_progressbar(pbar, size):
                segs = pbar.fraction * size
                return segs*'#' + (size-segs)*' '

            pbar = ProgressBar(max_val,
                fmt='%p%% [%#]',    # '%#' turns into my hash_progressbar
                custom_expanding_outputters={'#': hash_progressbar})


    ## Predefined outputters
    All these are preceded with a percent symbol in the `fmt` string
    provided when creating a `ProgressBar`.

    `t`:
        Maximum progress count.
    `i`:
        Current count.
    `=`:
        Progress bar, without endcaps. Expands to fill available width.
    `_` (underscore):
        Expanding space.
    `p`:
        Percent progress, without percent symbol. To add that, use '%%'
    `r`:
        Count remaining.
    `e`:
        Time elapsed. Counted from first `pbar()` call, where `pbar` is
        your `ProgressBar` instance.
    `E`:
        ETA (estimated time of arrival). Based on current rate, linearly
        extrapolate to predict how much time in seconds is left.
    `R`:
        Count rate. In units of counts per second.
    `%`:
        A literal percent symbol.

    ## Fields available for your outputter
    When writing custom outputters, it is sometimes useful to access the
    internal fields of the `ProgressBar` instance. The following are
    available:

    `i`:
        Current count.
    `total`:
        Maximum progress count.
    `start_time`:
        Time of first display update. (from `time.time()`)
    `last_output_time`:
        Time of most recent display update. (from `time.time()`)
    `time_throttle`:
        Minimum time between display updates.
    `width`:
        Total available width for entire `ProgressBar` line.
    `last_output_width`:
        Width of last output, minus trailing spaces on the right.
    `rate`:
        How many counts per second.
    `fraction`:
        A float of what amount is done. A value between 0 and 1.
    `remaining:
        How many counts left.
    `elapsed`:
        Total time elapsed since first count.
    `eta`:
        ETA (estimated time of arrival) of final count, based on
        current count rate.
    """
    class Formats(object):
        basic = '[%=] %p%%'
        fraction = '|%=| %i/%t'
        timer = basic + ' %es'
        predictive = '(%=) %p%% %es elapsed, ETA %Es'
        speed = '[%=] %R/s %p%%'
        advanced = '%r/%t remaining [%=] %p%% ETA %Es @ %R/s %es elapsed'
        items_remaining = '{%=} %r/%t remaining'
        stats_only = '%p%% %r/%t remaining %_ ETA %Es @ %R/s %es elapsed'

    def __init__(self,
                 total,
                 width=80,
                 fmt=Formats.advanced,
                 time_throttle=0.05,
                 custom_outputters=None,
                 custom_expanding_outputters=None
                 ):
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
        self.format = fmt
        self.width = width
        self.last_output_width = 0
        self.outputters = {
            't': str(self.total),
            'i': lambda: str(self.i),
            '=': self.make_progress_bar,
            '_': self.make_expanding_space,
            'p': lambda: self.float_formatter(100 * self.fraction),
            'r': lambda: str(self.remaining),
            'e': lambda: self.float_formatter(self.elapsed),
            'E': lambda: self.float_formatter(self.eta),
            'R': lambda: self.float_formatter(self.rate),
        }
        if custom_outputters or custom_expanding_outputters:
            custom_outputters = custom_outputters or {}
            if custom_expanding_outputters:
                custom_outputters.update(custom_expanding_outputters)
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
        self.expanding_outputters = [
            self.make_progress_bar,
            self.make_expanding_space,
        ]
        if custom_expanding_outputters:
            self.expanding_outputters.extend(custom_expanding_outputters.items())
        self.tokens = []
        self.update_format(fmt)

    def __call__(self, increment=1):
        """
        Update the ProgressBar state.
        :param increment: how much to increase self.i
        """
        self.i += increment
        if self.should_output():
            self.last_output_time = time()
            self.write()

    def update_format(self, fmt):
        self.format = fmt
        self.parse_format(fmt)

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
            if callable(token) and token not in self.expanding_outputters:
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
