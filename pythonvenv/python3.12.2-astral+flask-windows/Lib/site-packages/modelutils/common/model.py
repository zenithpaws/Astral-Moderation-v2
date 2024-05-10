import collections
import dataclasses


class Model:
    @dataclasses.dataclass
    class Node:
        op: str
        name: str
        inputs: list
        attrs: dict

    def __init__(self):
        self._nodes = {}
        self._data = {}
        self._attrs = {}

    @property
    def nodes(self):
        return self._nodes

    @property
    def data(self):
        return self._data

    @property
    def attrs(self):
        return self._attrs

    def add_node(self, op, name, inputs, attrs):
        assert name not in self._nodes, f"Duplicated name: {name}"
        self._nodes[name] = Model.Node(op, name, inputs, attrs)

    def add_data(self, name, data):
        assert name not in self._data
        self._data[name] = data

    def add_attr(self, key, value):
        assert key not in self._attrs
        self._attrs[key] = value

    def remove_node(self, name):
        del self._nodes[name]

    def validate(self):
        input_node_name = self._get_input_name()
        output_maps = collections.defaultdict(list)
        for node in self._nodes.values():
            for i in node.inputs:
                output_maps[i].append(node.name)

        stack = [input_node_name]
        stack_counts = [1]
        current_trace = []
        visited = set()
        while stack:

            current = stack.pop()
            visited.add(current)
            while stack_counts and stack_counts[-1] == 0:
                stack_counts.pop()
                current_trace.pop()

            stack_counts[-1] -= 1

            next_node_names = output_maps[current]
            next_node_in_trace = set(current_trace).intersection(next_node_names)
            if next_node_in_trace:
                print(f"Trace: {current_trace}")
                raise RuntimeError(f"Cycle detected: {current} -> {next_node_in_trace}")
            next_node_names = [n for n in next_node_names if n not in visited]
            stack.extend(next_node_names)
            stack_counts.append(len(next_node_names))
            current_trace.append(current)

            assert sum(stack_counts) == len(stack), f"stack_counts: {stack_counts}, stack: {stack}"

    def _data_summary(self, data_id):
        if data_id not in self._data:
            return ""

        return str(self._data[data_id].shape)

    def _node_summary(self, node_name):
        node = self._nodes[node_name]
        line = str(node)
        for input_id in node.inputs:
            line += self._data_summary(input_id)
        return line

    def _get_input_name(self):
        consumed_names = set([i for n in self.nodes.values() for i in n.inputs])
        weight_names = set(self.data.keys())
        existing_names = set(self.nodes.keys())
        input_nodes = consumed_names - weight_names - existing_names
        assert len(input_nodes) == 1, f"Multiple input nodes are found: {input_nodes}"
        return list(input_nodes)[0]

    def __str__(self):
        lines = [self._node_summary(node.name) for node in self]
        text = '\n'.join(lines)
        if self.attrs:
            text += '\n' + str(self.attrs)
        return text

    def __iter__(self):
        """Sort the nodes topologically and iterate over them"""
        nodes = self._topological_sort(self._nodes, self._get_input_name())
        return iter(nodes)

    @staticmethod
    def _get_layer_levels(nodes, input_name):
        start_node = [n for n in nodes.values() if input_name in n.inputs]
        assert len(start_node) == 1
        start_node_name = start_node[0].name

        output_maps = collections.defaultdict(list)
        for n in nodes.values():
            for i in n.inputs:
                output_maps[i].append(n.name)

        layer_levels = {}
        queue = [start_node_name]
        index = 0
        visited = set()
        while queue:
            next_names = []
            for name in queue:
                if name not in layer_levels or layer_levels[name] < index:
                    next_names.extend(output_maps[name])
                    layer_levels[name] = index
            queue = next_names
            index += 1

        assert len(layer_levels) == len(nodes)
        return layer_levels

    @staticmethod
    def _get_branch_levels(nodes):
        inputs_set = set([i for n in nodes.values() for i in n.inputs])
        nodes_set = set([n.name for n in nodes.values()])
        end_nodes = nodes_set - inputs_set
        assert len(end_nodes) == 1
        end_node_name = list(end_nodes)[0]

        queue = [(end_node_name, 0)]
        branch_levels = {end_node_name: 0}
        while queue:
            name, level = queue.pop(0)
            level = min(branch_levels[name], level)
            for i, n in enumerate(nodes[name].inputs):
                if n in nodes and not (n in branch_levels and i + level > branch_levels[n]):
                    queue.append((n, i + level))
                branch_levels[n] = i + level

        return branch_levels

    @staticmethod
    def _topological_sort(nodes, input_name):
        layer_levels = Model._get_layer_levels(nodes, input_name)
        branch_levels = Model._get_branch_levels(nodes)
        max_layer_level = max(layer_levels.values())
        max_branch_level = max(branch_levels.values())

        layers = [None] * (max_layer_level + 1)
        for name, level in layer_levels.items():
            if layers[level]:
                layers[level].append(name)
            else:
                layers[level] = [name]

        for i in range(len(layers)):
            layers[i].sort(key=lambda x: branch_levels[x])

        sorted_names = [l[0] for l in layers]  # Branch level=0
        index_conversion_map = {i: i for i in range(len(layers))}
        for branch_level in range(1, max_branch_level + 1):
            current_list = [l[branch_level] if len(l) > branch_level else None for l in layers]
            assert not current_list[-1]  # Last layer always has branch level=0.

            start_point = 0
            for i in range(1, len(current_list)):
                if not current_list[i-1] and current_list[i]:
                    start_point = i
                if current_list[i-1] and not current_list[i]:
                    sublist = current_list[start_point:i]
                    index = index_conversion_map[i]
                    sorted_names[index:index] = sublist
                    for j in range(i+1, len(layers)):
                        index_conversion_map[j] += len(sublist)

        return [nodes[n] for n in sorted_names]
