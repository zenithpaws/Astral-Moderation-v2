import argparse
import tensorflow as tf


def pprint_table(table):
    max_lens = [0] * max([len(t) for t in table])
    for t in table:
        for i in range(len(t)):
            max_lens[i] = max(max_lens[i], len(t[i]))

    for t in table:
        print("".join([f"{t[i]: <{max_lens[i]}}" for i in range(len(t))]))


def print_node_summary(graph_def):
    nodes_summary = []
    for node in graph_def.node:
        summary = [node.op, str(node.input), '=> ' + node.name]
        nodes_summary.append(summary)
    pprint_table(nodes_summary)


def summarize(filename):
    graph_def = tf.compat.v1.GraphDef()
    with open(filename, 'rb') as f:
        graph_def.ParseFromString(f.read())

    print_node_summary(graph_def)


def main():
    parser = argparse.ArgumentParser('Dump a TensorFlow model to text')
    parser.add_argument('model_filename', type=str, help='Filename for the input TF file')

    args = parser.parse_args()
    summarize(args.model_filename)


if __name__ == '__main__':
    main()
