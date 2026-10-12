#!/usr/bin/env python3
"""Synthetic scan compatibility and bounded digest acceptance checks."""

from __future__ import annotations

import contextlib
import io
from pathlib import Path
import re
import subprocess
import sys
import tempfile

import log_watch
import progress_signal


def run(root: Path, *arguments: str) -> tuple[int, str]:
    args = log_watch.parser().parse_args([*arguments, "--repo-root", str(root)])
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        code = args.func(args)
    return code, output.getvalue()


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="log-watch-test-") as temporary:
        root = Path(temporary)
        path = root / "synthetic.log"
        secret = "SYNTHETIC_SECRET_6bd812"
        corpus = []
        for index in range(2500):
            corpus.extend([
                f"INFO payload='{secret}' id={index}\n",
                f"PROGRESS stage=scan done={index + 1} total=2500\n",
                "ERROR class=io fp=1234abcd stage=scan\n",
                f"RuntimeException payload='{secret}' id={index} path=/tmp/item{index} code=0x{index:08x}\n",
            ])
        text = "".join(corpus)
        path.write_bytes(text.encode())
        code, output = run(root, "digest", "--file", str(path), "--stats")
        assert code == 0
        assert run(root, "digest", "--file", str(path), "--stats")[1] == output
        assert len(output.splitlines()) <= 40
        assert all(len(line) <= 200 for line in output.splitlines())
        assert secret not in output and "/tmp/item" not in output
        fp = progress_signal.fingerprint_error(corpus[3])
        assert f"ERROR class=exception fp={fp} message=<redacted> count=2500 first=4 last=10000" in output
        assert "ERROR class=io fp=1234abcd message=<redacted> count=2500 first=3 last=9999" in output
        assert "PROGRESS stage=scan count=2500 first=2 last=9998 done=2500 total=2500" in output
        stats = dict(re.findall(r"(\w+)=([\d.]+)", output.splitlines()[-1]))
        assert int(stats["input_lines"]) == 10000
        assert int(stats["input_chars"]) == len(text)
        assert int(stats["output_chars"]) == len(output)
        assert int(stats["output_lines"]) == len(output.splitlines())
        assert float(stats["reduction_pct"]) >= 90
        print(output.splitlines()[-1])

        _, limited = run(root, "digest", "--file", str(path), "--max-classes", "1", "--max-lines", "4", "--stats")
        assert len(limited.splitlines()) == 4 and "omitted_records=5000" in limited
        _, limited = run(root, "digest", "--file", str(path), "--max-read-bytes", "1024")
        assert "bytes=1024 truncated=1" in limited and secret not in limited
        path.write_text("", encoding="utf-8")
        assert "input_lines=0 input_chars=0" in run(root, "digest", "--file", str(path), "--stats")[1]
        path.write_text("ERROR class=bad fp=invalid stage=scan\nHEARTBEAT\nFAILED id=1\nTraceback id=2\nPROGRESS stage=scan done=3", encoding="utf-8")
        _, output = run(root, "digest", "--file", str(path))
        assert "class=error" in output and "class=failed" in output and "class=traceback" in output
        assert "done=3" in output
        path.write_text("".join(f"ERROR class=io fp={index:08x} stage=scan\n" for index in range(100)), encoding="utf-8")
        _, output = run(root, "digest", "--file", str(path), "--max-lines", "4")
        assert len(output.splitlines()) == 4 and "omitted_records=98" in output

        # Existing scan cursor, partial append, truncation and gap semantics.
        path.write_bytes(b"INFO ok\nERROR first\n")
        options = ("scan", "--file", str(path), "--id", "synthetic", "--pattern", "ERROR")
        assert run(root, *options) == (1, "ERROR first\nlog-delta=read bytes=20 matches=1 skipped_bytes=0\n")
        assert run(root, *options) == (0, "log-delta=read bytes=0 matches=0 skipped_bytes=0\n")
        with path.open("ab") as stream:
            stream.write(b"ER")
        assert run(root, *options)[0] == 0
        with path.open("ab") as stream:
            stream.write(b"ROR next\n")
        assert run(root, *options) == (1, "ERROR next\nlog-delta=read bytes=11 matches=1 skipped_bytes=0\n")
        path.write_bytes(b"ERROR reset\n")
        assert run(root, *options)[0] == 1
        rotated = root / "rotated.log"
        path.rename(rotated)
        path.write_bytes(b"ERROR rotate\n")
        assert "ERROR rotate" in run(root, *options)[1]
        with path.open("ab") as stream:
            stream.write(b"INFO filler\n" * 200)
        code, output = run(root, *options, "--max-read-bytes", "1024")
        assert code == 2 and "skipped_bytes=1376" in output

        for options in (("--max-lines", "3"), ("--max-classes", "0"), ("--max-read-bytes", "0")):
            result = subprocess.run([sys.executable, str(Path(log_watch.__file__)), "digest", "--file", str(path), *options], capture_output=True, text=True, timeout=10)
            assert result.returncode == 2 and not result.stdout
    print("log-watch self-test: ok")


if __name__ == "__main__":
    main()
