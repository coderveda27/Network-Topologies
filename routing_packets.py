import random
from typing import Optional

from python_ta.contracts import check_contracts


from a3_network import Channel, Packet, NodeAddress, Node
from a3_part1 import AbstractRing, AbstractStar, AbstractTorus


@check_contracts
class AlwaysRightRing(AbstractRing):
    """An implementation of the Always-Right Ring Network.

    Note that you only need to implement the route_packet method for this class.
    It will inherit the initializer from AbstractRing and the other useful methods
    from AbstractNetwork!
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
        k = self.get_radix()
        if current_address == dest:
            return None
        else:
            curr_node = self._nodes[current_address]
            if current_address == k - 1:
                next_address = (current_address + 1) % k
            else:
                next_address = (current_address + 1)

            return curr_node.channels[next_address]

    def get_radix(self) -> int:
        """ Return the radix for the given AlwaysRightRing """
        # k is the max value that node 0 is connected to plus 1
        zero_node = self._nodes[0]
        value = max(zero_node.channels)
        return value + 1


@check_contracts
class ShortestPathRing(AbstractRing):
    """An implementation of the Shortest-Path Ring Network.

    Note that you only need to implement the route_packet method for this class.
    It will inherit the initializer from AbstractRing and the other useful methods
    from AbstractNetwork!
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
        k = self.get_radix()
        if current_address == dest:
            return None
        else:
            curr_node = self._nodes[current_address]
            left_address = (current_address - 1) % k
            right_address = (current_address + 1) % k
            if left_address == 0:
                left_dist = 1
            else:
                left_dist = abs(dest - left_address)
            if right_address == k - 1:
                right_dist = 1
            else:
                right_dist = abs(dest - right_address)

            if left_dist >= right_dist:  # go right even if there is a tie
                next_address = right_address
            else:  # left_dist < right_dist  go left
                next_address = left_address
        return curr_node.channels[next_address]

    def get_radix(self) -> int:
        """Return the radix for the given AlwaysRightRing"""
        zero_node = self._nodes[0]
        value = max(zero_node.channels)
        return value + 1
        # easier to call len()


@check_contracts
class ShortestPathTorus(AbstractTorus):
    """An implementation of the Shortest-Path Torus Network.

    Note that you only need to implement the route_packet method for this class.
    It will inherit the initializer from AbstractTorus and the other useful methods
    from AbstractNetwork!
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

        Implementation notes:
            - To determine the next node address, you'll need to recover the radix of this torus.
              There are a few different approaches for this, but if you want to calculate a square
              root, we haven't allowed you to import math.sqrt, but you can use "** 0.5" instead.
        """
        dest = packet.destination
        if current_address == dest:
            return None
        else:
            curr_node = self._nodes[current_address]
            k = int(len(self._nodes) ** 0.5)
            x_s = current_address[0]
            y_s = current_address[1]
            x_d = dest[0]
            y_d = dest[1]
            if x_s != x_d:
                is_right = self.get_direction(x_s, x_d, k)
                if is_right:
                    x_address = (x_s + 1) % k
                else:
                    x_address = (x_s - 1) % k
                return curr_node.channels[(x_address, y_s)]
            else:
                is_up = self.get_direction(y_s, y_d, k)
                if is_up:
                    y_address = (y_s + 1) % k
                else:
                    y_address = (y_s - 1) % k
                return curr_node.channels[(x_s, y_address)]

    def get_direction(self, src: int, dst: int, k: int) -> bool:
        """..."""
        # if true go inc else go dec
        if dst > src:
            left_dist = k - (dst - src)
            right_dist = dst - src
        else:
            left_dist = src - dst
            right_dist = k - (src - dst)
        return right_dist <= left_dist


@check_contracts
class ShortestPathStar(AbstractStar):
    """An implementation of the Shortest-Path Star Network.

    Note that you only need to implement the route_packet method for this class.
    It will inherit the initializer from AbstractStar and the other useful methods
    from AbstractNetwork!
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
        k1 = self.get_radii()
        central_nodes = range(k1)
        # print(central_nodes)
        # outer_nodes = range(k1, k1 + k2)
        if current_address == dest:
            return None
        else:
            curr_node = self._nodes[current_address]
            if packet.source in central_nodes:
                next_address = dest
                return curr_node.channels[next_address]
            elif dest in central_nodes:
                next_address = dest
                return curr_node.channels[next_address]
            else:
                random_central_address = random.randint(0, k1 - 1)
                return curr_node.channels[random_central_address]

    def get_radii(self) -> int:
        """ Return a tuple of the number of central nodes and the number of outer nodes """
        length = len(self._nodes)
        k1 = 0
        for node in self._nodes.values():
            if len(node.channels) == length - 1:
                k1 += 1
        # k2 = length - k1
        # return (k1, k2)
        return k1


if __name__ == '__main__':
    import doctest

    doctest.testmod(verbose=True)

    import python_ta

    python_ta.check_all(config={
        'max-line-length': 120,
        'extra-imports': ['random', 'a3_network', 'a3_part1'],
        'disable': ['unused-import']
    })
