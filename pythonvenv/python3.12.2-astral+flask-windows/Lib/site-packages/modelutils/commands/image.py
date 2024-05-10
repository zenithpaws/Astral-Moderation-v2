import argparse
import io
import pathlib
import sys
import PIL.Image
import numpy as np


def load_image(image_filepath, image_size, scale, subtract_value, bgr):
    image = PIL.Image.open(image_filepath)
    image = image.resize((image_size, image_size), PIL.Image.ANTIALIAS)
    image = np.array(image, dtype=np.float32) / 255
    image *= scale
    image -= subtract_value
    image = image[:, :, (2, 1, 0)] if bgr else image

    image = image[np.newaxis, :]

    bytesio = io.BytesIO()
    np.save(bytesio, image)
    bytesio.seek(0)
    serialized = bytesio.read()
    sys.stdout.buffer.write(serialized)


def main():
    parser = argparse.ArgumentParser(description="Load a image and dump as numpy array")
    parser.add_argument('image_filepath', type=pathlib.Path)
    parser.add_argument('--size', type=int, default=224, help="input size")
    parser.add_argument('--scale', type=float, default=1)
    parser.add_argument('--subtract', type=float, default=0)
    parser.add_argument('--bgr', action='store_true')

    args = parser.parse_args()
    if not args.image_filepath.exists():
        parser.error(f"{args.image_filepath} doesn't exist.")

    load_image(args.image_filepath, args.size, args.scale, args.subtract, args.bgr)


if __name__ == '__main__':
    main()
