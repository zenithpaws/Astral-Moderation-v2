import argparse
import pathlib
import numpy as np
from ..common.utils import read_input_npy, write_output_npy


def diff(filepath0, filepath1):
    assert filepath0 and filepath1
    array0 = read_input_npy(filepath0)
    array1 = read_input_npy(filepath1)
    output_data = np.abs(array0 - array1)
    write_output_npy(output_data)


def main():
    parser = argparse.ArgumentParser(description="Get one array from a npy dictionary")
    parser.add_argument('npy_filepath0', type=pathlib.Path, help="Filepath to the npy file.")
    parser.add_argument('npy_filepath1', type=pathlib.Path, help="Filepath to the npy file.")

    args = parser.parse_args()
    diff(args.npy_filepath0, args.npy_filepath1)
