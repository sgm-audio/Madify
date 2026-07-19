from importlib.metadata import version

__version__ = version("madify")


def main() -> None:
    print(f"Madify {__version__}")
