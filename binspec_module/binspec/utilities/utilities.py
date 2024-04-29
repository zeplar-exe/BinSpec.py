import math


def bits_to_bytes(bits: bytes, *, big_endian: bool=True) -> bytes:
  """**This function expects a bytes object where each byte represents a single bit. It is primarily meant to be used when implementing a :class:`SpecType`'s parse method.
  
  Arguments
  :param bits: bytes object of bits to convert. 
  
  Keyword Arguments
  :param big_endian: Flag whether to create a big endian :class:`bytes` object.
  
  :return: A :class:`bytes` containing the given bits as if they were compressed."""
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


def bits_to_int(bits: bytes, *, big_endian: bool=True) -> int:
  """**This function expects a bytes object where each byte represents a single bit. It is primarily meant to be used when implementing a :class:`SpecType`'s parse method.
  
  Arguments
  :param bits: bytes object of bits to convert to an integer. 
  
  Keyword Arguments
  :param big_endian: Flag whether to read the given bits in big endian or little endian order.
  
  :return: An n-bit integer from the given bits."""
  b = bits_to_bytes(bits, big_endian=big_endian)
  n = int.from_bytes(b, byteorder="big")

  return n