
import nox

# Run tests under each supported minor version
@nox.session(python=["3.12", "3.11", "3.10"])
def tests(session):
    """Run pytest for all supported Python versions."""
    session.install("pytest")
    session.install(".")        # install the package from pyproject.toml
    session.run("pytest", "-q")
