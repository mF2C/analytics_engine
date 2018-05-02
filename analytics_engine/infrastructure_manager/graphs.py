# Copyright (c) 2017, Intel Research and Development Ireland Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Graph utils.
"""
import networkx as nx
from networkx.algorithms import isomorphism
import analytics_engine.common as common

LOG = common.LOG


def _node_match(node_a_attr, node_b_attr):
    """
    Compares attributes of the nodes for equality.

    :param node_a_attr: Attributes of first node.
    :param node_b_attr: Attributes of second node.
    :return: True is equal - otherwise False
    """
    if node_a_attr == node_b_attr:
        return True
    return False


def _edge_match(edge_a_attr, edge_b_attr):
    """
    Compares attributes of the edges for equality.

    :param edge_a_attr: Attributes of first edge.
    :param edge_b_attr: Attributes of second edge.
    :return: True is equal - otherwise False
    """
    if edge_a_attr == edge_b_attr:
        return True
    return False


def match_type(one, another):
    """
    Matcher which matches on type.

    :param one: dictionary A
    :param another: dictionary B
    :return: True or False.
    """
    res = True
    # this will make sure network node is mapped to network node.
    if 'type' in one and 'type' in another:
        res = one['type'] == another['type']
    return res


def compare_topology(graph1, graph2, match1=_node_match, match2=_edge_match):
    """
    Compares the topology of two graphs.

    :param graph1: The first graph.
    :param graph2: The second graph.
    :param match1: Matcher for attributes of the nodes.
    :param match2: Matcher for attributes of the edges.
    :return: Triple of: True if graphs are identical - otherwise False,
                         True if g2 is subgraph of g1 - otherwise False,
                         dict with the mappings and differences.
    """
    graph_equal = False
    is_subgraph = False
    result = {'mapping': {}, 'diff': []}

    comp = isomorphism.DiGraphMatcher(graph1,
                                      graph2,
                                      node_match=match1,
                                      edge_match=match2)

    if comp.is_isomorphic():
        graph_equal = True
    elif comp.subgraph_is_isomorphic():
        is_subgraph = True
        result['diff'] = list(set(graph1.nodes()) - set(comp.mapping.keys()) -
                              set(comp.mapping.values()))

    result['mapping'] = comp.mapping

    return graph_equal, is_subgraph, result


def compare_graphs(before, after):
    """
    Compare two (sub)graphs.

    Note: a == b != b == a!

    :param before: A networkx (sub)graph.
    :param after: A networkx (sub)graph.
    :returns: A dict with changes.
    """
    res = {'added': [],
           'removed': [],
           'added_edge': [],
           'removed_edge': [],
           'chg_attr': []}

    for node in after.nodes():
        if node not in before.nodes():
            # add missing nodes
            if node not in res['added']:
                res['added'].append(node)
            for link in after.out_edges([node]):
                if link[1] not in before.nodes() \
                        and link[1] not in res['added']:
                    res['added'].append(link[1])
                res['added_edge'].append(link)
        else:
            # already there...
            if before.node[node]['attributes'] != \
                    after.node[node]['attributes']:
                res['chg_attr'].append((node,
                                        before.node[node]['attributes'],
                                        after.node[node]['attributes']))
    for node in before.nodes():
        if node not in after.nodes():
            res['removed'].append(node)
            for link in before.out_edges([node]):
                res['removed_edge'].append(link)
        else:
            # node exists lets check the edges.
            for link in after.out_edges([node]):
                if link not in before.out_edges([node]):
                    res['added_edge'].append(link)
            for link in before.out_edges([node]):
                if link not in after.out_edges([node]):
                    res['removed_edge'].append(link)
    return res


def filter_graph(graph, layers=None):
    """
    Filter graph based on layers and excluded nodes.

    :param graph: The graph.
    :param layers: The layers to be kept.
    :return: A copy of the original graph.
    """
    layers = layers or []
    res = graph.copy()
    for item in graph.nodes(data=True):
        if item[1]['layer'] not in layers:
            res.remove_node(item[0])
    return res


def get_allocation_graph(graph, lower_type='machine', higher_layer=None,
                         lower_layer=None):
    """
    Return a graph on how particular entities from a higher layer (default:
    virtual) are allocated upon entities from a lower layer (default:
    physical).

    :param graph: A sub graph describing a service stack.
    :param lower_type: Type of the lower level entity (default: machine).
    :param higher_layer: Identifiers for higher layer (default: virtual).
    :param higher_layer: Identifiers for lower layer (default: physical).
        :return: Filtered Graph.
    """
    if higher_layer is None:
        higher_layer = ['virtual']
    if lower_layer is None:
        lower_layer = ['physical']

    tmp1 = nx.DiGraph()
    for machine in filter_graph(graph, layers=lower_layer).nodes(
            data=True):
        if machine[1]['type'] == lower_type:
            filtr = [machine[0]]
            filtr.extend(graph.to_undirected().neighbors(machine[0]))
            for node in graph.nodes(data=True):
                if node[0] in filtr and node[1]['layer'] in higher_layer:
                    tmp1.add_node(machine[0], machine[1])
                    tmp1.add_node(node[0], node[1])
                    tmp1.add_edge(node[0], machine[0])
    return tmp1


def get_vm_allocation(graph):
    """
    Figure out how VMs are placed on which physical nodes.

    :param graph: The subgraph to inspect.
    :return: Dictionary with the mapping.
    """
    alloc_map = {}
    for item in graph:
        if graph.node[item]['type'] == 'compute':
            for rel in nx.all_neighbors(graph, item):
                if graph.node[rel]['type'] == 'machine':
                    alloc_map[item] = rel
    return alloc_map


def find_placement_diffs(graph1, graph2, match1=_node_match,
                         match2=_edge_match):
    """
    Find differences in the placements of two stacks. Returns either True or
    False and a (possible) mapping.

    :param graph1: Graph describing first stack.
    :param graph2: Graph describing second stack.
    :param match1: Matcher for attributes of the nodes.
    :param match2: Matcher for attributes of the edges.

    :return: True or False and a dictionary with mappings.
    """
    all_equal, _, big_map = compare_topology(graph1, graph2, match1, match2)
    graph_a = filter_graph(graph1, layers=['service', 'virtual'])
    graph_b = filter_graph(graph2, layers=['service', 'virtual'])
    service_equal, service_similar, tmp = compare_topology(graph_a, graph_b,
                                                           match1, match2)

    if all_equal:
        # All identical.
        LOG.info('placement is identical...')
        return True, big_map
    elif service_equal or service_similar:
        # Stacks seem to be 'identical' - diff might be in alloc.
        tmp1 = filter_graph(graph1, layers=['virtual', 'physical'])
        tmp2 = filter_graph(graph2, layers=['virtual', 'physical'])

        identy, similar, mapy = compare_topology(tmp1, tmp2, match1, match2)

        if identy or similar:
            LOG.info('Placement is similar...')
            return True, mapy
        else:
            LOG.info('Placement is not similar...')
            # XXX: Returns mapping of virtual/service nodes - not the physical
            # ones as those cannot be mapped...
            return False, tmp
    elif not all_equal and not service_equal and not service_similar:
        # Those stacks have to do nothing with each other!
        LOG.info('Not matching at all!')
        return False, {'diff': [], 'mapping': {}}


def _weight_table(dat):
    """
    Return weight table.
    """
    table = {}
    # weight tables
    for item in dat:
        if dat[item] not in table:
            table[dat[item]] = [(item, 1.0)]
        else:
            old = table[dat[item]]
            new = []
            for old_item in old:
                new.append((old_item[0], 1.0 / (len(old) + 1.0)))
            new.append((item, 1.0 / (len(old) + 1.0)))
            table[dat[item]] = new
    return table


def _weight_list(dat):
    """
    Return weight list.
    """
    tmp = _weight_table(dat)
    res = {}
    for item in tmp:
        for ent in tmp[item]:
            res[ent[0]] = ent[1]
    return res


def optimize_placement(mapping, map_a, map_b):
    """
    Suggest placement optimization. Returns suggestion on which VMs could
    be consolidated or deconsolidated.

    :param mapping: A mapping of the nodes.
    :param map_a: Placement map of the first service stack.
    :param map_b: Placement map of the second service stack.
    :returns: Tuple of VMs which need to be (de)consolidated.
    """
    wla = _weight_list(map_a)
    wlb = _weight_list(map_b)

    consol = []
    deconsol = []
    for item in wla:
        if wlb[mapping[item]] < wla[item]:
            deconsol.append(mapping[item])
        elif wlb[mapping[item]] == wla[item]:
            pass
        else:
            consol.append(mapping[item])

    return consol, deconsol


def merge_graph(graph_1, graph_2):
    """
    Merge two graphs together.
    :return: A merged Graph.
    """
    graph = graph_1.copy()
    graph.add_nodes_from(graph_2.nodes(data=True))
    graph.add_edges_from(graph_2.edges(data=True))
    graph_undirected = graph.to_undirected()
    if nx.is_connected(graph_undirected):
        return graph
    else:
        raise ValueError("Trying to merge graphs with no nodes in common!")
