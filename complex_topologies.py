import random
from typing import Optional

from python_ta.contracts import check_contracts

from a3_network import Channel, NodeAddress, Node, Packet 
from a3_part1 import AbstractRing, AbstractTorus, AbstractStar


@check_contracts
class GreedyChannelRing(AbstractRing):
    """An implementation of the Greedy-Channel Ring Network.
    """

    def route_packet(self, current_address: NodeAddress, packet: Packet) -> Optional[Channel]:
        """Return the channel that the packet should traverse next, given that it has
        just arrived at the node with address current_address.

        That is, the returned channel has the node corresponding to current_address as
        one of its endpoints. Ideally, but not necessarily, traversing the returned channel
        helps get the given packet closer to its destination.

        Return None if the current_address is equal to the packet's destination!

        Preconditions:
        - current_address in self._nodes
        - packet.source in self._nodes
        - packet.destination in self._nodes
        """
        dest = packet.destination
        if current_address == dest:
            return None
        else:
            channels_lst = []

            curr_node = self._nodes[current_address]
            neighbour_add = curr_node.channels.keys()
            for address in neighbour_add:
                node = self._nodes[address]
                channel = node.channels[current_address]
                d = self.get_distance(address, dest)
                channels_lst.append((d, channel))

        return greedy_channel_select(channels_lst)

    def get_distance(self, n1: NodeAddress, n2: NodeAddress) -> int:
        """Return the shortest path distance between the two given node (addresses).

        Remember that path distance is measured as the number of channels/edges, not nodes.
        When n1 == n2, the shortest path distance is 0.

        Preconditions:
            - n1 in self._nodes
            - n2 in self._nodes
        """
        # compute k for ring
        k = len(self._nodes)

        if n1 == n2:
            return 0
        else:
            if n2 > n1:
                left_dist = k - (n2 - n1)
                right_dist = n2 - n1
            else:
                left_dist = n2 - n1
                right_dist = k - (n2 - n1)

            if left_dist >= right_dist:
                return right_dist
            else:
                return left_dist


@check_contracts
class GreedyChannelTorus(AbstractTorus):
    """An implementation of the Greedy-Channel Torus Network.
    """

    def route_packet(self, current_address: NodeAddress, packet: Packet) -> Optional[Channel]:
        """Return the channel that the packet should traverse next, given that it has
        just arrived at the node with address current_address.

        That is, the returned channel has the node corresponding to current_address as
        one of its endpoints. Ideally, but not necessarily, traversing the returned channel
        helps get the given packet closer to its destination.

        Return None if the current_address is equal to the packet's destination!

        Preconditions:
        - current_address in self._nodes
        - packet.source in self._nodes
        - packet.destination in self._nodes
        """
        dest = packet.destination
        if current_address == dest:
            return None
        else:
            channels_lst = []

            curr_node = self._nodes[current_address]
            neighbour_add = curr_node.channels.keys()
            for address in neighbour_add:
                node = self._nodes[address]
                channel = node.channels[current_address]
                d = self.get_distance(address, dest)
                channels_lst.append((d, channel))

        return greedy_channel_select(channels_lst)

    def get_distance(self, n1: NodeAddress, n2: NodeAddress) -> int:
        """Return the shortest path distance between the two given node (addresses).

        Remember that path distance is measured as the number of channels/edges, not nodes.
        When n1 == n2, the shortest path distance is 0.

        Preconditions:
            - n1 in self._nodes
            - n2 in self._nodes
        """
        # compute k for torus
        x_s, y_s = n1
        x_d, y_d = n2
        x_dist = self.get_ring_distance(x_s, x_d)
        y_dist = self.get_ring_distance(y_s, y_d)

        return x_dist + y_dist

    def get_ring_distance(self, n1: int, n2: int) -> int:
        """A helper method for get_distance"""
        # compute k for ring
        k = len(self._nodes)

        if n1 == n2:
            return 0
        else:
            if n2 > n1:
                left_dist = abs(k - (n2 - n1))
                right_dist = abs(n2 - n1)
            else:
                left_dist = abs(n2 - n1)
                right_dist = abs(k - (n2 - n1))

            if left_dist >= right_dist:
                return right_dist
            else:
                return left_dist


@check_contracts
class GreedyChannelStar(AbstractStar):
    """An implementation of the Greedy-Channel Star Network.
    """

    def route_packet(self, current_address: NodeAddress, packet: Packet) -> Optional[Channel]:
        """Return the channel that the packet should traverse next, given that it has
        just arrived at the node with address current_address.

        That is, the returned channel has the node corresponding to current_address as
        one of its endpoints. Ideally, but not necessarily, traversing the returned channel
        helps get the given packet closer to its destination.

        Return None if the current_address is equal to the packet's destination!

        Preconditions:
        - current_address in self._nodes
        - packet.source in self._nodes
        - packet.destination in self._nodes
        """
        dest = packet.destination
        if current_address == dest:
            return None
        else:
            channels_lst = []

            curr_node = self._nodes[current_address]
            neighbour_add = curr_node.channels.keys()
            for address in neighbour_add:
                node = self._nodes[address]
                channel = node.channels[current_address]
                d = self.get_distance(address, dest)
                channels_lst.append((d, channel))

        return greedy_channel_select(channels_lst)

    def get_distance(self, n1: NodeAddress, n2: NodeAddress) -> int:
        """Return the shortest path distance between the two given node (addresses).

        Remember that path distance is measured as the number of channels/edges, not nodes.
        When n1 == n2, the shortest path distance is 0.

        Preconditions:
            - n1 in self._nodes
            - n2 in self._nodes
        """
        # compute k for star
        length = len(self._nodes)
        k1 = 0
        for node in self._nodes.values():
            if len(node.channels) == length - 1:
                k1 += 1
        central_nodes = range(k1)

        if n1 == n2:
            return 0
        else:
            if n2 in central_nodes or n1 in central_nodes:
                return 1
            else:
                return 2


@check_contracts
def greedy_channel_select(channels: list[tuple[int, Channel]]) -> Channel:
    """Return the channel that minimizes the quantity described under "Greedy Channel Routing Algorithn"
    on the assignment handout.

    Each tuple in channels is of the form (d, channel), where d is the shortest-path distance
    from the neighbour to the packet's destination, and channel is the channel to that neighbour.

    Break ties as described on the assignment handout.

    Preconditions:
    - channels != []
    - all(tup[0] >= 0 for tup in channels)
    """
    min_dist = channels[0][0]
    min_score = min_dist + channels[0][1].total_occupancy()
    for d, channel in channels:
        channel_occupancy = channel.total_occupancy()
        score = d + channel_occupancy
        if score < min_score:
            min_score = score
            if d < min_dist:
                min_dist = d
    for d, c in channels:
        score = d + c.total_occupancy()
        if score != min_score:
            channels.remove((d, c))
    if len(channels) > 1:
        for d, c in channels:
            if d != min_dist:
                channels.remove((d, c))
    if len(channels) > 1:
        index = random.randint(0, len(channels))
        return channels[index][1]
    return channels[0][1]


###################################################################################################
# Question 2
###################################################################################################
@check_contracts
class GreedyPathRing(AbstractRing):
    """An implementation of the Greedy-Path Ring Network.
    """

    def route_packet(self, current_address: NodeAddress, packet: Packet) -> Optional[Channel]:
        """Return the channel that the packet should traverse next, given that it has
        just arrived at the node with address current_address.

        That is, the returned channel has the node corresponding to current_address as
        one of its endpoints. Ideally, but not necessarily, traversing the returned channel
        helps get the given packet closer to its destination.

        Return None if the current_address is equal to the packet's destination!

        Preconditions:
        - current_address in self._nodes
        - packet.source in self._nodes
        - packet.destination in self._nodes
        """
        dest = packet.destination
        if current_address == dest:
            return None
        else:
            channels_lst = self.find_paths(current_address, dest)
            return greedy_path_select(channels_lst)


@check_contracts
class GreedyPathTorus(AbstractTorus):
    """An implementation of the Greedy-Path Torus Network.
    """

    def route_packet(self, current_address: NodeAddress, packet: Packet) -> Optional[Channel]:
        """Return the channel that the packet should traverse next, given that it has
        just arrived at the node with address current_address.

        That is, the returned channel has the node corresponding to current_address as
        one of its endpoints. Ideally, but not necessarily, traversing the returned channel
        helps get the given packet closer to its destination.

        Return None if the current_address is equal to the packet's destination!

        Preconditions:
        - current_address in self._nodes
        - packet.source in self._nodes
        - packet.destination in self._nodes
        """
        dest = packet.destination
        if current_address == dest:
            return None
        else:
            channels_lst = self.find_paths(current_address, dest)
            return greedy_path_select(channels_lst)


@check_contracts
class GreedyPathStar(AbstractStar):
    """An implementation of the Greedy-Path Star Network.
    """

    def route_packet(self, current_address: NodeAddress, packet: Packet) -> Optional[Channel]:
        """Return the channel that the packet should traverse next, given that it has
        just arrived at the node with address current_address.

        That is, the returned channel has the node corresponding to current_address as
        one of its endpoints. Ideally, but not necessarily, traversing the returned channel
        helps get the given packet closer to its destination.

        Return None if the current_address is equal to the packet's destination!

        Preconditions:
        - current_address in self._nodes
        - packet.source in self._nodes
        - packet.destination in self._nodes
        """
        dest = packet.destination
        if current_address == dest:
            return None
        else:
            channels_lst = self.find_paths(current_address, dest)
            return greedy_path_select(channels_lst)


@check_contracts
def greedy_path_select(paths: list[list[Channel]]) -> Channel:
    """Return the first channel in the path that minimizes the quantity described under "Greedy Path Routing Algorithn"
    on the assignment handout.

    Break ties as described on the assignment handout.

    Preconditions:
    - paths != []
    - every element of paths is a valid path
    - every path in paths starts at the same node
    - every path in paths ends at the same node
    """
    min_len = len(paths[0])
    min_score = compute_path_score(paths[0])
    for p in paths:
        score = compute_path_score(p)
        length = len(p)
        if score < min_score:
            min_score = score
            if length < min_len:
                min_len = length
    for p in paths:
        score = compute_path_score(p)
        if score != min_score:
            paths.remove(p)
    if len(paths) > 1:
        for p in paths:
            if len(p) != min_len:
                paths.remove(p)
    if len(paths) > 1:
        index = random.randint(0, len(paths))
        return paths[index][0]
    return paths[0][0]


@check_contracts
def compute_path_score(path: list[Channel]) -> int:
    """Return the "Greedy Path Routing Algorithm" path score for the given path.

    See assignment handout for details.

    Preconditions:
        - path is a valid path
        - path != []
    """
    score = 0
    k = len(path)
    for i, c in enumerate(path):
        score += max(c.total_occupancy() - i, 0)
    return k + score


if __name__ == '__main__':
    import doctest

    doctest.testmod(verbose=True)

    import python_ta

    python_ta.check_all(config={
        'max-line-length': 120,
        'extra-imports': ['random', 'a3_network', 'a3_part1'],
        'disable': ['unused-import']
    })
