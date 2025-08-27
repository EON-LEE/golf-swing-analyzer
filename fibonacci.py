def fibonacci(n):
    """
    Calculate fibonacci sequence up to n numbers.
    
    Args:
        n (int): Number of fibonacci numbers to generate
        
    Returns:
        list: List of fibonacci numbers
        
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
