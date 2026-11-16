
import nox

# Run tests under each supported minor version
@nox.session(python=["3.12", "3.11", "3.10"])
def tests(session):
    """Run pytest for all supported Python versions."""
    session.install(".", "--group", "dev")
    session.run("python", "-m", "pytest")
