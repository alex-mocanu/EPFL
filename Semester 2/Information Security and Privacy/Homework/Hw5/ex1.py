import wave
import numpy as np


def find_flag(lsbs, header):
    num_bytes = len(lsbs) // 8
    # Get byte string
    binary_byte_str = np.array(lsbs[:num_bytes*8]).reshape(-1, 8)
    mask = np.array([1<<(7-i) for i in range(8)]).reshape(1, -1)
    byte_str = bytes(list((binary_byte_str * mask).sum(1)))

    # Find the header of the flag
    flag_start = byte_str.find(header)
    # Find the end of the flag
    flag_end = flag_start + byte_str[flag_start:].find(b'}') + 1
    print('The flag is :', byte_str[flag_start:flag_end])


if __name__ == '__main__':
    audio_file = 'alexandru.mocanu@epfl.ch.wav'
    with wave.open(audio_file, 'rb') as f:
        # Get audiofile characteristics
        num_frames = f.getnframes()
        frame_rate = f.getframerate()
        sample_width = f.getsampwidth()

        # Read content
        frames = f.readframes(num_frames)

        # Extract least significant bits
        lsbs = [frames[i] & 1 for i in range(0, len(frames), sample_width)]
        flag_header = b'COM402{'

        find_flag(lsbs, flag_header)
