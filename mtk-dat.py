#!/usr/bin/env python

import os
import struct

FILE_HEADER = 0x4D544B2D
FILE = "mtkwlan.dat"
OUTPUT_DIR = "output"

class MTKFile:
    file_name: str
    data_offset: int
    size: int

def get_file_header(file):
    file.seek(0)
    return struct.unpack('<I', file.read(4))[0]

def read_from_offset(file, offset, size):
    file.seek(offset)
    return struct.unpack('<I', file.read(size))[0]

def read_string_from_offset(file, offset):
    file.seek(offset)
    string_bytes = bytearray()
    while True:
        byte = file.read(1)
        if byte == b'\x00' or byte == b'':
            break
        string_bytes.extend(byte)
    return string_bytes.decode('ascii')

def dump_file(file, offset, size, file_name):
    file.seek(offset)
    with open(f"{OUTPUT_DIR}/{file_name}", "wb") as output_file:
        output_file.write(file.read(size))

def get_file_size(file):
    file.seek(0, os.SEEK_END)
    return file.tell()

files = []

def main():
    with open(FILE, "rb") as file:
        file_size = get_file_size(file)
        file_header = get_file_header(file)
        print(f"File: {FILE}")
        print(f"Size: {file_size} bytes")
        print(f"Header: 0x{file_header:08X}")

        if file_header == FILE_HEADER:
            print("Header is correct")

        section_start_offset = 0x4
        section_size = 76 # Size of each section
        print(f"Section Size: {section_size} bytes")
        current_offset = section_start_offset

        header_section = 0x504
        while current_offset < header_section:
            data_start_offeset = current_offset + 0x0
            size_offset = current_offset + 0x4
            file_name_offset = current_offset + 0xC
            date_offset = current_offset + 0x3c

            data_start = read_from_offset(file, data_start_offeset, 4)
            size = read_from_offset(file, size_offset, 4)
            
            file_name = read_string_from_offset(file, file_name_offset)
            date = read_string_from_offset(file, date_offset)

            print(f"{file_name}\t| 0x{data_start:08X}\t| {size}\t")

            mtk_file = MTKFile()
            mtk_file.file_name = file_name
            mtk_file.data_offset = data_start
            mtk_file.size = size

            files.append(mtk_file)

            current_offset += section_size

        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)

        for mtk_file in files:
            print(f"Dumping: {mtk_file.file_name}\t")
            dump_file(file, mtk_file.data_offset, mtk_file.size, mtk_file.file_name)

if __name__ == "__main__":
    main()
