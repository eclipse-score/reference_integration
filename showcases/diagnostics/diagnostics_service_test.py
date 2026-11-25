# *******************************************************************************
# Copyright (c) 2026 Contributors to the Eclipse Foundation
#
# See the NOTICE file(s) distributed with this work for additional
# information regarding copyright ownership.
#
# This program and the accompanying materials are made available under the
# terms of the Apache License Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0
#
# SPDX-License-Identifier: Apache-2.0
# *******************************************************************************
"""Exercise the check and boot service racing to start diagnostics."""

import http.server
import os
import signal
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

CHECK, SERVICE = (Path(arg).resolve() for arg in sys.argv[1:3])
del sys.argv[1:3]


class DiagnosticsServiceTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.processes = []
        self.ready = threading.Event()
        root = self.root
        ready = self.ready

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                self.respond()

            def do_POST(self):
                self.respond()

            def respond(self):
                if not ready.is_set() or not (root / "starts").exists():
                    self.close_connection = True
                    return
                self.send_response(200)
                self.end_headers()
                if self.path.endswith("authorize"):
                    self.wfile.write(b'{"access_token":"test"}')
                elif self.path.endswith("apps"):
                    self.wfile.write(b'["sovd2uds","score-diagnostics"]')

            def log_message(self, *_args):
                pass

        self.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.cleanup)

        self.write_executable("ip", f'#!/bin/bash\n[[ -f "{root}/network" ]] && echo "2: eth0 inet 192.0.2.1/24"\n')
        self.write_executable("hostname", "#!/bin/bash\nexit 1\n")
        # Use the same open-file-description lock semantics as util-linux flock.
        self.write_executable(
            "flock",
            "#!/usr/bin/env python3\n"
            "import fcntl, sys\n"
            "from pathlib import Path\n"
            f"root = Path({str(root)!r})\n"
            "if '-n' not in sys.argv:\n"
            "    (root / 'blocking-attempt').touch()\n"
            "try:\n"
            "    fcntl.flock(int(sys.argv[-1]), fcntl.LOCK_EX | "
            "(fcntl.LOCK_NB if '-n' in sys.argv else 0))\n"
            "except BlockingIOError:\n"
            "    sys.exit(75)\n"
            "(root / 'locked').touch()\n",
        )
        self.write_executable(
            "manager",
            f'#!/bin/bash\necho "$$" >> "{root}/starts"\ntrap \'exit 0\' TERM INT\nwhile :; do sleep 0.1; done\n',
        )
        service = SERVICE.read_text().replace("/showcases/data/diagnostics", str(root))
        service = service.replace("/run/score-diagnostics.lock", str(root / "lock"))
        service = service.replace("/usr/bin/launch_manager", str(root / "manager"))
        self.write_executable("service.sh", service)
        check = CHECK.read_text().replace("/showcases/data/diagnostics", str(root))
        check = check.replace("7690", str(self.server.server_port))
        self.write_executable("check.sh", check)
        self.env = os.environ.copy()
        self.env["PATH"] = f"{root}:{self.env['PATH']}"

    def write_executable(self, name, content):
        path = self.root / name
        path.write_text(content)
        path.chmod(0o755)

    def start(self, name):
        output = self.root / f"{name}-{len(self.processes)}.log"
        with output.open("w") as log:
            process = subprocess.Popen([str(self.root / name)], stdout=log, stderr=subprocess.STDOUT, env=self.env)
        self.processes.append(process)
        return process, output

    def wait_for(self, condition, message):
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            if condition():
                return
            time.sleep(0.05)
        self.fail(message)

    def starts(self):
        path = self.root / "starts"
        return path.read_text().splitlines() if path.exists() else []

    def cleanup(self):
        for process in reversed(self.processes):
            if process.poll() is None:
                process.send_signal(signal.SIGTERM)
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.temp.cleanup()

    def test_check_waits_for_boot_service_before_network(self):
        boot, _ = self.start("service.sh")
        self.wait_for(lambda: (self.root / "locked").exists(), "boot service did not acquire the lock")
        check, output = self.start("check.sh")
        self.wait_for(
            lambda: "waiting for the existing" in output.read_text(),
            "check did not join the boot service",
        )
        assert self.starts() == []
        (self.root / "network").touch()
        self.ready.set()
        assert check.wait(timeout=15) == 0, output.read_text()
        assert boot.poll() is None, "check stopped the boot service"
        assert len(self.starts()) == 1

    def test_boot_waits_for_check_owned_service(self):
        (self.root / "network").touch()
        check, output = self.start("check.sh")
        self.wait_for(lambda: len(self.starts()) == 1, "check did not start a manager")
        boot, _ = self.start("service.sh")
        self.wait_for(lambda: (self.root / "blocking-attempt").exists(), "boot did not attempt the lock")
        assert len(self.starts()) == 1, "boot started a second manager"
        self.ready.set()
        assert check.wait(timeout=15) == 0, output.read_text()
        self.wait_for(lambda: len(self.starts()) == 2, "boot did not acquire the released lock")
        assert boot.poll() is None


if __name__ == "__main__":
    unittest.main()
