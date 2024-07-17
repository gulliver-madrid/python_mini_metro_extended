from .node import Node


def skip_stations_on_same_path(node_path: list[Node]) -> list[Node]:
    assert len(node_path) >= 2

    if len(node_path) == 2:
        return node_path

    nodes_to_remove: list[Node] = []
    i = 0  # Start of the current segment
    j = 1  # End of the current segment

    path_set_list = [x.paths for x in node_path]
    path_set_list.append(set())  # Prevent index out of range

    while j <= len(path_set_list) - 1:
        set_a = path_set_list[i]
        set_b = path_set_list[j]

        if set_a & set_b:
            j += 1  # Continue exploring the current segment
        else:
            # Mark intermediate nodes for removal
            for k in range(i + 1, j - 1):
                nodes_to_remove.append(node_path[k])
            i = j - 1
            j += 1

    for node in nodes_to_remove:
        node_path.remove(node)

    return node_path
