def genreg_via_cycles(n, k, g, adjacency_lists=None, nj_stack=None, additional_edge_predicates=None):
    """
    Generates and returns the first regular graph of n, k, g found via cycle generation
    see http://www.mathe2.uni-bayreuth.de/markus/reggraphs.html

    Implementation Notes:

    could be modified to return and take the adjacency_lists and nj_stack in order to find next graph

    should track symmetric graph states
    no need to reattempt a graph state that leads to failure
    and returning a symmetric graph is redundant
    however such a tracking system could be expensive
    see http://www.mathe2.uni-bayreuth.de/markus/pdf/pub/FastGenRegGraphJGT.pdf

    if any graph exists, discovering one via cycles appears to reasonably efficient even without said system
    for my purposes implementing such a system was not important

    :param n: number of vertices
    :param k: degree (edges per node)
    :param g: minimum girth
    :param adjacency_lists: either a previous graph or set of externally required edges
    :param nj_stack: N/A (Not yet implemented)
    :param additional_edge_predicates: list of [function(n, k, g, ni, nj, k_list, adjacency_lists)=>bool]
    :return: adjacency_lists
    """

    if not validate_arguments(n, k, g):
        return None

    # k_list tracks the degree of each node
    k_list = [0] * n
    if adjacency_lists is None:
        adjacency_lists = construct_adjacency_lists(n, k)
    else:
        for ni in range(n):
            while k_list[ni] < k and 0 <= adjacency_lists[ni][k_list[ni]]:
                k_list[ni] += 1

    if nj_stack is None:
        nj_stack = []
        ci = 0
        # enter the loop
    else:
        # ToDo: modify code in such a way that we can essentially jump into the failed edge part of the loop
        # Note: probably not very meaningful without tracking symmetric graphs
        # otherwise a symmetric graph could be returned
        return None

    # iterate through each cycle/degree
    while ci < k:
        n0 = 0
        # iterate through each node ensuring that each node has more than ci edges
        while n0 < n:
            # if this node needs the ci cycle or edge
            if ci == k_list[n0]:
                # begin the cycle/edge at n0
                ni = n0
                nj = (ni + 1) % n
                done = False
                while not done:
                    # Find the next valid node nj for edge ni -> nj
                    while ni != nj and not is_edge_valid(
                            n,
                            ci + (1 if nj != n0 or ci == k - 1 else 2),  # only allow edges less than this cycle/degree
                            g,
                            ni, nj,
                            k_list, adjacency_lists,
                            additional_edge_predicates
                    ):
                        nj = (nj + 1) % n

                    # if no valid edges were found before going all the way around,
                    # undo most recently created edge and attempt to resume with next node
                    if ni == nj:
                        # if this was the first edge of this cycle
                        # revert to the state of the last connection of the previous cycle
                        if ni == n0:
                            if nj_stack:
                                nj = nj_stack.pop()
                                ci = k_list[nj] - (2 if k_list[nj] < k or k % 2 == 0 else 1)
                                n0 = nj if ci < k - 1 else adjacency_lists[nj][k_list[nj] - 1]

                            # if nothing left to revert to then fail
                            else:
                                return None

                        k_list[nj] -= 1
                        ni = adjacency_lists[nj][k_list[nj]]
                        adjacency_lists[nj][k_list[nj]] = -1

                        k_list[ni] -= 1
                        adjacency_lists[ni][k_list[ni]] = -1

                        nj = (nj + 1) % n

                    # if valid edge found, create edge
                    else:
                        adjacency_lists[ni][k_list[ni]] = nj
                        k_list[ni] += 1

                        adjacency_lists[nj][k_list[nj]] = ni
                        k_list[nj] += 1

                        # if cycle is complete or k is odd and ci is on last iteration then done
                        # if k is odd and ci is on last iteration, each node only needs one edge (not a cycle)
                        done = nj == n0 or ci == k - 1
                        if done:
                            nj_stack.append(nj)
                        else:
                            ni = nj
                            nj = (nj + 1) % n
            # while n0 < n: continued
            n0 += 1
        # while ci < k: continued
        ci += 2

    return adjacency_lists


def construct_adjacency_lists(n, k):
    return [[-1] * k for _ in range(n)]


def is_edge_valid(n, k, g, ni, nj, k_list, adjacency_lists, additional_edge_predicates=None):
    # if nj has no edges there will be no issues
    if k_list[nj] == 0 and 0 < k:
        return True

    # invalid if nj is already has the maximum edges allowed
    if k <= k_list[nj]:
        return False

    if additional_edge_predicates:
        for additional_edge_predicate in additional_edge_predicates:
            if not additional_edge_predicate(n, k, g, ni, nj, k_list, adjacency_lists):
                return False

    # prime queues for breadth first traversal
    source_nodes = []
    target_nodes = []
    for ki in range(k_list[ni]):
        source_nodes.append(ni)
        target_nodes.append(adjacency_lists[ni][ki])
    source_nodes.append(ni)
    target_nodes.append(nj)

    # use a breadth first traversal to check for duplicate nodes to enforce girth
    node_set = set()
    edges_to_traverse = g // 2
    even = g % 2 == 0
    for iteration in range(edges_to_traverse):
        # ignore duplicate nodes if girth is even and on the last iteration
        ignore_if_duplicated = even and iteration == edges_to_traverse - 1

        next_source_nodes = []
        next_target_nodes = []
        for i in range(len(source_nodes)):
            source_node = source_nodes[i]
            target_node = target_nodes[i]

            if target_node in node_set:
                return False

            if not ignore_if_duplicated:
                node_set.add(target_node)

            if iteration < edges_to_traverse - 1:
                # prepare children for next iteration
                for ki in range(k_list[target_node]):
                    next_target_node = adjacency_lists[target_node][ki]
                    if next_target_node != source_node:
                        next_source_nodes.append(target_node)
                        next_target_nodes.append(next_target_node)

        source_nodes = next_source_nodes
        target_nodes = next_target_nodes

    return True


def validate_arguments(n, k, g):
    if n % 2 == 1 and k % 2 == 1:
        print("Impossible arguments: both n and k are odd")
        return False

    if g <= 3 or k <= 2:
        if n < g or n <= k:
            print("Impossible arguments: n <= k or n < g")
            return False
        else:
            return True

    if g == 4:
        if n < 2 * k:
            print("Impossible arguments: n < 2k and g = 4")
            return False
        return True

    if k == 3:
        if g == 5:
            if n < 10:
                print("Impossible arguments: n < 10, k = 3 and g = 5")
                return False
        elif g == 6:
            if n < 14:
                print("Impossible arguments: n < 14, k = 3 and g = 6")
                return False
        else:
            print("Good luck: k = 3 and g >= 7")
            print("see: https://hog.grinvin.org/Cubic")
            print("and http://staffhome.ecm.uwa.edu.au/~00013890/remote/cages/index.html")
        return True

    if k == 4:
        if g == 5:
            if n < 19:
                print("Impossible arguments: n < 19, k = 4 and g = 5")
                return False
        elif g == 6:
            if n < 26:
                print("Impossible arguments: n < 26, k = 4 and g = 6")
                return False
        else:
            print("Good luck: k = 4 and g >= 7")
            print("see: https://hog.grinvin.org/Quartic")
        return True

    print("Good luck: k >= 5 and g >= 5")
    print("see: http://www.mathe2.uni-bayreuth.de/markus/reggraphs.html")

    return True
