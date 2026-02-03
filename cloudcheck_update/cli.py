import os
import sys
from cloudcheck_update import update


def main():
    threshold = int(os.environ.get("ERROR_THRESHOLD", 10))
    errors = update()
    for error in errors:
        print(error)
    error_count = len(errors)
    if error_count > threshold:
        print(f"Error count ({error_count}) exceeds threshold ({threshold})")
        return 1
    elif error_count > 0:
        print(f"Error count ({error_count}) within threshold ({threshold})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
