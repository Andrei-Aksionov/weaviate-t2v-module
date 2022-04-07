from time import sleep

import requests


def wait_for_startup(url: str, expected_status_code: int, timeout: int) -> None:
    """Wait till either response status code is equal to expected or timeout is exceeded.

    Parameters
    ----------
    url : str
        what endpoint to call
    expected_status_code : int
        what status code is excpected
    timeout : int
        home many seconds to try to call endpoint

    Raises
    ------
    requests.Timeout
        if timeout time is exceeded and endpoint didn't return excepted status code
    """
    for _ in range(timeout):
        try:
            response = requests.get(url)
            if response.status_code == expected_status_code:
                return None
        except requests.exceptions.ConnectionError:
            # in case service inside docker container is not yet running
            pass
        sleep(1)

    raise requests.Timeout(f"Service hasn't started in {timeout} seconds")
