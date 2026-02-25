"""
Error Recovery Module - Retry Logic with Exponential Backoff

Provides reusable error recovery patterns for watchers and MCP servers:
- Exponential backoff retry logic
- Graceful degradation
- Queue management for offline APIs
- Circuit breaker pattern
"""

import time
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Callable, Any, Optional, Dict, List
from functools import wraps
import threading

# Configuration
MAX_RETRIES = 5
BASE_DELAY = 1.0  # seconds
MAX_DELAY = 60.0  # seconds
EXPONENTIAL_BASE = 2

# Setup logging
logger = logging.getLogger('error_recovery')

# Queue directory for offline operations
QUEUE_DIR = Path("Offline_Queue")
QUEUE_DIR.mkdir(exist_ok=True)


class CircuitBreaker:
    """
    Circuit Breaker Pattern Implementation
    
    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Circuit tripped, requests fail immediately
    - HALF_OPEN: Testing if service recovered
    """
    
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
        self._lock = threading.Lock()
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        with self._lock:
            if self.state == 'OPEN':
                if self._should_attempt_reset():
                    self.state = 'HALF_OPEN'
                    logger.info("Circuit breaker: HALF_OPEN - testing recovery")
                else:
                    logger.warning("Circuit breaker: OPEN - request rejected")
                    raise Exception("Circuit breaker OPEN - service unavailable")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return True
        
        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return elapsed >= self.recovery_timeout
    
    def _on_success(self):
        """Handle successful call"""
        with self._lock:
            self.failures = 0
            self.state = 'CLOSED'
            logger.debug("Circuit breaker: CLOSED - service healthy")
    
    def _on_failure(self):
        """Handle failed call"""
        with self._lock:
            self.failures += 1
            self.last_failure_time = datetime.now()
            
            if self.failures >= self.failure_threshold:
                self.state = 'OPEN'
                logger.error(f"Circuit breaker: OPEN - {self.failures} failures")
    
    def get_status(self) -> Dict[str, Any]:
        """Get circuit breaker status"""
        return {
            'state': self.state,
            'failures': self.failures,
            'threshold': self.failure_threshold,
            'last_failure': self.last_failure_time.isoformat() if self.last_failure_time else None
        }


def retry_with_backoff(
    max_retries: int = MAX_RETRIES,
    base_delay: float = BASE_DELAY,
    max_delay: float = MAX_DELAY,
    exponential_base: float = EXPONENTIAL_BASE,
    exceptions: tuple = (Exception,),
    on_retry: Optional[Callable] = None
):
    """
    Decorator for retry with exponential backoff
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff
        exceptions: Tuple of exceptions to catch
        on_retry: Callback function called on each retry
    
    Usage:
        @retry_with_backoff(max_retries=5, base_delay=1.0)
        def api_call():
            # Your code here
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(f"{func.__name__}: Max retries ({max_retries}) exceeded")
                        break
                    
                    # Calculate delay with exponential backoff and jitter
                    delay = min(
                        base_delay * (exponential_base ** attempt),
                        max_delay
                    )
                    
                    # Add jitter (±10%)
                    import random
                    jitter = delay * 0.1 * (2 * random.random() - 1)
                    delay += jitter
                    
                    logger.warning(
                        f"{func.__name__}: Attempt {attempt + 1}/{max_retries} failed. "
                        f"Retrying in {delay:.2f}s. Error: {str(e)}"
                    )
                    
                    # Call retry callback if provided
                    if on_retry:
                        on_retry(attempt, delay, e)
                    
                    time.sleep(delay)
            
            raise last_exception
        
        return wrapper
    return decorator


class OfflineQueue:
    """
    Queue for operations when API is offline
    
    Stores operations to disk and replays when service recovers
    """
    
    def __init__(self, queue_dir: Path = QUEUE_DIR):
        self.queue_dir = queue_dir
        self.queue_dir.mkdir(exist_ok=True)
        self._lock = threading.Lock()
    
    def enqueue(self, operation: Dict[str, Any]) -> str:
        """Add operation to queue"""
        with self._lock:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            filename = f"queue_{timestamp}.json"
            filepath = self.queue_dir / filename
            
            queue_item = {
                'id': filename.replace('queue_', '').replace('.json', ''),
                'timestamp': datetime.now().isoformat(),
                'operation': operation,
                'retries': 0,
                'status': 'pending'
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(queue_item, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Queued operation: {filename}")
            return queue_item['id']
    
    def dequeue(self) -> Optional[Dict[str, Any]]:
        """Get next operation from queue"""
        with self._lock:
            queue_files = sorted(self.queue_dir.glob('queue_*.json'))
            
            if not queue_files:
                return None
            
            oldest_file = queue_files[0]
            
            with open(oldest_file, 'r', encoding='utf-8') as f:
                queue_item = json.load(f)
            
            return queue_item
    
    def mark_complete(self, queue_id: str):
        """Mark operation as complete and remove from queue"""
        with self._lock:
            filepath = self.queue_dir / f"queue_{queue_id}.json"
            
            if filepath.exists():
                # Move to completed
                completed_dir = self.queue_dir / 'completed'
                completed_dir.mkdir(exist_ok=True)
                
                filepath.rename(completed_dir / filepath.name)
                logger.info(f"Completed operation: {queue_id}")
    
    def mark_failed(self, queue_id: str, error: str):
        """Mark operation as failed"""
        with self._lock:
            filepath = self.queue_dir / f"queue_{queue_id}.json"
            
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    queue_item = json.load(f)
                
                queue_item['status'] = 'failed'
                queue_item['error'] = error
                queue_item['failed_at'] = datetime.now().isoformat()
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(queue_item, f, indent=2, ensure_ascii=False)
                
                logger.error(f"Failed operation: {queue_id} - {error}")
    
    def get_queue_size(self) -> int:
        """Get number of pending operations"""
        with self._lock:
            return len(list(self.queue_dir.glob('queue_*.json')))
    
    def replay_all(self, processor: Callable[[Dict], bool]) -> Dict[str, Any]:
        """
        Replay all queued operations
        
        Args:
            processor: Function to process each operation, returns True on success
        
        Returns:
            Dict with replay statistics
        """
        stats = {
            'total': 0,
            'successful': 0,
            'failed': 0,
            'errors': []
        }
        
        while True:
            queue_item = self.dequeue()
            if not queue_item:
                break
            
            stats['total'] += 1
            
            try:
                operation = queue_item['operation']
                success = processor(operation)
                
                if success:
                    self.mark_complete(queue_item['id'])
                    stats['successful'] += 1
                else:
                    self.mark_failed(queue_item['id'], 'Processor returned False')
                    stats['failed'] += 1
                    stats['errors'].append(f"{queue_item['id']}: Processor failed")
            
            except Exception as e:
                self.mark_failed(queue_item['id'], str(e))
                stats['failed'] += 1
                stats['errors'].append(f"{queue_item['id']}: {str(e)}")
        
        logger.info(f"Replay complete: {stats['successful']}/{stats['total']} successful")
        return stats
    
    def get_status(self) -> Dict[str, Any]:
        """Get queue status"""
        return {
            'pending': self.get_queue_size(),
            'completed': len(list((self.queue_dir / 'completed').glob('*.json'))) if (self.queue_dir / 'completed').exists() else 0,
            'directory': str(self.queue_dir)
        }


# Global circuit breakers for different services
circuit_breakers = {
    'email': CircuitBreaker(failure_threshold=5, recovery_timeout=60),
    'odoo': CircuitBreaker(failure_threshold=3, recovery_timeout=120),
    'social': CircuitBreaker(failure_threshold=5, recovery_timeout=90),
    'twitter': CircuitBreaker(failure_threshold=5, recovery_timeout=90),
    'browser': CircuitBreaker(failure_threshold=3, recovery_timeout=60)
}

# Global offline queues
offline_queues = {
    'email': OfflineQueue(QUEUE_DIR / 'email'),
    'odoo': OfflineQueue(QUEUE_DIR / 'odoo'),
    'social': OfflineQueue(QUEUE_DIR / 'social'),
    'twitter': OfflineQueue(QUEUE_DIR / 'twitter')
}


def resilient_api_call(
    service: str,
    func: Callable,
    *args,
    queue_if_offline: bool = True,
    **kwargs
) -> Any:
    """
    Make API call with full error recovery
    
    Args:
        service: Service name (email, odoo, social, twitter)
        func: Function to call
        queue_if_offline: Queue operation if circuit breaker is open
        *args, **kwargs: Arguments to pass to function
    
    Returns:
        Function result
    
    Usage:
        result = resilient_api_call(
            'odoo',
            create_invoice,
            invoice_data,
            queue_if_offline=True
        )
    """
    circuit_breaker = circuit_breakers.get(service)
    queue = offline_queues.get(service)
    
    if not circuit_breaker:
        # No circuit breaker configured, just call function
        return func(*args, **kwargs)
    
    try:
        # Try to call with circuit breaker
        result = circuit_breaker.call(func, *args, **kwargs)
        logger.debug(f"{service}: API call successful")
        return result
    
    except Exception as e:
        logger.error(f"{service}: API call failed - {str(e)}")
        
        # Queue if offline and queueing enabled
        if queue_if_offline and queue and circuit_breaker.state == 'OPEN':
            operation = {
                'service': service,
                'function': func.__name__,
                'args': args,
                'kwargs': kwargs,
                'queued_at': datetime.now().isoformat()
            }
            
            queue_id = queue.enqueue(operation)
            logger.info(f"{service}: Operation queued (ID: {queue_id})")
            
            return {
                'status': 'queued',
                'queue_id': queue_id,
                'message': f'Operation queued for later execution'
            }
        
        # Re-raise exception if queuing not enabled
        raise e


def get_recovery_status() -> Dict[str, Any]:
    """Get status of all recovery systems"""
    status = {
        'circuit_breakers': {},
        'offline_queues': {},
        'timestamp': datetime.now().isoformat()
    }
    
    for name, cb in circuit_breakers.items():
        status['circuit_breakers'][name] = cb.get_status()
    
    for name, queue in offline_queues.items():
        status['offline_queues'][name] = queue.get_status()
    
    return status


def replay_all_queues() -> Dict[str, Any]:
    """Replay all queued operations across all services"""
    results = {}
    
    for name, queue in offline_queues.items():
        logger.info(f"Replaying {name} queue...")
        
        def processor(operation):
            # Try to execute the queued operation
            # This would need to map back to actual functions
            logger.info(f"Processing queued {name} operation: {operation.get('function', 'unknown')}")
            return True  # Placeholder
        
        results[name] = queue.replay_all(processor)
    
    return results


# Example usage and test
if __name__ == "__main__":
    print("Error Recovery Module - Test")
    print("="*60)
    
    # Test retry with backoff
    @retry_with_backoff(max_retries=3, base_delay=0.5)
    def flaky_function():
        import random
        if random.random() < 0.7:  # 70% failure rate
            raise Exception("Simulated failure")
        return "Success!"
    
    print("\nTesting retry with backoff...")
    try:
        result = flaky_function()
        print(f"Result: {result}")
    except Exception as e:
        print(f"Failed after retries: {e}")
    
    # Test circuit breaker
    print("\nTesting circuit breaker...")
    cb = CircuitBreaker(failure_threshold=3, recovery_timeout=5)
    
    for i in range(5):
        try:
            cb.call(lambda: (_ for _ in ()).throw(Exception("Test error")))
        except:
            pass
        print(f"Attempt {i+1}: State = {cb.state}")
    
    # Test offline queue
    print("\nTesting offline queue...")
    queue = OfflineQueue()
    queue_id = queue.enqueue({'test': 'operation', 'data': 'test123'})
    print(f"Queued operation: {queue_id}")
    print(f"Queue size: {queue.get_queue_size()}")
    
    # Get status
    print("\nRecovery Status:")
    print(json.dumps(get_recovery_status(), indent=2))
    
    print("\n" + "="*60)
    print("Error Recovery Module - Test Complete")
