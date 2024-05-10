import argparse
import json
import pathlib
from ..common.utils import read_input_npy


def to_json(input_filepath):
    input_data = read_input_npy(input_filepath)
    data = input_data.tolist()
    json_string = json.dumps(data, indent=4)
    print(json_string)


def main():
    parser = argparse.ArgumentParser(description="Convert npy to json")
    parser.add_argument('npy_filepath', nargs='?', type=pathlib.Path, help="Filepath to the npy file. If not specified, read from stdin.")

    args = parser.parse_args()
    to_json(args.npy_filepath)
