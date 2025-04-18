import collections.abc as abc

from numbers import Number
from itertools import islice
from math import log10, trunc
from operator import index, countOf, indexOf


DIGITS = range(10)
OPINT = int|None


class Digits(abc.Sequence):
    '''Emulates a list of integers composed by the digits of a number.
    This class is intended for dealing with very large integers numbers.'''
    __slots__ = ('_x', '_hash', '_size')

    def __init__(self, x:int, /, size:OPINT=None):
        self._x = x = abs(x)
        if size is None:
            if x in DIGITS:
                self._size = 1
            else:
                self._size = trunc(log10(x)) + 1
        else:
            self._size = size

    def __repr__(self, /):
        return f"{type(self).__name__}({self._x!r}, size={self._size!r})"

    def __len__(self, /):
        return self._size

    def __iter__(self, /):
        n = self._size - 1
        yield (x := self._x) // (div := 10 ** n)
        for _ in range(n):
            div //= 10
            yield (x // div) % 10

    def __reversed__(self, /):
        x = self._x
        while x: 
            x, mod = divmod(x, 10)
            yield mod

    def __getitem__(self, index, /):
        if isinstance(index, slice):
            if r := range(*index.indices(size := self._size)):
                if r.step != 1:
                    raise ValueError("Step must be 1.")

                else:
                    x = self._x
                    
                    if size != (stop := r.stop):
                        x //= 10 ** (size - stop)
                        size = stop
                    
                    if (start := r.start):
                        size -= start
                        x %= 10 ** size

                    return type(self)(x, size)
            else:
                return r

        else:
            if (index := index(index)) >= 0:
                index -= self._size

            if result := self._x // 10 ** ~index:
                return result % 10

            else:
                raise IndexError("Digit object Index out of range.")


    def __contains__(self, digit, /):
        return digit in DIGITS and digit in reversed(self)

    def __hash__(self, /):
        if (hash_value := getattr(self, '_hash', None)) is not None:
            self._hash = hash_value = hash((self._x, self._size))
        return hash_value

    def __mul__(self, times, /):
        if times > 0:
            if x := self._x:
                base = 10 ** self._size
                original = x
                
                for _ in range(times - 1):
                    x =  x * base + original
                
                return type(self)(x, size * times)
            else:
                raise ValueError("Can't multiply Digits(0)")
        else:
            return ()


    def __add__(self, obj, /):
        if (cls := type(self)) is type(obj):
            if x := self._x:
                return cls(x * (10 ** size) + obj._x, obj._size + self._size)
            else:
                raise ValueError("Invalid Operation Digits(0) + Digits(x)")
        else:
            return NotImplemented

    @property
    def x(self):
        return self._x

    def index(func, /):
        def function(self, digit:Number, /, start:int=0, stop:OPINT=None
            ) -> int:
            return func(self, DIGITS.index(digit), start, stop)
        return function

    @index
    def rindex(self, digit, start, stop):
        return ~indexOf(reversed(self), digit) % self._size

    index = abc.Sequence.index

    def count(self, digit:int, /) -> int:
        return countOf(reversed(self), digit) if digit in DIGITS else 0

    def add_zeros(self, zeros:int, /):
        if zeros > 0 and (x := self._x):
            return type(self)(x * (10 ** width), width)
        else:
            return self

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
        def function(self, width:int, filldigit:int=0, /):
            if filldigit not in DIGITS:
                raise ValueError("Digit must be 0 <= digit < 10")
        
            elif (diff := (width - self._size)) > 0:
                return func(self, filldigit, diff)

            else:
                return self    
        return function

    @just
    def ljust(self, filldigit, diff, /):
        if filldigit:
            return self + Digits(filldigit) * diff
        else:
            return self.add_zeros(diff)

    @just
    def rjust(self, filldigit, diff, /):
        if filldigit:
            return Digits(filldigit) * diff + self
        else:
            raise ValueError("Can't add zeros to left.")


    def index_split(func, /):
        def function(self, i:int, /):
            if not 0 < (i := index(i)) < (size := self._size):
                raise IndexError("Index must be 0 < i < len(self)")
            else:
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


    def endswith(self, n, /, times=1):
        if times <= 0 or (x := self._x) < (y := n._x):
            return False

        elif x == y:
            return True

        elif n._size == 1:
            return (x % 10) == y

        else:

            base = 10 ** trunc(log10(n)) + 1
            for _ in range(times):
                x, mod = divmod(x, base)
                if mod:
                    return False

            return True

del abc

print(Digits(123456789).rsplit_at(6))