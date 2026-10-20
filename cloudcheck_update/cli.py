import os
import sys
from cloudcheck_update import update


def main():
    threshold = int(os.environ.get("ERROR_THRESHOLD", 10))
    errors = update()
    for error in errors:
        print(error)
    error_count = len(errors)
    write_step_summary(errors, threshold)
    if error_count > threshold:
        print(f"Error count ({error_count}) exceeds threshold ({threshold})")
        return 1
    elif error_count > 0:
        print(f"Error count ({error_count}) within threshold ({threshold})")
    return 0


def write_step_summary(errors, threshold):
    """Write the error list to the GitHub Actions job summary, if running in Actions."""
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return
    lines = [f"## Signature update: {len(errors)} errors (threshold {threshold})", ""]
    for error in errors:
        # errors can carry multi-line tracebacks; keep only the first line in the summary
        first_line = (str(error).strip().splitlines() or [""])[0]
        lines.append(f"- {first_line}")
    with open(summary_path, "a") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    sys.exit(main())
