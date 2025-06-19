import time
import threading


class BatchMonitor:
    def __init__(self, client, batch_id, goal_fn, callback_fn, interval=30):
        """
        Args:
            client (Client): Turkle client instance
            batch_id (int): ID of the batch to monitor
            goal_fn (Callable[[dict], bool]): Function that receives progress dict and returns True if goal is met
            callback_fn (Callable[[dict], None]): Function called once goal is met. Received progress dict
            interval (int): Seconds between polling API
        """
        self.client = client
        self.batch_id = batch_id
        self.goal_fn = goal_fn
        self.callback_fn = callback_fn
        self.interval = interval
        self._stop_event = threading.Event()

    def _check_loop(self, timeout=None):
        start_time = time.time()
        while not self._stop_event.is_set():
            try:
                progress = self.client.batches.progress(self.batch_id)
                if self.goal_fn(progress):
                    self.callback_fn(progress)
                    return
            except Exception as e:
                print(f"Error checking progress: {e}")
            if timeout is not None and (time.time() - start_time) > timeout:
                raise TimeoutError(f"BatchMonitor timed out after {timeout} seconds")
            time.sleep(self.interval)

    def wait(self, timeout=None):
        """
        Block until the goal is reached or timeout is exceeded.

        Args:
            timeout (int or float, optional): Maximum time in seconds to wait. None means no timeout.

        Raises:
            TimeoutError: If timeout is exceeded before goal is reached.
        """
        self._check_loop(timeout=timeout)

    def start_background(self):
        """Start monitoring in a background thread."""
        thread = threading.Thread(target=self._check_loop, daemon=True)
        thread.start()
        return thread

    def stop(self):
        """Stop monitoring (only applies to background mode)."""
        self._stop_event.set()
