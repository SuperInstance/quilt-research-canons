import struct
WIDTH = 80
HEIGHT = 24
HEADER_SIZE = 16
CELLS_COUNT = WIDTH * HEIGHT
CELL_SIZE = 4
TOTAL_GRID_BYTES = CELLS_COUNT * CELL_SIZE
EXPECTED_TOTAL_SIZE = HEADER_SIZE + TOTAL_GRID_BYTES

def prove_memory_layout():
    frame_tick = 42
    primary_metric = 115
    secondary_metric = 5
    padding_word = 0

    header_bytes = struct.pack("<IIII", frame_tick, primary_metric, secondary_metric, padding_word)
    grid_bytes = bytearray()

    for row in range(HEIGHT):
        for col in range(WIDTH):
            symbol = ord('X') if row < 20 else ord('~')
            color_tag = 12 if row < 20 else 2
            weight = 200
            flags = 1
            buzz_variance = 8 if row >= 20 else 0

            packed_word = (symbol) | (color_tag << 8) | (weight << 16) | ((flags & 0x0F) << 24) | ((buzz_variance & 0x0F) << 28)
            grid_bytes.extend(struct.pack("<I", packed_word))

    total_payload = header_bytes + grid_bytes

    unmarshalled_header = struct.unpack("<IIII", total_payload[0:16])
    cell_offset = 16 + (21 * WIDTH * 4)
    target_cell_bytes = total_payload[cell_offset:cell_offset+4]
    unmarshalled_cell_word = struct.unpack("<I", target_cell_bytes)[0]

    extracted_symbol = unmarshalled_cell_word & 0xFF
    extracted_color = (unmarshalled_cell_word >> 8) & 0xFF
    extracted_weight = (unmarshalled_cell_word >> 16) & 0xFF
    extracted_flags = (unmarshalled_cell_word >> 24) & 0x0F
    extracted_buzz = (unmarshalled_cell_word >> 28) & 0x0F

    return len(total_payload), EXPECTED_TOTAL_SIZE, unmarshalled_header, chr(extracted_symbol), extracted_color, extracted_weight, extracted_flags, extracted_buzz

payload_len, expected_len, header, symbol, color, weight, flags, buzz = prove_memory_layout()
print(f"Payload Size Match: {payload_len == expected_len} ({payload_len} bytes)")
print(f"Header: {header}")
print(f"Cell Row 21 -> Symbol: {symbol}, Color: {color}, Weight: {weight}, Flags: {flags}, Buzz: {buzz}")
