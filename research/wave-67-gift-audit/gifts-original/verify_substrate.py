import struct
# Strict Structural Constants matching the C-compatible Macro specs
WIDTH = 80
HEIGHT = 24
HEADER_BYTES = 16
GRID_BYTES = WIDTH * HEIGHT * 4  # 1920 cells * 4 bytes each = 7680 bytes
EXPECTED_TOTAL_BYTES = HEADER_BYTES + GRID_BYTES  # Exactly 7696 bytes

def generate_proven_frame():
    """
    Constructs a raw, memory-aligned binary frame simulating a live host matrix.
    Packs header metrics and bit-packed cell arrays directly into raw bytes.
    """
    # 1. Pack the 16-byte fixed alignment header: [u32 tick, u32 primary, u32 secondary, u32 padding]
    tick = 42
    primary_metric = 115     # e.g., NMEA Heading or Core Engine Load
    secondary_metric = 5     # e.g., Operational System Depth Limit
    padding_word = 0

    binary_frame = bytearray(struct.pack("<IIII", tick, primary_metric, secondary_metric, padding_word))

    # 2. Pack the 7680-byte visual grid matrix sequentially into memory
    for y in range(HEIGHT):
        for x in range(WIDTH):
            # Define specific cell test coordinates at Row 21, Column 10
            if y == 21 and x == 10:
                glyph = ord('~')      # Symbol code 126
                color_tag = 2         # Mapped to Cyan Shader Channel index
                weight = 200          # High-intensity signal weight
                flags = 1             # Active structural configuration bit flag
                buzz_variance = 8     # Experiential dissonance magnitude (0-15)
            else:
                # Baseline background field noise values
                glyph = 32; color_tag = 0; weight = 0; flags = 0; buzz_variance = 0

            packed_word = (
                (glyph & 0xFF) |
                ((color_tag & 0xFF) << 8) |
                ((weight & 0xFF) << 16) |
                ((flags & 0x0F) << 24) |
                ((buzz_variance & 0x0F) << 28)
            )
            binary_frame.extend(struct.pack("<I", packed_word))

    return bytes(binary_frame)

def execute_unmarshalling_proof(frame_bytes):
    """
    Simulates the unmanaged memory parsing pass performed by the GPU shaders.
    Extracts raw fields using bitwise shifts to verify complete structural accuracy.
    """
    print("========================================================================")
    print("[SUBSTRATE EMBODIMENT PROOF]")
    print("========================================================================")

    actual_size = len(frame_bytes)
    print(f" -> Target Structural Size  : {EXPECTED_TOTAL_BYTES} bytes")
    print(f" -> Allocated Frame Output  : {actual_size} bytes")
    assert actual_size == EXPECTED_TOTAL_BYTES, "CRITICAL DETACHMENT: Frame size mismatch."
    print(" -> Boundary Constraint Verification: PASS [Byte-Perfect Alignment Match]\n")

    header_slice = frame_bytes[0:16]
    tick, primary, secondary, pad = struct.unpack("<IIII", header_slice)

    print("─── HEADER UNMARSHAL PASS ──────────────────────────────────────────────")
    print(f" * Unpacked Frame System Tick     : {tick}")
    print(f" * Unpacked Primary System Metric : {primary}")
    print(f" * Unpacked Secondary Metric      : {secondary}")
    print(f" * Alignment Padding Word Context : 0x{pad:08X}")

    target_row = 21
    target_col = 10
    cell_offset = HEADER_BYTES + ((target_row * WIDTH) + target_col) * 4

    cell_bytes = frame_bytes[cell_offset:cell_offset+4]
    raw_word = struct.unpack("<I", cell_bytes)[0]

    unpacked_glyph = raw_word & 0xFF
    unpacked_color = (raw_word >> 8) & 0xFF
    unpacked_weight = (raw_word >> 16) & 0xFF
    unpacked_flags = (raw_word >> 24) & 0x0F
    unpacked_buzz = (raw_word >> 28) & 0x0F

    print(f"\n─── CELL DECONVOLUTION PASS (Row {target_row}, Col {target_col}, Offset: Byte {cell_offset}) ───")
    print(f" * Raw 32-bit Word Ingested : 0x{raw_word:08X}")
    print(f" * Extracted Glyph Symbol   : '{chr(unpacked_glyph)}' (Code {unpacked_glyph})")
    print(f" * Extracted Color Tag Index: {unpacked_color}")
    print(f" * Extracted Signal Weight  : {unpacked_weight} / 255")
    print(f" * Extracted Invariant Flag : {unpacked_flags}")
    print(f" * Extracted Sub-Symbolic Buzz: {unpacked_buzz} / 15")
    print("========================================================================")

if __name__ == "__main__":
    frame = generate_proven_frame()
    execute_unmarshalling_proof(frame)
