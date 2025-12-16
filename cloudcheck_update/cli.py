import sys
from cloudcheck_update import update


def main():
    errors = update()
    for error in errors:
        print(error)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
