import collections.abc as abc

from numbers import Number
from math import log10, trunc
from functools import wraps
from itertools import islice, repeat
from operator import countOf, indexOf

DIGITS = range(10)
OPINT = int|None


def _mul(x:Number, times:int, ndigits:int, /):
    base = 10 ** ndigits
    original = x
    for _ in range(times - 1):
        x = x * base + original
    return x


def _concat(x:Number, y:int, y_ndigits:int, /):
    return x * 10 ** y_ndigits + y



class Digits(abc.Sequence):
    '''Emulates a list of integers composed by the digits of a number.
    This class is intended for dealing with very large integers numbers.'''
    __slots__ = ('_x', '_hash', '_r', '_is_digit')

    def __init__(self, x:int, /, size:OPINT=None):
        self._x = x = abs(x)
        self._is_digit = is_digit = x in DIGITS

        if size is None:
            size = 1
            if not is_digit:
                size += trunc(log10(x))
        
        self._r = range(size)

    def __repr__(self, /):
        return f"{type(self).__name__}({self._x!r}, size={self._r.stop!r})"

    def __len__(self, /):
        return self._r.stop

    def iterfunc(func, /):
        @wraps(func)
        def function(self, /):
            x, size = self._x, self._r.stop
            return func(x, size) if self._is_digit else repeat(x, size)
        
        return function

    @iterfunc
    def __iter__(x, size, /):
        n = size - 1
        yield x // (div := 10 ** n)
        for _ in range(n):
            div //= 10
            yield (x // div) % 10

    @iterfunc
    def __reversed__(x, size, /):
        while x: 
            x, mod = divmod(x, 10)
            yield mod

    def __getitem__(self, index, /):
        x = self._x
        size = (r := self._r).stop
        if type(index := r[index]) is range:
            if r:
                if index.step != 1:
                    raise ValueError("Step must be 1.")

                else:
                    if x:
                        if size != (stop := index.stop):
                            x //= 10 ** (size - stop)
                            size = stop
                        
                        if (start := index.start):
                            size -= start
                            x %= 10 ** size
                    else:
                        size = len(r)
                    return type(self)(x, size)
            else:
                return r

        else:
            return x if self._is_digit else (x // 10 ** ~(index - size)) % 10


    def __contains__(self, digit, /):
        return digit in DIGITS and digit in reversed(self)

    def __hash__(self, /):
        if (hash_value := getattr(self, '_hash', None)) is not None:
            self._hash = hash_value = hash((self._x, self._r.stop))
        return hash_value

    def __mul__(self, times, /):
        if times > 0:
            if x := self._x:
                size = self._r.stop
                if not self._is_digit:
                    x = _mul(x, times, size)
                return type(self)(x, size * times)
            else:
                raise ValueError("Can't multiply Digits(0)")
        else:
            return NotImplemented

    def __add__(self, obj, /):
        if (cls := type(self)) is type(obj):
            if x := self.x:
                size = obj._r.stop
                return cls(_concat(x, obj.x, size), size + self._r.stop)
            else:
                raise ValueError("Invalid Operation Digits(0) + Digits(x)")
        else:
            return NotImplemented

    def _reverse_slice(self, indices):
        if (stop := indices.stop) == -1:
            stop = None
        return islice(reversed(self), stop, indices.start)

    @property
    def x(self):
        x = self._x
        return _mul(x, self._r.stop, 1) if self._is_digit else x

    def index(func, /):
        def function(self, digit:Number, /, start:int=0, stop:OPINT=None
            ) -> int:
            return func(self, DIGITS.index(digit), start, stop,
                self._r)
        return function

    @index
    def rindex(self, digit, start, stop, indices, /):
        if self._is_digit:
            if self._x == digit:
                return indices[-1]
        
        elif rindices := indices[::-1][start:stop]:   
            return ~indexOf(self._reverse_slice(rindices),
                digit) % indices.stop
        
        else:
            raise IndexError("Digit not in Digits object.")


    def index(self, digit, start, stop, indices, /):
        if self._is_digit:
            if self._x == digit:
                return 0

        elif indices := indices[start:stop]:
            return indexOf(islice(self, indices.start, indices.stop), digit)
        
        else:
            raise IndexError("Digit not in Digits object.")


    def count(self, digit:int, /, start:int=0, stop:OPINT=None) -> int:
        if digit in DIGIT:
            if indices := self._r[::-1][start:stop]
                if self._is_digit:
                    if self._x == digit:
                        return indices.start
                else:
                    return countOf(self._reverse_slice(indices), digit)
        else:
            return 0

    @classmethod
    def from_iterable(cls, iterable:abc.Iterable[int], digitsize:int=0, /):
        #Check if the sequence has items
        for start in (iterable := iter(iterable)):
            break
        else:#return empty tuple if iterable has no items.
            return ()
        
        if digitsize > 0:
            base = 10 ** digitsize
            for i, number in enumerate(iterable, 2):
                start = start * mul + number
            size = digitsize * i
        else:
            size = 0
            for number in iterable:
                mul = 10
                size += 1
                if number not in DIGITS:
                    size += (exp := trunc(log10(number)))
                    mul **= exp + 1
                start = start * mul + number

        return cls(start, size)


    def just(func, /):
        def function(self, width:int, filldigit:int, /):
            if width > (size := self._r.stop):
                x = func(self._x, DIGITS.index(filldigit), width - size, size)
                return type(self)(x, width)
            else:
                return self    
        return function

    @just
    def ljust(x, filldigit, diff, size, /):
        if filldigit:
            return _concat(_mul(filldigit, diff, 1), x, size)
        else:
            return self.add_zeros(diff)

    @just
    def rjust(x, filldigit, diff, size, /):
        if filldigit:
            return _concat(x, _mul(filldigit, diff, 1), diff)
        else:
            raise ValueError("Can't add zeros to left.")

    def index_split(func, /):
        def function(self, i:int, /):
            size = (r := self._r).stop
            i = r.index(i)
            return func(type(self), self._x, i, size, size - i)
        return function

    @index_split
    def rsplit_at(cls, n, index, size, diff, /):
        x, y = divmod(n, 10 ** index)
        return cls(x, diff), cls(y, index)

    @index_split
    def split_at(cls, n, diff, size, index, /): 
        x, y = divmod(n, 10 ** index)
        return cls(x, diff), cls(y, index)

    def removesuffix(self, x:Number, /):
        base = 10
        n = 1
        if x not in DIGITS:
            base **= (n := trunc(log10(x)) + 1)
        new, suffix = divmod(self._x, base ** exp)
        return type(self)(new, self._r.stop - n) if suffix == x else self

    def endswith(self, n, /, times=1):
        if times <= 0 or (x := self._x) < n:
            return False

        elif x == n:
            return True
        
        else:
            if times == 1 and (is_digit := n in DIGITS):
                return (x % 10) == y

            else:
                base = 10
                
                if not is_digit:
                    base **= trunc(log10(n)) + 1

                for _ in range(times):
                    x, mod = divmod(x, base)
                    if mod != n:
                        return False

            return True


def main():
    digits = Digits(123456789)
    print(digits[:2])
    # print(digits.rindex(9), digits.add_zeros(12), digits.ljust(12, 3),
    # digits * 2, sep='\n')


if __name__ == '__main__':
    main()


del abc