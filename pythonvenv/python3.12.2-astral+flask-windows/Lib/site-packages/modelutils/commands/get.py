import argparse
import pathlib
import numpy as np
from ..common.utils import read_input_npy, write_output_npy


def get(input_filepath, name):
    input_data = read_input_npy(input_filepath)
    assert input_data.dtype == np.dtype('O')
    input_data = input_data.item()
    if not name and len(input_data) != 1:
        raise RuntimeError("Please specify name")

    output_data = input_data[name] if name else next(iter(input_data.values()))
    write_output_npy(output_data)


def main():
    parser = argparse.ArgumentParser(description="Get one array from a npy dictionary")
    parser.add_argument('npy_filepath', nargs='?', type=pathlib.Path, help="Filepath to the npy file. If not specified, read from stdin.")
    parser.add_argument('--name')

    args = parser.parse_args()

    get(args.npy_filepath, args.name)
