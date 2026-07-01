#!/usr/bin/env python3
"""Capture logs from two serial ports (right and left earbuds) into separate and merged files."""

from __future__ import annotations

import argparse
import datetime as dt
import queue
import threading
import time
from pathlib import Path

try:
    import serial
except ImportError as exc:
    raise SystemExit(
        "pyserial is required. Install with: pip install -r tools/loopback_test/requirements.txt"
    ) from exc


class SerialReader(threading.Thread):
    def __init__(
        self,
        port: str,
        baud: int,
        label: str,
        out_queue: "queue.Queue[tuple[str, str, str]]",
        stop_event: threading.Event,
    ) -> None:
        super().__init__(daemon=True)
        self.port = port
        self.baud = baud
        self.label = label
        self.out_queue = out_queue
        self.stop_event = stop_event

    def run(self) -> None:
        try:
            with serial.Serial(self.port, self.baud, timeout=0.2) as ser:
                while not self.stop_event.is_set():
                    raw = ser.readline()
                    if not raw:
                        continue
                    ts = dt.datetime.now().isoformat(timespec="milliseconds")
                    line = raw.decode("utf-8", errors="replace").rstrip("\r\n")
                    self.out_queue.put((ts, self.label, line))
        except serial.SerialException as err:
            ts = dt.datetime.now().isoformat(timespec="milliseconds")
            self.out_queue.put((ts, self.label, f"[SERIAL_ERROR] {err}"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture dual-bud UART logs.")
    parser.add_argument("--right-port", default="COM4", help="Right bud serial port (default: COM4)")
    parser.add_argument("--left-port", default="COM25", help="Left bud serial port (default: COM25)")
    parser.add_argument("--baud", type=int, default=115200, help="UART baud rate (default: 115200)")
    parser.add_argument(
        "--duration",
        type=int,
        default=90,
        help="Capture duration in seconds (default: 90). Use 0 for manual stop.",
    )
    parser.add_argument(
        "--out-dir",
        default="tools/loopback_test/logs",
        help="Output directory for log files",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    merged_path = out_dir / f"loopback_merged_{stamp}.log"
    right_path = out_dir / f"right_{stamp}.log"
    left_path = out_dir / f"left_{stamp}.log"

    print("Starting dual log capture")
    print(f"Right bud: {args.right_port} | Left bud: {args.left_port} | Baud: {args.baud}")
    print(f"Merged log: {merged_path}")

    stop_event = threading.Event()
    out_q: "queue.Queue[tuple[str, str, str]]" = queue.Queue()

    readers = [
        SerialReader(args.right_port, args.baud, "RIGHT", out_q, stop_event),
        SerialReader(args.left_port, args.baud, "LEFT", out_q, stop_event),
    ]

    for reader in readers:
        reader.start()

    start = time.time()
    try:
        with merged_path.open("w", encoding="utf-8") as merged, right_path.open(
            "w", encoding="utf-8"
        ) as right_f, left_path.open("w", encoding="utf-8") as left_f:
            while True:
                if args.duration > 0 and (time.time() - start) >= args.duration:
                    break

                try:
                    ts, label, line = out_q.get(timeout=0.2)
                except queue.Empty:
                    continue

                row = f"{ts} [{label}] {line}\n"
                merged.write(row)
                merged.flush()

                if label == "RIGHT":
                    right_f.write(f"{ts} {line}\n")
                    right_f.flush()
                elif label == "LEFT":
                    left_f.write(f"{ts} {line}\n")
                    left_f.flush()

                print(row, end="")

    except KeyboardInterrupt:
        print("\nCapture interrupted by user")
    finally:
        stop_event.set()
        for reader in readers:
            reader.join(timeout=1.0)

    print("Capture complete")
    print(f"Saved: {merged_path}")
    print(f"Saved: {right_path}")
    print(f"Saved: {left_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
