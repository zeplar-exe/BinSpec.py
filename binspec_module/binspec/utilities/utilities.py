import math


def bits_to_bytes(bits: list[int], *, big_endian: bool=True) -> bytes:
  byte_count = math.ceil(len(bits) / 8)
  b = bytearray()

  if not big_endian:
    bits = list(reversed(bits))
  
  for i in range(0, byte_count * 8, 8):
    byte = 0

    for j in range(8):
      byte <<= 1
      
      if (i + j) >= len(bits):
        # this is a theoretically impossible edge case
        break # break out because we don't have any bits left 
      else:
        if bits[i + j] == 0:
          pass # bit shift adds the zero
        else:
          byte |= 1

        if (i + j + 1) >= len(bits):
          break # avoid extra bit shift since this is the last bit
    
    b.append(byte)

  if byte_count > 1 and (len(bits) % 8) != 0: # this whole section shifts everything to the right to remove the trailing zeros on the most significant byte
    excess_count = len(bits) % 8
    b[-1] <<= excess_count

    create_pairs = lambda l: ((l[i], l[i + 1], i, i + 1) for i in range(len(l) - 1)) # adjacent pairwise from list
    shifted_b = bytearray(len(b))

    for byte_right, byte_left, byte_right_index, byte_left_index in create_pairs(list(reversed(b))):
      for i in range(excess_count):
        byte_right >>= 1

        if (byte_left & 1) != 0:
          byte_right |= 128

        byte_left >>= 1
      
      shifted_b[byte_right_index] = byte_right
      shifted_b[byte_left_index] = byte_left
  
    b = bytearray(reversed(shifted_b))
  
  return bytes(b)

def bits_to_int(bits: list[int], *, big_endian: bool=True) -> int:
  b = bits_to_bytes(bits, big_endian=big_endian)
  n = int.from_bytes(b, byteorder="big")

  return n