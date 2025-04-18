import collections.abc as abc

from numbers import Number
from math import log10, trunc
from itertools import islice, repeat
from operator import countOf, indexOf, floordiv, mod, mul


DIGITS = range(10)
OPINT = int|None


def reverse_digits(x:Number, /) -> abc.Generator[Number]:
    x = abs(x)
    while x:
        x, mod = divmod(x, 10)
        yield x
    else:
        yield x


def digital_root(x:Number, /) -> Number:
    return x % 9 or x


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

    def __init__(self, x:int, /, size:int):
        self._x = x = abs(x)
        self._is_digit = x in DIGITS
        self._r = range(size)


    def __repr__(self, /):
        return f"{type(self).__name__}({self._x!r}, size={self._r.stop!r})" 

    def __len__(self, /):
        return self._r.stop

    def __iter__(self, /):
        if size := self._r.stop:
            rdigits = bytes(reverse_digits(self._x))
            
            if size > (ndigits := len(rdigits)):
                yield from repeat(0, size - ndigits)
            
            yield from reversed(rdigits)


    def __reversed__(self, /):
        x = self._x
        
        for i in reversed(self._r):
            if not x:
                break
            
            x, mod = divmod(x, 10)  
            yield mod

        else:
            return
        
        if i:
            yield from repeat(x, i)


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
            else:
                size = 0

            return type(self)(x, size)

        else:
            return x and (x // 10 ** ~(index - size)) % 10


    def __contains__(self, digit, /):
        if digit in DIGITS:
            x = self._x
            return x == digit if self._is_digit else digit in reversed(self)
        else:
            return False

    def __hash__(self, /):
        if (hash_value := getattr(self, '_hash', None)) is not None:
            self._hash = hash_value = hash((self._x, self._r.stop))
        return hash_value

    def __mul__(self, times, /):
        x = self._x
        if (size := self._r.stop) and times > 0:
            size *= times
            if x:
                base = 10 ** size
                original = x
                for _ in range(times - 1):
                    x = x * base + original

        return type(self)(x, size)    

    def __add__(self, obj, /):
        if (cls := type(self)) is type(obj):
            size = obj._r.stop
            return cls(x * 10 ** size + obj.x, size + self._r.stop)
        else:
            return NotImplemented

    def _reverse_slice(self, indices):
        if (stop := indices.stop) == -1:
            stop = None
        return islice(reversed(self), stop, indices.start)

    @property
    def x(self):
        return self._x:

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


    @index
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


    def index_split(reverse, /):
        def function(self, i:int, /):
            size = (r := self._r).stop
            i = r.index(i)
            if not reverse:
                index = size - index
            tuple(map(cls, divmod(n, 10 ** index)))
            return func(type(self), self._x, i, size)
        return function

    rsplit_at, rsplit_at = map(index_split, (True, False))


    def last(func, /):
        def function(self, n:int, /):
            r = self._r
            return type(self)(func(self._x, 10 ** (n := r.index(n))), r.stop - n)

    last_n = last(floordiv)

    removelast_n = last(mod)

    def digital_root(self, /): return digital_root(self._x)
    
    @classmethod
    def from_number(cls, x:Number, /):
        return cls(x, log10(trunc(x)) + 1 if (x := abs(x)) else 1)


def main():
    digits = Digits(123456789)
    print(digits[:2])
    # print(digits.rindex(9), digits.add_zeros(12), digits.ljust(12, 3),
    # digits * 2, sep='\n')


if __name__ == '__main__':
    main()


del abc, floordiv, mod