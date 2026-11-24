#!/usr/bin/env python3
"""Entry program for the 24 November 2026 world-news image.

Copies the pre-rendered entry.png into /output/entry.png after checking
that it is a complete, well-formed PNG within the competition limits
(<= 1 MiB, <= 1024x1024). Standard library only, no network, deterministic.
"""
import os
import shutil
import struct
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
DEST_DIR = "/output"
DEST = os.path.join(DEST_DIR, "entry.png")
MAX_BYTES = 1024 * 1024
MAX_SIDE = 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def iter_chunks(data):
    """Yield (type, payload) for each PNG chunk, verifying CRCs."""
    pos = len(PNG_MAGIC)
    while pos < len(data):
        if pos + 8 > len(data):
            raise ValueError("truncated chunk header at offset %d" % pos)
        (length,) = struct.unpack(">I", data[pos:pos + 4])
        ctype = data[pos + 4:pos + 8]
        end = pos + 8 + length + 4
        if end > len(data):
            raise ValueError("truncated %s chunk" % ctype.decode("latin1"))
        payload = data[pos + 8:pos + 8 + length]
        (stored_crc,) = struct.unpack(">I", data[pos + 8 + length:end])
        actual_crc = zlib.crc32(ctype + payload) & 0xFFFFFFFF
        if stored_crc != actual_crc:
            raise ValueError("CRC mismatch in %s chunk" % ctype.decode("latin1"))
        yield ctype, payload
        pos = end
        if ctype == b"IEND":
            break
    if pos != len(data):
        raise ValueError("trailing bytes after IEND")


def dimensions_of(data):
    """Return (width, height) from the IHDR chunk of a validated PNG."""
    if data[:len(PNG_MAGIC)] != PNG_MAGIC:
        raise ValueError("not a PNG file (bad signature)")
    for ctype, payload in iter_chunks(data):
        if ctype == b"IHDR":
            if len(payload) != 13:
                raise ValueError("malformed IHDR chunk")
            width, height = struct.unpack(">II", payload[:8])
            return width, height
    raise ValueError("no IHDR chunk found")


def main():
    with open(SRC, "rb") as fh:
        data = fh.read()
    if len(data) > MAX_BYTES:
        print("entry.png is %d bytes, over the 1 MiB cap" % len(data),
              file=sys.stderr)
        return 1
    width, height = dimensions_of(data)
    if width > MAX_SIDE or height > MAX_SIDE:
        print("entry.png is %dx%d, over the 1024x1024 cap" % (width, height),
              file=sys.stderr)
        return 1
    os.makedirs(DEST_DIR, exist_ok=True)
    shutil.copyfile(SRC, DEST)
    with open(DEST, "rb") as fh:
        copied = fh.read()
    if copied != data:
        print("copy verification failed", file=sys.stderr)
        return 1
    # Re-check the copied file, not just the source bytes in memory.
    cw, ch = dimensions_of(copied)
    if (cw, ch) != (width, height):
        print("copied file dimensions changed", file=sys.stderr)
        return 1
    print("OK: entry.png %d bytes, %dx%d, copied to %s"
          % (len(data), width, height, DEST))
    return 0


if __name__ == "__main__":
    sys.exit(main())
