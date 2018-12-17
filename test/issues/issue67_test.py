"""
intervaltree: A mutable, self-balancing interval tree for Python 2 and 3.
Queries may be by point, by range overlap, or by range envelopment.

Test module: IntervalTree, insertion of a sequence of intervals caused
invariant violation
Submitted as issue #67 (Inserting intervals in specific sequence results in
invalid tree) by suola

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
from __future__ import absolute_import
from intervaltree import IntervalTree
import pytest

def test_interval_insersion_67():
    intervals = (
        (3657433088, 3665821696),
        (2415132672, 2415394816),
        (201326592, 268435456),
        (163868672, 163870720),
        (3301965824, 3303014400),
        (4026531840, 4294967296),
        (3579899904, 3579904000),
        (3439329280, 3443523584),
        (3431201536, 3431201664),
        (3589144576, 3589275648),
        (2531000320, 2531033088),
        (4187287552, 4187291648),
        (3561766912, 3561783296),
        (3046182912, 3046187008),
        (3506438144, 3506962432),
        (3724953872, 3724953888),
        (3518234624, 3518496768),
        (3840335872, 3840344064),
        (3492279181, 3492279182),
        (3447717888, 3456106496),
        (3589390336, 3589398528),
        (3486372962, 3486372963),
        (3456106496, 3472883712),
        (3508595496, 3508595498),
        (3511853376, 3511853440),
        (3452226160, 3452226168),
        (3544510720, 3544510736),
        (3525894144, 3525902336),
        (3524137920, 3524137984),
        (3508853334, 3508853335),
        (3467337728, 3467341824),
        (3463212256, 3463212260),
        (3446643456, 3446643712),
        (3473834176, 3473834240),
        (3487039488, 3487105024),
        (3444686112, 3444686144),
        (3459268608, 3459276800),
        (3483369472, 3485466624),
    )
    tree = IntervalTree()
    for interval in intervals:
        tree.addi(*interval)
    tree.verify()

