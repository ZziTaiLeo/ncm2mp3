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
import ffmpeg

class Convert():
    def __init__(self):
        #构造转换函数
        pass
    def dump(self,source,target):
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
        return file_name

    def ncm2mp3(self,source_root, f ,target_dir):
        source_file = os.path.join(source_root,f)
        print(f'### Now is npm  to flac: {source_file} ###')
        # try:
        #source_file的 目录位置
        new_f = self.dump(source_file, source_root)
        print(f'new_f :{new_f}')
        # except:
        #     print(f" {source_file} can't dump")
        #source_file 末尾将.ncm 换为.flac
        print(f'f is :{f}')
        self.flac2mp3(source_file.replace(f, new_f), target_dir)
        #删除source_file
        print(f'删除文件:{source_file.replace(f, new_f)}')
        os.remove(source_file.replace(f, new_f))
            

    def flac2mp3(self,source_file,target_dir):
        print(f'### now is flac to mp3: {source_file} ###')
        #获取source_file 最后的文件名
        f = os.path.basename(source_file)
        target_file = os.path.join(target_dir,f.replace('.flac','.mp3'))
        input_stream = ffmpeg.input(source_file)
        # try:
        # ffmpeg 替换已存在内容
        if os.path.exists(target_file):
            os.remove(target_file)
        output_stream = ffmpeg.output(input_stream, target_file, ab='320k',map_metadata=0,id3v2_version=3,loglevel='quiet')
        ffmpeg.run(output_stream)
        # except:
        #     print(f" {source_file} can't convert")
        