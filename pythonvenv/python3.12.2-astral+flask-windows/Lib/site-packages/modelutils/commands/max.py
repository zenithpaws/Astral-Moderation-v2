import argparse
import pathlib
import numpy as np
from ..common.utils import read_input_npy


def np_max(input_filepath):
    input_data = read_input_npy(input_filepath)
    max_value = np.max(input_data)
    print(max_value)


def main():
    parser = argparse.ArgumentParser(description="Get a max scalar value from numpy array")
    parser.add_argument('npy_filepath', nargs='?', type=pathlib.Path, help="Filepath to the npy file. If not specified, read from stdin.")

    args = parser.parse_args()

    np_max(args.npy_filepath)
