from known_good.models.module import Module
from known_good.models.known_good import Path, load_known_good, KnownGood
import subprocess
import pty
import os
import sys

def run_unit_test(known: KnownGood) -> bool:
    print("Running unit tests...")

    master, slave = pty.openpty()
    file_obj = os.fdopen(master, "rb", buffering=0)

    for _, value in known.modules["target_sw"].items():
        
        call = ["bazel", "test", "--config", "unit-tests", f"@{value.name}{value.metadata.code_root_path}"]
        print(f"Testing module: {value.name} - {' '.join(call)}")

        process = subprocess.Popen(
            call,
            stdout=slave,
            stderr=slave,
            close_fds=True
        )

        os.close(slave)

        for line in iter(file_obj.readline, b""):
            print(line.decode(), end="")

        process.wait()
        
        break # left until works

    return True


def main() -> int:
    known = load_known_good(Path("../known_good_next.json"))
    run_unit_test(known=known)

    return 0

if __name__ == "__main__":
    main()
