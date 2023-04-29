from python_ta.contracts import check_contracts

from a3_network import AbstractNetwork, Node, NodeAddress


@check_contracts
class AbstractRing(AbstractNetwork):
    """An abstract network with a ring topology.

    See the assignment handout for a description of this and other network topologies you're implementing.

    Representation Invariants:
        - all(isinstance(address, int) for address in self._nodes)
    """

    def __init__(self, k: int) -> None:
        """Initialize this network with a ring topology of radix k.

        Preconditions:
            - k >= 3
        """
        AbstractNetwork.__init__(self)
        # self._k = k
        # self._nodes = {}
        for i in range(k):
            self.add_node(i)
            if i > 0:
                self.add_channel(i, i - 1)
            if i == k - 1:
                self.add_channel(0, k - 1)


@check_contracts
class AbstractTorus(AbstractNetwork):
    """An abstract network with a torus topology.

    See the assignment handout for a description of this and other network topologies you're implementing.

    Representation Invariants:
        - all(isinstance(address, tuple) for address in self._nodes)
    """

    def __init__(self, k: int) -> None:
        """Initialize this network with a torus topology of radix k.

        Preconditions:
            - k >= 3
        """
        AbstractNetwork.__init__(self)
        # self._k = k
        # self._nodes = {}
        r = k - 1
        for x in range(k):
            for y in range(k):
                self.add_node((x, y))
                if y > 0:
                    self.add_channel((x, y), (x, y - 1))
                if y == r:
                    self.add_channel((x, y), (x, y - r))
                if x > 0:
                    self.add_channel((x, y), (x - 1, y))
                if x == r:
                    self.add_channel((x, y), (x - r, y))


@check_contracts
class AbstractStar(AbstractNetwork):
    """An abstract network with a star topology.

    A star topology has k1 central nodes that are all adjacent to each other and k2 outer nodes that
    are each adjacent to all central nodes.

    See the assignment handout for a description of this and other network topologies you're implementing.

    Private Instance Attributes (in addition to _nodes from AbstractNetwork):
        - _num_central: the number of central nodes
        - _num_outer: the number of outer nodes

    Representation Invariants:
        - all(isinstance(address, int) for address in self._nodes)
        - self._num_central >= 1
        - self._num_outer >= 1
    """
    _num_central: int
    _num_outer: int

    def __init__(self, k1: int, k2: int) -> None:
        """Initialize this network with a star topology of k1 central nodes and k2 outer nodes.

        Preconditions:
            - k1 >= 1
            - k2 >= 1

        Implementation note:
            - In addition to initialzing self._nodes, make sure to initialize the other two
              instance attributes described in the class docstring.
        """
        AbstractNetwork.__init__(self)
        self._num_central = k1
        self._num_outer = k2
        # self._nodes = {}

        for i in range(k1):
            self.add_node(i)
            for h in range(i):
                self.add_channel(h, i)
        for j in range(k1, k1 + k2):
            self.add_node(j)
            for c in range(k1):
                self.add_channel(c, j)


if __name__ == '__main__':
    import doctest

    doctest.testmod(verbose=True)


    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'extra-imports': ['a3_network'],
        'disable': ['abstract-method', 'unused-import']
    })
