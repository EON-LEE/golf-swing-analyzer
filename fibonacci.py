"""Fibonacci sequence generator with optimizations."""

from typing import List, Iterator
from functools import lru_cache

def fibonacci(n: int) -> List[int]:
    """
    Calculate fibonacci sequence up to n numbers.
    
    Args:
        n: Number of fibonacci numbers to generate
        
    Returns:
        List of fibonacci numbers
        
    Raises:
        TypeError: If n is not an integer
        ValueError: If n is negative
    """
    if not isinstance(n, int):
        raise TypeError("n must be an integer")
    if n < 0:
        raise ValueError("n must be non-negative")
    
    if n == 0:
        return []
    if n == 1:
        return [0]
    
    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])
    
    return fib

@lru_cache(maxsize=None)
def fibonacci_nth(n: int) -> int:
    """Get nth fibonacci number (0-indexed) with memoization."""
    if n < 0:
        raise ValueError("n must be non-negative")
    if n <= 1:
        return n
    return fibonacci_nth(n-1) + fibonacci_nth(n-2)

def fibonacci_generator(limit: int) -> Iterator[int]:
    """Generate fibonacci numbers up to limit."""
    a, b = 0, 1
    count = 0
    while count < limit:
        yield a
        a, b = b, a + b
        count += 1
