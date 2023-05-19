import argparse
 
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('files', type=argparse.FileType('rb+'), nargs='+')
    args = parser.parse_args()
 
    for file in args.files:
        buffer = bytearray(file.read())
 
        # Delete initial empty line
        while (buffer[0] == 0x0d) or (buffer[0] == 0x0a):
            del buffer[0]
 
        # Un-split Subject: CC: etc.
        for i in range(buffer.find(b'\x0d\x0a---')):
            if (buffer[i] == 0x3a) and (buffer[i+1] == 0x0d) and (buffer[i+2] == 0x0a):
                del buffer[i+1]
                buffer[i+1] = 0x20
 
        # Remove double CRLF from chunks
        i = buffer.find(b'\x0d\x0a@@')
        while i < len(buffer) - 3:
            if (buffer[i] == 0x0d) and (buffer[i+1] == 0x0a) and (buffer[i+2] == 0x0d) and (buffer[i+3] == 0x0a):
                del buffer[i]
                del buffer[i]
            i = i + 1
        file.seek(0)
        file.write(buffer)
        file.truncate()