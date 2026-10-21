"""Copied proven five-filter native RGBA decoder plus decoded-byte SHA. No image mutation."""
import struct,zlib,hashlib
def require(condition,message):
    if not condition: raise ValueError(message)

def inspect_rgba_png(data):
    """Decode native 8-bit RGBA PNG pixels using stdlib, including all five filters.

    UE's bundled Python need not contain Pillow. Chunk CRC, pixel extent and alpha
    are checked from the actual file, rather than trusting the artist metadata.
    """
    require(data[:8] == b"\x89PNG\r\n\x1a\n", "Not a PNG")
    offset, header, payload, ended = 8, None, [], False
    while offset + 12 <= len(data):
        length = struct.unpack_from(">I", data, offset)[0]
        kind = data[offset + 4:offset + 8]
        stop = offset + 12 + length
        require(stop <= len(data), "Truncated PNG chunk")
        body = data[offset + 8:offset + 8 + length]
        crc = struct.unpack_from(">I", data, offset + 8 + length)[0]
        require(zlib.crc32(kind + body) & 0xffffffff == crc, "PNG chunk CRC mismatch")
        if header is None:
            require(kind == b"IHDR" and length == 13, "PNG must begin with IHDR")
            header = struct.unpack(">IIBBBBB", body)
            require(header == (512, 512, 8, 6, 0, 0, 0),
                    f"Expected native 512x512 8-bit RGBA/noninterlaced PNG, got {header}")
        elif kind == b"IHDR":
            raise ValueError("Duplicate PNG header")
        elif kind == b"IDAT":
            payload.append(body)
        elif kind == b"IEND":
            require(length == 0 and stop == len(data), "Invalid PNG end or trailing bytes")
            ended = True
            break
        offset = stop
    require(ended and payload, "Incomplete PNG")
    decoder = zlib.decompressobj()
    raw = decoder.decompress(b"".join(payload)) + decoder.flush()
    require(decoder.eof and not decoder.unused_data and not decoder.unconsumed_tail,
            "Invalid PNG zlib stream")
    stride, height = 512 * 4, 512
    require(len(raw) == (stride + 1) * height, "PNG decompressed extent mismatch")
    previous = bytearray(stride)
    minimum, maximum, left, top, right, bottom = 255, 0, 512, 512, -1, -1
    corners = []
    rgba_hash = hashlib.sha256()
    for y in range(height):
        start = y * (stride + 1)
        filtering = raw[start]
        require(0 <= filtering <= 4, "Unknown PNG row filter")
        row = bytearray(raw[start + 1:start + 1 + stride])
        if filtering:
            for i in range(stride):
                a = row[i - 4] if i >= 4 else 0
                b = previous[i]
                c = previous[i - 4] if i >= 4 else 0
                if filtering == 1:
                    predictor = a
                elif filtering == 2:
                    predictor = b
                elif filtering == 3:
                    predictor = (a + b) // 2
                else:
                    p = a + b - c
                    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                    predictor = a if pa <= pb and pa <= pc else b if pb <= pc else c
                row[i] = (row[i] + predictor) & 255
        if y == 0 or y == 511:
            corners.extend((row[3], row[stride - 1]))
        alpha = row[3::4]
        minimum, maximum = min(minimum, min(alpha)), max(maximum, max(alpha))
        nonzero = [x for x, value in enumerate(alpha) if value]
        if nonzero:
            left, top = min(left, nonzero[0]), min(top, y)
            right, bottom = max(right, nonzero[-1]), y
        rgba_hash.update(row)
        previous = row
    return {"rgba_sha256": rgba_hash.hexdigest(), "canvas_px": [512, 512], "mode": "RGBA", "bit_depth": 8,
            "alpha_extrema": [minimum, maximum], "corner_alpha": corners,
            "corners_transparent": corners == [0, 0, 0, 0],
            "bbox_px": [left, top, right + 1, bottom + 1] if right >= 0 else None,
            "nonempty": right >= 0, "canvas_transformed": False}
