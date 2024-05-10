import argparse
from ..common.utils import read_input_npy, write_output_npy


def transpose(perms):
    input_data = read_input_npy(None)
    output_data = input_data.transpose(perms)
    write_output_npy(output_data)


def main():
    parser = argparse.ArgumentParser(description="Get one array from a npy dictionary")
    parser.add_argument('perm', nargs='+', type=int)

    args = parser.parse_args()

    transpose(args.perm)
