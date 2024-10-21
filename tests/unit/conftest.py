from pathlib import Path

from glue_jupyter.data import require_data


def pytest_sessionstart(session):
    # Ensure that required example data is available
    if not Path("w5.fits").exists():
        require_data("Astronomy/W5/w5.fits")
