from importlib.metadata import version

__version__ = version("phortinize")


def main() -> None:
    print(f"Phortinize {__version__}")
