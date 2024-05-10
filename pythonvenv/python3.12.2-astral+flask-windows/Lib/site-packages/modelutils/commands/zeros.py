import argparse
import numpy as np
from ..common.utils import write_output_npy


def zeros(dims, value):
    zeros = np.zeros(dims, dtype=np.float32)
    if value:
        zeros += value

    write_output_npy(zeros)


def main():
    parser = argparse.ArgumentParser(description="Create np.zeros() array")
    parser.add_argument('dims', nargs='+', type=int)
    parser.add_argument('--value', '-v', type=float)

    args = parser.parse_args()
    zeros(args.dims, args.value)


if __name__ == '__main__':
    main()
