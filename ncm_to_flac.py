# pip3 install pycrypto

import binascii
import struct
import base64
import json
import os
from Crypto.Cipher import AES
import argparse
import os 
import tqdm

def dump(source,target):
    core_key = binascii.a2b_hex("687A4852416D736F356B496E62617857")
    meta_key = binascii.a2b_hex("2331346C6A6B5F215C5D2630553C2728")
    unpad = lambda s : s[0:-(s[-1] if type(s[-1]) == int else ord(s[-1]))]
    f = open(source,'rb')
    header = f.read(8)
    assert binascii.b2a_hex(header) == b'4354454e4644414d'
    f.seek(2, 1)
    key_length = f.read(4)
    key_length = struct.unpack('<I', bytes(key_length))[0]
    key_data = f.read(key_length)
    key_data_array = bytearray(key_data)
    for i in range (0,len(key_data_array)): key_data_array[i] ^= 0x64
    key_data = bytes(key_data_array)
    cryptor = AES.new(core_key, AES.MODE_ECB)
    key_data = unpad(cryptor.decrypt(key_data))[17:]
    key_length = len(key_data)
    key_data = bytearray(key_data)
    key_box = bytearray(range(256))
    c = 0
    last_byte = 0
    key_offset = 0
    for i in range(256):
        swap = key_box[i]
        c = (swap + last_byte + key_data[key_offset]) & 0xff
        key_offset += 1
        if key_offset >= key_length: key_offset = 0
        key_box[i] = key_box[c]
        key_box[c] = swap
        last_byte = c
    meta_length = f.read(4)
    meta_length = struct.unpack('<I', bytes(meta_length))[0]
    meta_data = f.read(meta_length)
    meta_data_array = bytearray(meta_data)
    for i in range(0,len(meta_data_array)): meta_data_array[i] ^= 0x63
    meta_data = bytes(meta_data_array)
    meta_data = base64.b64decode(meta_data[22:])
    cryptor = AES.new(meta_key, AES.MODE_ECB)
    meta_data = unpad(cryptor.decrypt(meta_data)).decode('utf-8')[6:]
    meta_data = json.loads(meta_data)
    crc32 = f.read(4)
    crc32 = struct.unpack('<I', bytes(crc32))[0]
    f.seek(5, 1)
    image_size = f.read(4)
    image_size = struct.unpack('<I', bytes(image_size))[0]
    image_data = f.read(image_size)
    file_name = meta_data['musicName'] + '.' + meta_data['format']
    m = open(os.path.join(target,file_name),'wb')
    chunk = bytearray()
    while True:
        chunk = bytearray(f.read(0x8000))
        chunk_length = len(chunk)
        if not chunk:
            break
        for i in range(1,chunk_length+1):
            j = i & 0xff;
            chunk[i-1] ^= key_box[(key_box[j] + key_box[(key_box[j] + j) & 0xff]) & 0xff]
        m.write(chunk)
    m.close()
    f.close()

def npm2flac(source,target_dir):
    for root, dirs, files in os.walk(source):
        for file in files:
            print(f'### Now is {file} ###')
            if os.path.splitext(file)[1] == '.ncm':
                file = os.path.join(root, file)
                dump(file,target_dir)
                print(file)

def flac2mp3(source_dir,target_dir):
    #如果是以.flac结尾
    for root, dirs, file in os.walk(source_dir):
            for f in file:
                source_file = os.path.join(root,f)
                print(f'### now is {file} ###')
                target_file = os.path.join(target_dir,f[:-5] + '.mp3')
                cmd_ffmpeg  = f"ffmpeg -i {source_file} -ab 320k -map_metadata 0 -id3v2_version 3 {target_file}"
                os.system(cmd_ffmpeg)

#增加参数项目

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert Ncm to flac on muisc type")
    parser.add_argument('--ncm_dir',type=str, default='./ncm')
    parser.add_argument('--flac_dir',type=str, default='./flac')
    parser.add_argument('--mp3_dir',type=str, default='./mp3')
    parser.add_argument('--only_flac',action='store_true')
    args = parser.parse_args()
    import sys
    try:
        if not args.only_flac:
            print(f'### Starting NCM TO FLAC ###')
            npm2flac(args.ncm_dir,args.flac_dir)
        print(f'### Starting FLAC to MP3 ###')
        flac2mp3(args.flac_dir,args.mp3_dir)
        print(f'### Ending FLAC to MP3 ###')
    except:
        print('Fail')