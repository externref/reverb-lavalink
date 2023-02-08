import typing

import nox


def with_poetry(*deps: str):
    def decorator(callable: typing.Callable[[nox.Session], None]) -> None:
        @nox.session(name=callable.__name__)
        def _(session: nox.Session) -> None:
            session.log("checking dependencies")
            session.run("poetry", "install", external=True, silent=True)
            callable(session)

    return decorator


CODE_PATHS = ("reverb", "examples")


@with_poetry("black")
def run_black(session: nox.Session) -> None:
    session.run("poetry", "run", "python", "-m", "black", *CODE_PATHS, external=True)


@with_poetry("isort")
def run_isort(session: nox.Session) -> None:
    session.run("poetry", "run", "python", "-m", "isort", *CODE_PATHS, external=True)
