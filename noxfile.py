
import nox

# Run tests under each supported minor version
@nox.session(python=["3.12", "3.11", "3.10"])
def tests(session):
    """Run pytest for all supported Python versions."""
    session.install(".[dev]")  # install main and dev dependencies from pyproject.toml
    session.run("pytest", "-q")
