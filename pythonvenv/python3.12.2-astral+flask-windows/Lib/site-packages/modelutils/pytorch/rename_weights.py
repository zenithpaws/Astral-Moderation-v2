import argparse
import os
import torch


def rename_weights(input_filepath, output_filepath, rename_lists):
    if os.path.exists(output_filepath):
        raise RuntimeError(f"{output_filepath} already exists.")

    state_dict = torch.load(input_filepath)
    for rename in rename_lists:
        original_name, new_name = rename.split(':')
        original_name = original_name.strip()
        new_name = new_name.strip()

        state_dict[new_name] = state_dict[original_name]
        del state_dict[original_name]

    torch.save(state_dict, output_filepath)


def main():
    parser = argparse.ArgumentParser("Rename the name of pytorch state dict")
    parser.add_argument('input_filepath', type=str)
    parser.add_argument('output_filepath', type=str)
    parser.add_argument('--rename', type=str, action='append', help='<original name>:<new name>')

    args = parser.parse_args()

    rename_weights(args.input_filepath, args.output_filepath, args.rename)


if __name__ == '__main__':
    main()
