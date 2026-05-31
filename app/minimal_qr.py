"""Minimal QR Code generator - pure Python, zero dependencies.

Generates QR code (version 1-7, numeric/alphanumeric/byte mode).
Based on the QR code specification (ISO/IEC 18004).
"""

from typing import List, Tuple, Optional

# ─── Galois Field tables for Reed-Solomon error correction ──────────────────

# GF(256) with primitive polynomial x^8 + x^4 + x^3 + x^2 + 1 (0x11d)
GF_EXP = [0] * 512
GF_LOG = [0] * 256

def _init_gf():
    x = 1
    for i in range(255):
        GF_EXP[i] = x
        GF_LOG[x] = i
        x = (x << 1) ^ (0x11d if (x >> 7) & 1 else 0)
    for i in range(255, 512):
        GF_EXP[i] = GF_EXP[i - 255]

_init_gf()


def _gf_mul(a: int, b: int) -> int:
    if a == 0 or b == 0:
        return 0
    return GF_EXP[GF_LOG[a] + GF_LOG[b]]


def _rs_generator_poly(num_ec: int) -> List[int]:
    """Generate RS generator polynomial of degree num_ec."""
    g = [1]
    for i in range(num_ec):
        # Multiply by (x + α^i)
        g2 = [0] * (len(g) + 1)
        for j, coeff in enumerate(g):
            g2[j] ^= _gf_mul(coeff, GF_EXP[i])
            g2[j + 1] ^= coeff
        g = g2
    return g


def _rs_encode(msg: List[int], num_ec: int) -> List[int]:
    """Encode message with Reed-Solomon error correction."""
    gen = _rs_generator_poly(num_ec)
    remainder = [0] * num_ec
    for byte in msg:
        factor = byte ^ remainder[0]
        remainder = remainder[1:] + [0]
        for i, coeff in enumerate(gen[1:]):
            remainder[i] ^= _gf_mul(coeff, factor) if coeff else 0
    return msg + remainder


# ─── QR Code data encoding ──────────────────────────────────────────────────

MODE_NUMERIC = 1
MODE_ALPHANUM = 2
MODE_BYTE = 4

ALPHANUM_TABLE = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:"


def _encode_numeric(data: str) -> List[int]:
    bits = ""
    i = 0
    while i < len(data):
        chunk = data[i:i+3]
        n = int(chunk)
        bits += format(n, "0{}b".format(10 if len(chunk) == 1 else 7 if len(chunk) == 2 else 10))
        i += len(chunk)
    return bits


def _encode_alphanum(data: str) -> List[int]:
    bits = ""
    i = 0
    while i < len(data):
        if i + 1 < len(data):
            v = ALPHANUM_TABLE.index(data[i]) * 45 + ALPHANUM_TABLE.index(data[i + 1])
            bits += format(v, "011b")
            i += 2
        else:
            v = ALPHANUM_TABLE.index(data[i])
            bits += format(v, "06b")
            i += 1
    return bits


def _encode_byte(data: str) -> str:
    encoded = data.encode("iso-8859-1")
    return "".join(format(b, "08b") for b in encoded)


def _get_mode(data: str) -> int:
    if data.isdigit():
        return MODE_NUMERIC
    if all(c in ALPHANUM_TABLE for c in data):
        return MODE_ALPHANUM
    return MODE_BYTE


# ─── Version and capacity tables (versions 1-7) ────────────────────────────

# Format: (version, total_data_codewords, ec_codewords_per_block, num_blocks, data_codewords_per_block)
# For error correction level M (15% recovery)
VERSION_INFO = {
    1:  (26, 10, 1, 16),
    2:  (44, 16, 1, 28),
    3:  (70, 26, 1, 44),
    4:  (100, 18, 2, 32),
    5:  (134, 24, 2, 43),
    6:  (172, 16, 4, 27),
    7:  (196, 20, 4, 33),
}

# Character count indicator lengths: (numeric, alphanum, byte)
CHAR_COUNT_LENS = {1: (10, 9, 8), 2: (12, 11, 16), 3: (12, 11, 16),
                   4: (12, 11, 16), 5: (12, 11, 16), 6: (12, 11, 16), 7: (12, 11, 16)}

# ─── Data placement matrix ──────────────────────────────────────────────────

# Mask patterns
def _mask0(r, c): return (r + c) % 2 == 0
def _mask1(r, c): return r % 2 == 0
def _mask2(r, c): return c % 3 == 0
def _mask3(r, c): return (r + c) % 3 == 0
def _mask4(r, c): return (r // 2 + c // 3) % 2 == 0
def _mask5(r, c): return (r * c) % 2 + (r * c) % 3 == 0
def _mask6(r, c): return ((r * c) % 2 + (r * c) % 3) % 2 == 0
def _mask7(r, c): return ((r + c) % 2 + (r * c) % 3) % 2 == 0

MASKS = [_mask0, _mask1, _mask2, _mask3, _mask4, _mask5, _mask6, _mask7]

# Format info for error correction level M + mask
# Precomputed: EC level M indicator bits = 00
FORMAT_INFO = [
    [0x5c, 0x5d, 0x5e, 0x5f],  # EC level L
    [0x5c, 0x5d, 0x5e, 0x5f],  # placeholder
]

# ─── Main QR Code class ────────────────────────────────────────────────────

class MinimalQR:
    def __init__(self, data: str):
        self.data = data
        self.mode = _get_mode(data)
        self._build()

    def _select_version(self, data_bits: str) -> int:
        for ver in range(1, 8):
            total_cw, ec_per_block, num_blocks, data_per_block = VERSION_INFO[ver]
            total_data_bits = data_per_block * num_blocks * 8
            if len(data_bits) <= total_data_bits:
                return ver
        raise ValueError("Data too long for QR code (max version 7)")

    def _build(self):
        # 1. Encode data
        mode = self.mode
        # For simplicity, we auto-detect and handle byte mode for any non-trivial data
        if not self.data.isdigit() and not all(c in ALPHANUM_TABLE for c in self.data):
            mode = MODE_BYTE

        if mode == MODE_NUMERIC:
            data_bits = _encode_numeric(self.data)
            mode_bits = "0001"
        elif mode == MODE_ALPHANUM:
            data_bits = _encode_alphanum(self.data)
            mode_bits = "0010"
        else:
            data_bits = _encode_byte(self.data)
            mode_bits = "0100"

        # 2. Determine version
        self.version = self._select_version(data_bits)
        total_cw, ec_per_block, num_blocks, data_per_block = VERSION_INFO[self.version]
        # 3. Add mode and character count indicator
        cc_len = CHAR_COUNT_LENS[self.version][{1: 0, 2: 1, 4: 2}[mode]]

        cc_bits = format(len(self.data), f"0{cc_len}b")
        bitstream = mode_bits + cc_bits + data_bits

        # 4. Terminator and padding
        total_data_bits = data_per_block * num_blocks * 8
        bitstream += "0000"  # Terminator
        bitstream = bitstream[:total_data_bits].ljust(total_data_bits, "0")

        # Add padding bytes if needed
        while len(bitstream) < total_data_bits:
            bitstream += "11101100" if len(bitstream) % 16 == 0 else "00010001"

        bitstream = bitstream[:total_data_bits]

        # 5. Convert to bytes
        data_bytes = [int(bitstream[i:i+8], 2) for i in range(0, len(bitstream), 8)]

        # 6. Split into blocks and add EC
        block_size = len(data_bytes) // num_blocks if num_blocks > 1 else len(data_bytes)
        all_blocks = []
        for i in range(num_blocks):
            start = i * block_size
            end = start + block_size if i < num_blocks - 1 else len(data_bytes)
            block = data_bytes[start:end]
            encoded = _rs_encode(block, ec_per_block)
            all_blocks.append(encoded)

        # 7. Interleave data and EC bytes
        final_bytes = []
        max_data_len = max(len(b) - ec_per_block for b in all_blocks)
        for i in range(max_data_len):
            for block in all_blocks:
                if i < len(block) - ec_per_block:
                    final_bytes.append(block[i])

        for i in range(ec_per_block):
            for block in all_blocks:
                final_bytes.append(block[-(ec_per_block - i)])

        # 8. Build matrix
        self._build_matrix(final_bytes)
        self._apply_mask()

    def _build_matrix(self, data: List[int]):
        n = 21 + 4 * (self.version - 1)  # Module count
        self.size = n
        self.matrix = [[0] * n for _ in range(n)]

        # Add finder patterns (3 corners)
        self._add_finder_pattern(0, 0)
        self._add_finder_pattern(n - 7, 0)
        self._add_finder_pattern(0, n - 7)

        # Add timing patterns
        for i in range(8, n - 8):
            self.matrix[6][i] = 1 if i % 2 == 0 else 0
            self.matrix[i][6] = 1 if i % 2 == 0 else 0

        # Add dark module
        self.matrix[n - 8][8] = 1

        # Place data bits
        self.reserved = [[False] * n for _ in range(n)]
        self._mark_reserved()

        self._place_data(data)

    def _add_finder_pattern(self, row: int, col: int):
        """Add a 7x7 finder pattern at (row, col)."""
        for r in range(7):
            for c in range(7):
                if (r == 0 or r == 6 or c == 0 or c == 6 or
                    (2 <= r <= 4 and 2 <= c <= 4)):
                    self.matrix[row + r][col + c] = 1
                else:
                    self.matrix[row + r][col + c] = 0

        # Separator (white border around finder pattern)
        for i in range(-1, 8):
            if 0 <= row - 1 < self.size and 0 <= col + i < self.size:
                self.matrix[row - 1][col + i] = 0
            if 0 <= row + 7 < self.size and 0 <= col + i < self.size:
                self.matrix[row + 7][col + i] = 0
            if 0 <= row + i < self.size and 0 <= col - 1 < self.size:
                self.matrix[row + i][col - 1] = 0
            if 0 <= row + i < self.size and 0 <= col + 7 < self.size:
                self.matrix[row + i][col + 7] = 0

    def _mark_reserved(self):
        """Mark reserved areas (finder patterns, timing, format info)."""
        n = self.size

        # Finder patterns and separators
        for r, c in [(0, 0), (n - 7, 0), (0, n - 7)]:
            for dr in range(-1, 8):
                for dc in range(-1, 8):
                    if 0 <= r + dr < n and 0 <= c + dc < n:
                        self.reserved[r + dr][c + dc] = True

        # Timing patterns
        for i in range(n):
            self.reserved[6][i] = True
            self.reserved[i][6] = True

        # Format info areas
        for i in range(9):
            self.reserved[8][i] = True if i != 6 else False
            self.reserved[i][8] = True
            if n - 1 - i >= 0:
                self.reserved[8][n - 1 - i] = True
                self.reserved[n - 1 - i][8] = True
        self.reserved[8][8] = False
        self.reserved[8][n - 8] = True
        self.reserved[n - 8][8] = True

        # Version info (for version 7+)
        if self.version >= 7:
            for dr in range(3):
                for dc in range(6):
                    self.reserved[n - 11 + dr][dc] = True
                    self.reserved[dc][n - 11 + dr] = True

    def _place_data(self, data: List[int]):
        """Place encoded data bits into the matrix."""
        n = self.size
        bit_index = 0
        max_bits = len(data) * 8

        # Zigzag pattern: start from bottom-right, move left
        col = n - 1
        row = n - 1
        direction = -1  # -1 = up, 1 = down

        while col > 0:
            if col == 6:  # Skip timing pattern
                col -= 1
                continue

            # Process two columns at a time
            for _ in range(2):
                if self._can_place(row, col):
                    if bit_index < max_bits:
                        byte_idx = bit_index // 8
                        bit_idx = 7 - (bit_index % 8)
                        val = (data[byte_idx] >> bit_idx) & 1
                        self.matrix[row][col] = val
                    bit_index += 1
                col -= 1
            col += 2  # Reset column for vertical traversal

            # Move up or down
            next_row = row + direction
            if next_row < 0 or next_row >= n:
                direction *= -1
                col -= 2
                if col == 6:
                    col -= 1
            else:
                row = next_row

    def _can_place(self, row: int, col: int) -> bool:
        return (0 <= row < self.size and 0 <= col < self.size
                and not self.reserved[row][col])

    def _apply_mask(self):
        """Apply best mask pattern."""
        n = self.size
        best_score = float("inf")
        best_matrix = None

        for mask_idx, mask_fn in enumerate(MASKS[:8]):
            temp = [row[:] for row in self.matrix]
            for r in range(n):
                for c in range(n):
                    if not self.reserved[r][c] and mask_fn(r, c):
                        temp[r][c] ^= 1

            # Add format information
            self._add_format_info(temp, mask_idx)

            score = self._evaluate_penalty(temp)
            if score < best_score:
                best_score = score
                best_matrix = temp

        self.matrix = best_matrix if best_matrix else self.matrix

    def _add_format_info(self, matrix, mask_idx: int):
        """Add format info bits (EC level M = 0b00)."""
        n = self.size
        # Format info for EC level M (00) and mask index
        # Precomputed values
        format_bits = [
            0x5412, 0x5125, 0x5E7C, 0x5B4B,
            0x45F9, 0x40CE, 0x4F97, 0x4AA0,
        ]

        bits = format_bits[mask_idx]

        # Place format bits
        for i in range(15):
            bit = (bits >> (14 - i)) & 1

            # Top-left corner: horizontal
            if i < 6:
                matrix[8][i] = bit
            elif i == 6:
                matrix[8][7] = bit  # Skip timing pattern
            elif i == 7:
                matrix[8][8] = bit
            elif i == 8:
                matrix[7][8] = bit
            else:
                matrix[14 - i][8] = bit

            # Bottom-left / top-right corner
            if i < 6:
                matrix[n - 1 - i][8] = bit
            elif i == 8:
                matrix[8][n - 8] = bit
            elif i < 14:
                matrix[8][n - 15 + i] = bit

        # Dark module (position (n-8, 8))
        matrix[n - 8][8] = 1

    def _evaluate_penalty(self, matrix) -> int:
        """Evaluate mask penalty score (lower is better)."""
        n = self.size
        score = 0

        # Penalty 1: Adjacent modules in rows/columns
        for r in range(n):
            count = 1
            for c in range(1, n):
                if matrix[r][c] == matrix[r][c - 1]:
                    count += 1
                else:
                    if count >= 5:
                        score += count + 2
                    count = 1
            if count >= 5:
                score += count + 2

        for c in range(n):
            count = 1
            for r in range(1, n):
                if matrix[r][c] == matrix[r - 1][c]:
                    count += 1
                else:
                    if count >= 5:
                        score += count + 2
                    count = 1
            if count >= 5:
                score += count + 2

        # Penalty 2: 2x2 blocks
        for r in range(n - 1):
            for c in range(n - 1):
                if (matrix[r][c] == matrix[r][c + 1] ==
                    matrix[r + 1][c] == matrix[r + 1][c + 1]):
                    score += 3

        # Penalty 3: 1011101 or 0101110 patterns
        pattern1 = [1, 0, 1, 1, 1, 0, 1]
        pattern2 = [0, 1, 0, 0, 0, 1, 0]

        for r in range(n):
            for c in range(n - 6):
                row_slice = matrix[r][c:c+7]
                if row_slice == pattern1 or row_slice == pattern2:
                    score += 40
                col_slice = [matrix[i][c] for i in range(r, min(r + 7, n))]
                if len(col_slice) == 7 and (col_slice == pattern1 or col_slice == pattern2):
                    score += 40

        # Penalty 4: Balance of dark/light modules
        dark = sum(sum(row) for row in matrix)
        total = n * n
        percent = (dark * 100) // total
        prev = percent - (percent % 5)
        next_val = prev + 5
        score += min(abs(prev - 50) // 5, abs(next_val - 50) // 5) * 10

        return score

    def get_matrix(self) -> List[List[int]]:
        return self.matrix
