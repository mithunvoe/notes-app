"""
Decorator Pattern Implementation for Cross-Cutting Concerns

This module implements the Decorator design pattern to add behaviors like
retry logic, rate limiting, and timeouts to functions without modifying
their core logic.

Benefits:
- DRY (Don't Repeat Yourself) - Single implementation of retry/rate limit logic
- Composable - Can stack multiple decorators
- Declarative - Clear intent at function definition
- Separation of Concerns - Business logic separate from infrastructure
- Easy to test and modify

Example usage:
    @retry_on_failure(max_attempts=3, backoff_factor=2)
    @with_rate_limit(calls_per_minute=10)
    @with_timeout(60)
    def my_api_call():
        # Your code here
        pass
"""

import time
import functools
from typing import Callable, Any, Optional, Type
from threading import Lock
from collections import deque
from datetime import datetime, timedelta
import signal


class TimeoutError(Exception):
    """Raised when a function execution times out"""
    pass


class RateLimitExceeded(Exception):
    """Raised when rate limit is exceeded"""
    pass


def retry_on_failure(
    max_attempts: int = 3,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,),
    on_retry: Optional[Callable[[Exception, int], None]] = None
):
    """
    Decorator that retries a function on failure with exponential backoff.

    This decorator implements the retry pattern, catching specified exceptions
    and retrying the function with increasing delays between attempts.

    Args:
        max_attempts: Maximum number of attempts (default: 3)
        backoff_factor: Multiplier for exponential backoff (default: 2.0)
                       Wait time = backoff_factor ^ (attempt - 1)
        exceptions: Tuple of exception types to catch and retry (default: all)
        on_retry: Optional callback function called before each retry
                 Signature: callback(exception, attempt_number)

    Example:
        @retry_on_failure(max_attempts=3, backoff_factor=2)
        def unreliable_api_call():
            # This will retry up to 3 times with exponential backoff
            response = requests.get("https://api.example.com")
            return response.json()

    Returns:
        Decorated function with retry logic
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    # Don't sleep on last attempt
                    if attempt < max_attempts:
                        # Calculate wait time with exponential backoff
                        wait_time = backoff_factor ** (attempt - 1)

                        # Call retry callback if provided
                        if on_retry:
                            on_retry(e, attempt)

                        print(f"Attempt {attempt}/{max_attempts} failed: {str(e)}")
                        print(f"Retrying in {wait_time:.1f} seconds...")
                        time.sleep(wait_time)
                    else:
                        print(f"Attempt {attempt}/{max_attempts} failed: {str(e)}")
                        print(f"Max attempts reached, giving up.")

            # If we get here, all attempts failed
            raise last_exception

        return wrapper
    return decorator


def with_timeout(seconds: int):
    """
    Decorator that enforces a timeout on function execution.

    This decorator uses signals (on Unix) or threading (on Windows) to
    interrupt function execution if it takes longer than specified.

    Args:
        seconds: Maximum execution time in seconds

    Example:
        @with_timeout(60)
        def slow_operation():
            # This will raise TimeoutError if it takes longer than 60 seconds
            time.sleep(100)

    Note:
        On Windows, this uses threading which may not interrupt blocking I/O.
        On Unix/Linux, this uses SIGALRM which can interrupt most operations.

    Returns:
        Decorated function with timeout enforcement
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Use signal-based timeout on Unix systems
            try:
                # Try signal-based approach (Unix/Linux)
                def timeout_handler(signum, frame):
                    raise TimeoutError(f"Function '{func.__name__}' timed out after {seconds} seconds")

                # Set the signal handler and alarm
                old_handler = signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(seconds)

                try:
                    result = func(*args, **kwargs)
                finally:
                    # Cancel the alarm
                    signal.alarm(0)
                    # Restore old handler
                    signal.signal(signal.SIGALRM, old_handler)

                return result

            except AttributeError:
                # signal.SIGALRM not available (Windows)
                # Fall back to thread-based timeout (less reliable for blocking I/O)
                import threading

                result = [None]
                exception = [None]

                def target():
                    try:
                        result[0] = func(*args, **kwargs)
                    except Exception as e:
                        exception[0] = e

                thread = threading.Thread(target=target)
                thread.daemon = True
                thread.start()
                thread.join(seconds)

                if thread.is_alive():
                    # Thread is still running, timeout occurred
                    raise TimeoutError(f"Function '{func.__name__}' timed out after {seconds} seconds")

                if exception[0]:
                    raise exception[0]

                return result[0]

        return wrapper
    return decorator


class RateLimiter:
    """
    Rate limiter using a sliding window algorithm.

    This class implements a token bucket / sliding window rate limiter
    that tracks function calls and enforces rate limits.

    Thread-safe implementation using locks.
    """

    def __init__(self, calls_per_minute: int):
        """
        Initialize rate limiter.

        Args:
            calls_per_minute: Maximum number of calls allowed per minute
        """
        self.calls_per_minute = calls_per_minute
        self.min_interval = 60.0 / calls_per_minute  # Minimum seconds between calls
        self.call_times: deque = deque()
        self.lock = Lock()

    def acquire(self, blocking: bool = True) -> bool:
        """
        Acquire permission to make a call.

        Args:
            blocking: If True, wait until rate limit allows the call
                     If False, return immediately (True if allowed, False if rate limited)

        Returns:
            True if call is allowed, False if rate limited (only when blocking=False)
        """
        with self.lock:
            now = datetime.now()
            window_start = now - timedelta(minutes=1)

            # Remove calls outside the sliding window
            while self.call_times and self.call_times[0] < window_start:
                self.call_times.popleft()

            # Check if we're within the rate limit
            if len(self.call_times) < self.calls_per_minute:
                self.call_times.append(now)
                return True

            # Rate limit exceeded
            if not blocking:
                return False

            # Calculate wait time until oldest call expires
            oldest_call = self.call_times[0]
            wait_until = oldest_call + timedelta(minutes=1)
            wait_seconds = (wait_until - now).total_seconds()

            if wait_seconds > 0:
                print(f"Rate limit reached ({self.calls_per_minute} calls/min). Waiting {wait_seconds:.1f}s...")

        # Release lock while sleeping (allow other threads to check rate limit)
        if wait_seconds > 0:
            time.sleep(wait_seconds)

        # Recursive call after waiting
        return self.acquire(blocking=True)


def with_rate_limit(calls_per_minute: int):
    """
    Decorator that enforces rate limiting on function calls.

    This decorator uses a sliding window algorithm to ensure that
    a function is not called more than N times per minute.

    Args:
        calls_per_minute: Maximum number of calls allowed per minute

    Example:
        @with_rate_limit(calls_per_minute=10)
        def api_call():
            # This will be rate limited to 10 calls per minute
            return requests.get("https://api.example.com")

        # Calling api_call() 15 times in a row will cause the 11th call
        # to wait until the rate limit window allows it

    Returns:
        Decorated function with rate limiting
    """
    # Create a rate limiter instance per decorated function
    rate_limiter = RateLimiter(calls_per_minute)

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Acquire rate limit permission (will block if necessary)
            rate_limiter.acquire(blocking=True)

            # Execute function
            return func(*args, **kwargs)

        return wrapper
    return decorator


def with_exponential_backoff(
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    factor: float = 2.0
):
    """
    Decorator that adds exponential backoff between consecutive calls.

    Useful for API calls where you want to gradually increase delay
    between requests to avoid overwhelming the server.

    Args:
        initial_delay: Initial delay in seconds (default: 1.0)
        max_delay: Maximum delay in seconds (default: 60.0)
        factor: Multiplier for each consecutive call (default: 2.0)

    Example:
        @with_exponential_backoff(initial_delay=1.0, max_delay=30.0)
        def poll_status():
            # First call: no delay
            # Second call: 1s delay
            # Third call: 2s delay
            # Fourth call: 4s delay
            # Fifth call: 8s delay
            # Sixth call: 16s delay
            # Seventh call: 30s delay (capped at max_delay)
            return check_job_status()

    Returns:
        Decorated function with exponential backoff
    """
    state = {'last_call_time': None, 'current_delay': initial_delay}
    lock = Lock()

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            with lock:
                if state['last_call_time'] is not None:
                    # Calculate elapsed time since last call
                    elapsed = time.time() - state['last_call_time']
                    remaining_delay = state['current_delay'] - elapsed

                    if remaining_delay > 0:
                        print(f"Exponential backoff: waiting {remaining_delay:.1f}s...")
                        time.sleep(remaining_delay)

                    # Increase delay for next call
                    state['current_delay'] = min(state['current_delay'] * factor, max_delay)
                else:
                    # First call, no delay
                    state['current_delay'] = initial_delay

                state['last_call_time'] = time.time()

            return func(*args, **kwargs)

        # Add reset method to reset backoff state
        def reset_backoff():
            with lock:
                state['last_call_time'] = None
                state['current_delay'] = initial_delay

        wrapper.reset_backoff = reset_backoff

        return wrapper
    return decorator


# Convenience function for common combinations
def with_resilience(
    max_attempts: int = 3,
    timeout_seconds: int = 60,
    calls_per_minute: Optional[int] = None
):
    """
    Composite decorator combining retry, timeout, and optional rate limiting.

    This is a convenience decorator that applies multiple decorators in the
    correct order for robust API calls.

    Args:
        max_attempts: Maximum retry attempts
        timeout_seconds: Timeout per attempt in seconds
        calls_per_minute: Optional rate limit (calls per minute)

    Example:
        @with_resilience(max_attempts=3, timeout_seconds=60, calls_per_minute=10)
        def robust_api_call():
            return requests.get("https://api.example.com").json()

    Returns:
        Decorated function with retry, timeout, and rate limiting
    """
    def decorator(func: Callable) -> Callable:
        # Apply decorators in order: rate limit -> timeout -> retry
        decorated = func

        # Apply retry first (innermost)
        decorated = retry_on_failure(max_attempts=max_attempts)(decorated)

        # Apply timeout
        decorated = with_timeout(timeout_seconds)(decorated)

        # Apply rate limit if specified (outermost)
        if calls_per_minute:
            decorated = with_rate_limit(calls_per_minute)(decorated)

        return decorated

    return decorator
