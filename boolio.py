""" A python module for interacting with the BaaS booleans.io.

boolio is free software
boolio is copyright under the MIT License (MIT)

The MIT License (MIT)

Copyright (c) 2016 Logan Byers (github.com/loganbyers)

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE


Author: Logan Byers (github.com/loganbyers)
Date: 2016-04-11
"""

import requests


class Bool (object):

    """Internet-based boolean."""

    def __init__(self, bid=None, val=False):
        """Construct a boolean."""
        if val in ('false', 'False'):
            val = False
        elif val in ('true', 'True'):
            val = True
        if bid is None:
            b = _api_post(val)
            self.bid = b.bid
            self.val = b.val
        else:
            self.bid = bid
            self.val = val

    def copy(self):
        """Get a copy of a boolean."""
        return Bool(self.bid, self.val)

    def pull(self):
        """Sync boolean state from the remote version."""
        b = _api_get(self.bid)
        if b is None:
            return False
        self.val = b.val
        return True

    def toggle(self):
        """Toggle boolean value."""
        if _api_put(self, not self.val):
            self.val = not self.val
            return True
        return False

    def destroy(self):
        """Destroy the online reference."""
        return _api_delete(self.bid)

    def __str__(self):
        """Get a string representation."""
        return str(int(self.val))

    def __call__(self, val=None):
        """Set a value and update the remote version."""
        if val is None:
            return _api_put(self.bid, self.val)
        if type(val) is not bool:
            return
        if _api_put(self.bid, val):
            self.val = val
            return True
        return False


class BoolString (object):

    """An ordered collection of Bool."""

    def __init__(self, length):
        """Construct a string of Bools."""
        self.binary = tuple(Bool() for i in range(length))
        self.length = length

    def copy(self):
        """Get a copy of the object."""
        bs = BoolString(0)
        bs.binary = tuple(b.copy() for b in self.binary)
        bs.length = len(self.binary)
        return bs

    def ids(self):
        """Get the remote ids."""
        return tuple(b.bid for b in self.binary)

    def pull(self):
        """Sync boolean states from the remote versions."""
        return tuple(b.pull() for b in self.binary)

    def bits(self):
        """Get a binary representation."""
        s = ''
        for i in self.binary[::-1]:
            if i.val:
                s = s + '1'
            else:
                s = s + '0'
        return s

    def __int__(self):
        """Get unsigned bit value."""
        r = 0
        for i, b in enumerate(self.binary):
            if b.val:
                r += 2**i
        return r

    def __str__(self):
        """Get representation as string."""
        #return str(unichr(int(self)))
        return self.bits()

    def __len__(self):
        """Get the length of the string."""
        return self.length

    def __getitem__(self, key):
        """Get the value for an index."""
        if key >= len(self.binary):
            return
        return self.binary[key].val

    def __call__(self, position=None, value=None):
        """Set a bit value or sync state to remote version."""
        if (position is None) and (value is None):
            return tuple(b() for b in self.binary)
        if position >= len(self.binary):
            return
        return self.binary[position](value)

    def __iter__(self):
        """Get an iterator."""
        return iter(self.binary)

    def destroy(self):
        """Destroy every boolean."""
        return tuple(b.destroy() for b in self.binary)


def save(file, obj, state=True):
    """Write the a Bool or BoolString to a text file."""
    if type(obj) not in (Bool, BoolString):
        return
    with open(file, 'wb') as fout:
        if type(obj) is Bool:
            if state:
                fout.write(str(obj.bid) + '\t' + str(obj.val) + '\n')
            else:
                fout.write(str(obj.bid) + '\n')
        else:
            for b in obj:
                if state:
                    fout.write(str(b.bid) + '\t' + str(b.val) + '\n')
                else:
                    fout.write(str(b.bid) + '\n')


def load(file):
    """Load a Bool or BoolString from a file."""
    with open(file, 'rb') as fout:
        boolize = lambda x: Bool(*x.rstrip().split('\t'))
        f = fout.readlines()
        if len(f) == 1:
            return boolize(f[0])
        else:
            bs = BoolString(0)
            bs.binary = tuple(map(boolize, f))
            bs.length = len(bs.binary)
            return bs


def _api_post(val=False, verify=False):
    """Create a boolean."""
    if val:
        val = 'true'
    else:
        val = 'false'
    try:
        r = requests.post('https://api.booleans.io', verify=False, data={'val': val})
    except:
        return
    else:
        return Bool(r.json()['id'], r.json()['val'])


def _api_put(bid, val=None):
    """Set a boolean value."""
    url = 'https://api.booleans.io/' + bid
    if val is None:
        r = requests.put(url, verify=False)
    else:
        r = requests.put(url, verify=False, data={'val': _bool_to_val(val)})
    if r.status_code == 404:
        return False
    else:
        return True


def _api_get(bid):
    """Get a boolean."""
    url = 'https://api.booleans.io/' + bid
    r = requests.get(url, verify=False)
    if r.status_code == 404:
        return None
    return Bool(r.json()['id'], r.json()['val'])


def _api_delete(bid):
    """Delete a boolean."""
    if type(bid) is Bool:
        bid = bid.bid
    url = 'https://api.booleans.io/' + bid
    r = requests.delete(url, verify=False)
    if r.status_code == 200:
        return True
    else:
        return False


def _val_to_bool(val):
    """Convert a text representation to a bool."""
    if val == 'true':
        return True
    else:
        return False


def _bool_to_val(val):
    """Convert a bool to a text representation."""
    if val:
        return 'true'
    else:
        return 'false'
