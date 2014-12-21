[![Build status badge][]][build status]

intervaltree
============

A mutable, self-balancing interval tree for Python 2 and 3. Queries may be by point, by range overlap, or by range envelopment.

This library was designed to allow tagging text and time intervals, where the intervals include the lower bound but not the upper bound.

Installing
----------

```sh
pip install intervaltree
```

Features
--------

* Supports Python 2.6+ and Python 3.2+
* Initialize blank or from an iterable of `Intervals` in O(n * log n).
* Insertions

    * `tree[begin:end] = data`
    * `tree.add(interval)`
    * `tree.addi(begin, end, data)`
    * `tree.extend(list_of_interval_objs)`

* Deletions

    * `tree.remove(interval)`             (raises `ValueError` if not present)
    * `tree.discard(interval)`            (quiet if not present)
    * `tree.removei(begin, end, data)`    (short for `tree.remove(Interval(begin, end, data))`)
    * `tree.discardi(begin, end, data)`   (short for `tree.discard(Interval(begin, end, data))`)
    * `tree.remove_overlap(point)`
    * `tree.remove_overlap(begin, end)`   (removes all overlapping the range)
    * `tree.remove_envelop(begin, end)`   (removes all enveloped in the range)

* Overlap queries:

    * `tree[point]`
    * `tree[begin, end]`
    * `tree.search(point)`
    * `tree.search(begin, end)`

* Envelop queries:

    * `tree.search(begin, end, strict=True)`

* Membership queries:

    * `interval_obj in tree`              (this is fastest, O(1))
    * `tree.containsi(begin, end, data)`
    * `tree.overlaps(point)`
    * `tree.overlaps(begin, end)`

* Iterable:

    * `for interval_obj in tree:`
    * `tree.items()`

* Sizing:

    * `len(tree)`
    * `tree.is_empty()`
    * `not tree`
    * `tree.begin()`          (the `begin` coordinate of the leftmost interval)
    * `tree.end()`            (the `end` coordinate of the rightmost interval)

* Restructuring

    * `split_overlaps()`

* Copy- and typecast-able:

    * `IntervalTree(tree)`    (`Interval` objects are same as those in tree)
    * `tree.copy()`           (`Interval` objects are shallow copies of those in tree)
    * `set(tree)`             (can later be fed into `IntervalTree()`)
    * `list(tree)`            (ditto)

* Equal-able
* Pickle-friendly
* Automatic AVL balancing

Examples
--------

* Getting started

    ``` python
    >>> from intervaltree import Interval, IntervalTree
    >>> t = IntervalTree()
    >>> t
    IntervalTree()
    
    ```

* Adding intervals - any object works!

    ``` python
    >>> t[1:2] = "1-2"
    >>> t[4:7] = (4, 7)
    >>> t[5:9] = {5: 9}
    
    ```

* Query by point

    ``` python
    >>> sorted(t[6])
    [Interval(4, 7, (4, 7)), Interval(5, 9, {5: 9})]
    >>> sorted(t[6])[0]
    Interval(4, 7, (4, 7))
    
    ```

* Query by range

    Note that ranges are inclusive of the lower limit, but non-inclusive of the upper limit. So:

    ``` python
    >>> sorted(t[2:4])
    []
    
    ```

    But:

    ``` python
    >>> sorted(t[1:5])
    [Interval(1, 2, '1-2'), Interval(4, 7, (4, 7))]
    
    ```

* Accessing an `Interval` object

    ``` python
    >>> iv = Interval(4, 7, (4, 7))
    >>> iv.begin
    4
    >>> iv.end
    7
    >>> iv.data
    (4, 7)
    
    >>> begin, end, data = iv
    >>> begin
    4
    >>> end
    7
    >>> data
    (4, 7)
    
    ```

* Constructing from lists of `Interval`s

    We could have made a similar tree this way:

    ``` python
    >>> ivs = [(1, 2), (4, 7), (5, 9)]
    >>> t = IntervalTree(
    ...    Interval(begin, end, "%d-%d" % (begin, end)) for begin, end in ivs
    ... )
    
    ```

    Or, if we don't need the data fields:

    ``` python
    >>> t2 = IntervalTree(Interval(*iv) for iv in ivs)
    
    ```

* Removing intervals
    
    ``` python
    >>> t.remove( Interval(1, 2, "1-2") )
    >>> sorted(t)
    [Interval(4, 7, '4-7'), Interval(5, 9, '5-9')]

    >>> t.remove( Interval(500, 1000, "Doesn't exist"))  # raises ValueError
    Traceback (most recent call last):
    ValueError
    
    >>> t.discard(Interval(500, 1000, "Doesn't exist"))  # quietly does nothing

    >>> del t[5]  # same as t.remove_overlap(5)
    >>> t
    IntervalTree()
    
    ```

    We could also empty a tree by removing all intervals (this works in O(1) time):

    ``` python
    >>> t2.empty()
    >>> t2
    IntervalTree()
    
    ```
    
    We can also remove intervals that overlap a range:
    
    ``` python
    >>> t = IntervalTree([
    ...     Interval(0, 10), 
    ...     Interval(10, 20), 
    ...     Interval(20, 30), 
    ...     Interval(30, 40)])
    >>> t.remove_overlap(25, 35)
    >>> sorted(t)
    [Interval(0, 10), Interval(10, 20)]

    ```
    
    And we can remove only those intervals completely enveloped in a range:
    
    ``` python
    >>> t.remove_envelop(5, 20)
    >>> sorted(t)
    [Interval(0, 10)]
    
    ```
    
* Chopping

    We could also chop out parts of the tree:
    
    ``` python
    >>> t = IntervalTree([Interval(0, 10)])
    >>> t.chop(3, 7)
    >>> sorted(t)
    [Interval(0, 3), Interval(7, 10)]
    
    ```
    
    To modify the new intervals' data fields based on which side of the interval is being chopped:
    
    ``` python
    >>> def datafunc(iv, islower):
    ...     oldlimit = iv[islower]
    ...     return "oldlimit: {0}, islower: {1}".format(oldlimit, islower)
    >>> t = IntervalTree([Interval(0, 10)])
    >>> t.chop(3, 7, datafunc)
    >>> sorted(t)[0]
    Interval(0, 3, 'oldlimit: 10, islower: True')
    >>> sorted(t)[1]
    Interval(7, 10, 'oldlimit: 0, islower: False')

* Slicing

    You can also slice intervals in the tree without removing them:
    
    ``` python
    >>> t = IntervalTree([Interval(0, 10), Interval(5, 15)])
    >>> t.slice(3)
    >>> sorted(t)
    [Interval(0, 3), Interval(3, 10), Interval(5, 15)]
    
    ```
    
    You can also set the data fields, for example, re-using `datafunc()` from above:
    
    ``` python
    >>> t = IntervalTree([Interval(5, 15)])
    >>> t.slice(10, datafunc)
    >>> sorted(t)[0]
    Interval(5, 10, 'oldlimit: 15, islower: True')
    >>> sorted(t)[1]
    Interval(10, 15, 'oldlimit: 5, islower: False')
    
    
Future improvements
-------------------

See the [issue tracker][] on GitHub.

Based on
--------

* Eternally Confuzzled's [AVL tree][Confuzzled AVL tree]
* Wikipedia's [Interval Tree][Wiki intervaltree]
* Heavily modified from Tyler Kahn's [Interval Tree implementation in Python][Kahn intervaltree] ([GitHub project][Kahn intervaltree GH])
* Incorporates modifications by [konstantint][Konstantin intervaltree]

Copyright
---------

* [Chaim-Leib Halbert][GH], 2013-2014
* Modifications, [Konstantin Tretyakov][Konstantin intervaltree], 2014

Licensed under the [Apache License, version 2.0][Apache].

The source code for this project is at https://github.com/chaimleib/intervaltree


[build status badge]: https://travis-ci.org/chaimleib/intervaltree.svg?branch=master
[build status]: https://travis-ci.org/chaimleib/intervaltree
[GH]: https://github.com/chaimleib/intervaltree
[issue tracker]: https://github.com/chaimleib/intervaltree/issues
[Konstantin intervaltree]: https://github.com/konstantint/PyIntervalTree
[Confuzzled AVL tree]: http://www.eternallyconfuzzled.com/tuts/datastructures/jsw_tut_avl.aspx
[Wiki intervaltree]: http://en.wikipedia.org/wiki/Interval_tree
[Kahn intervaltree]: http://zurb.com/forrst/posts/Interval_Tree_implementation_in_python-e0K
[Kahn intervaltree GH]: https://github.com/tylerkahn/intervaltree-python
[Apache]: http://www.apache.org/licenses/LICENSE-2.0
