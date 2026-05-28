"""Rich-console rendering of demo output.

rich is imported lazily inside each helper so importing this module (and the
runners that use it) stays light and unit tests remain hermetic.
"""


def print_json_result(data) -> None:
    """Pretty-print a result dict as syntax-highlighted JSON."""
    from rich import print_json
    print_json(data=data)


def print_text_result(text: str, title: str = "De-identified (tagged text)") -> None:
    """Print plain/tagged text in a titled panel (literal, no markup parsing)."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    Console().print(Panel(Text(text), title=title, expand=False))
