from concurrent.futures import ThreadPoolExecutor
from typing import Callable, List


def batch_parallel_run(tasks: List[Callable]) -> None:
    """
    Run a batch of tasks in parallel. This should be used for I/O-bound tasks.
    Reference used:
    https://stackoverflow.com/a/56138825
    https://stackoverflow.com/a/58897275
    """
    with ThreadPoolExecutor() as executor:
        running_tasks = [executor.submit(task) for task in tasks]
        for running_task in running_tasks:
            running_task.result()
