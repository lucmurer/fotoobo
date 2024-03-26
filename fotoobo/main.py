"""
This is the main project entry point.

When invoking fotoobo it starts the main() function in this file. Its main purpose is to start the
typer cli with app().
The second task is to catch all exceptions and print a friendly message on the screen instead of
a traceback. The traceback is written to a traceback.log file in the local directory for debug
purposes.

The exceptions in the main functions cannot be tested because the test-method for typer always
exits with its own exit codes (1 or 2) when an exception rises.
"""
import sys
import traceback

from rich.console import Console
from rich.panel import Panel

from fotoobo.cli.main import app
from fotoobo.exceptions import APIError, FotooboError, FotooboWarning


def main() -> None:
    """
    This is the main function
    """
    try:
        app()

    except FotooboWarning as warn:
        console = Console(style="#ff6600", stderr=True)
        console.print(
            Panel(
                f"fotoobo finished with a warning:\n{warn}",
                title="Warning",
                title_align="left",
            )
        )
        sys.exit(30)

    except (FotooboError, APIError) as err:
        console = Console(style="#ff0000", stderr=True)
        console.print(
            Panel(
                f"fotoobo finished with an error:\n{err}\nCannot continue.",
                title="Error",
                title_align="left",
            )
        )
        sys.exit(40)

    except Exception:  # pylint: disable=broad-except # pragma: no cover
        print("oops, something did not work as expected. See traceback.log for more info")
        with open("traceback.log", "w", encoding="UTF-8") as exc_file:
            traceback.print_exc(file=exc_file)
        sys.exit(50)


if __name__ == "__main__":  # pragma: no cover
    main()
