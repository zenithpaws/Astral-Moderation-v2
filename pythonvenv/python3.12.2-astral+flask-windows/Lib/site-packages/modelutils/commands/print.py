import argparse
import pathlib
import sys
import numpy as np
from ..common.utils import read_input_npy


def _stats(data):
    return f"shape: {data.shape} min: {np.min(data)} max: {np.max(data)} mean: {np.mean(data)}"


def npy_print(input_filepath, show_stat, show_all):
    input_data = read_input_npy(input_filepath)
    if show_all:
        np.set_printoptions(threshold=sys.maxsize)

    if show_stat:
        if input_data.dtype == np.dtype('O'):
            input_data = input_data.item()
            for name, data in input_data.items():
                print(f"{name}: {_stats(data)}")
        else:
            print(_stats(input_data))
    else:
        print(input_data)


def main():
    parser = argparse.ArgumentParser(description="Get one array from a npy dictionary")
    parser.add_argument('npy_filepath', nargs='?', type=pathlib.Path, help="Filepath to the npy file. If not specified, read from stdin.")
    parser.add_argument('--stats', '-s', action='store_true')
    parser.add_argument('--all', '-a', action='store_true')

    args = parser.parse_args()
    if args.stats and args.all:
        parser.error("--stats and --all cannot be used together.")

    npy_print(args.npy_filepath, args.stats, args.all)
