from __future__ import annotations
from dataclasses import dataclass, field
import heapq
import random
from typing import Optional

from python_ta.contracts import check_contracts
 
from a3_network import Channel, NodeAddress, AbstractNetwork, Packet
from a3_part1 import AbstractRing, AbstractTorus


###################################################################################################
# The main NetworkSimulation class
###################################################################################################
@check_contracts
class NetworkSimulation:
    """A network simulation that can run a particular simulation configuration on a given network.
    """
    _network: AbstractNetwork
    _current_channels: set[Channel]
    _current_time: int

    def __init__(self, network: AbstractNetwork) -> None:
        """Initialize this simulation with the given network."""
        self._network = network
        self._current_channels = set()
        self._current_time = 0

    def run_with_initial_packets(self, packets: list[tuple[int, Packet]],
                                 print_events: bool = False) -> list[PacketStats]:
        """Run a simulation using the given packet data. Return a list of statistics for each packet.

        Each element of packets is a tuple (timestamp, packet), indicating that the given packet
        should be added to the simulation at the given timestamp.

        Pass print_events=True to print a record of each event when it is processed.

        Preconditions:
        - packets != []
        - all(packet_data[0] >= 0 for packet_data in packets)
        """
        stats = _StatisticsTracker()
        initial_events = [_NewPacketEvent(timestamp, packet) for timestamp, packet in packets]

        events = _EventQueueHeap()
        for event in initial_events:
            events.enqueue(event)

        self._current_channels = set()
        self._current_time = 0

        while not events.is_empty():
            event = events.dequeue()
            if print_events:
                print(event)

            if event.timestamp != self._current_time:
                self._current_channels = set()
                self._current_time = event.timestamp

            new_events = event.handle_event(self._network, stats, self._current_channels)
            for new_event in new_events:
                events.enqueue(new_event)

        return list(stats.packets.values())


@check_contracts
def generate_random_packets(
        network: AbstractNetwork,
        n: int,
        p: float,
        pattern_type: str = 'random') -> list[tuple[int, Packet]]:
    """Randomly generate a list of n packets and timestamps for when each packet should be created.

    Packet sources are chosen uniformly at random from all network nodes.

    If pattern_type == 'random' (the default), the packet destinations are chosen uniformly at random
    (independent of their source). If pattern_type == 'hard', the packet dstinations are chosen
    to maximize the shortest-path distance to the packet's source.

    NOTE: we have only provided code to support the 'random' option. If you'd like to try the 'hard'
    option, you must implement the HardTraffic class at the bottom of this file. Doing so is optional.

    Preconditions:
        - n >= 1
        - 0.0 < p <= 1.0
        - pattern_type in {'random', 'hard'}
    """
    if pattern_type == 'random':
        pattern = _UniformRandomTraffic(network)
    else:  # pattern_type == 'hard'
        pattern = _HardTraffic(network)

    packet_id = 0
    timestamp = 0
    packets = []

    while len(packets) < n:
        for source in network.get_node_addresses():
            if random.uniform(0.0, 1.0) <= p:
                destination = pattern.generate_destination(source)
                packet = Packet(packet_id, source, destination)
                packet_id += 1
                packets.append((timestamp, packet))

                if len(packets) == n:
                    return packets

        timestamp += 1

    return packets


###################################################################################################
# Simulation Event classes
###################################################################################################
class _Event:
    """An abstract class representing an event in our simulation.

    Instance Attributes:
        - timestamp: the start time (in cycles) of the event

    Representation Invariants:
        - self.timestamp >= 0
    """
    timestamp: int

    def __init__(self, timestamp: int) -> None:
        """Initialize this event with the given timestamp.

        Preconditions:
            - timestamp >= 0
        """
        self.timestamp = timestamp

    def handle_event(self, network: AbstractNetwork, stats: _StatisticsTracker,
                     current_channels: set[Channel]) -> list[_Event]:
        """Mutate the given interconnection network to process this event.

        Return a new list of new events created by processing this event.
        Update the given stats to reflect the new event.
        """
        raise NotImplementedError


class _NewPacketEvent(_Event):
    """An event for when a new packet is created in the network."""
    _packet: Packet

    def __init__(self, timestamp: int, packet: Packet) -> None:
        """Initialize this event with the given timestamp and packet.


        Preconditions:
            - timestamp >= 0
        """
        _Event.__init__(self, timestamp)
        self._packet = packet

    def handle_event(self, network: AbstractNetwork, stats: _StatisticsTracker,
                     _current_channels: set[Channel]) -> list[_Event]:
        """Mutate the given network to process this event.

        Return a new list of new events created by processing this event.
        Update the given stats to reflect the new event.

        Preconditions:
        - self._packet.source in network._nodes
        - self._packet.destination in network._nodes
        """
        stats.update(self.timestamp, self._packet.source, self._packet)

        next_channel = network.add_new_packet(self._packet)

        # If the packet is the occupant, make sure the channel gets activated at the next cycle.
        # If the packet was added to the buffer, no need to trigger a new event---an ActivateChannelEvent
        # for the channel must already have been enqueued.
        if next_channel.occupant is self._packet:
            return [_ActivateChannelEvent(self.timestamp + 1, next_channel)]
        else:
            return []

    def __str__(self) -> str:
        """Return a string representation of this event."""
        return f'[{self.timestamp}] New packet {self._packet.identifier}: '\
               f'{self._packet.source} -> {self._packet.destination}'


class _ActivateChannelEvent(_Event):
    """An event for when a packet traverses a channel in the network."""
    _channel: Channel
    _packet: Packet

    def __init__(self, timestamp: int, channel: Channel) -> None:
        """Initialize this event with the given timestamp and channel being traversed.

        Preconditions:
            - timestamp >= 0
        """
        _Event.__init__(self, timestamp)
        self._channel = channel
        self._packet = channel.occupant

    def handle_event(self, network: AbstractNetwork, stats: _StatisticsTracker,
                     current_channels: set[Channel]) -> list[_Event]:
        """Mutate the given network to process this event.

        Return a new list of new events created by processing this event.
        Update the given stats to reflect the new event.
        """
        # Skip this event if the channel has already been activated in this timestep
        if self._channel in current_channels:
            return []
        else:
            current_channels.add(self._channel)

        stats.update(self.timestamp, self._packet.next_stop.address, self._packet)

        new_channel = network.activate_channel(self._channel)
        new_events = []

        # If the channel has a new occupant, it should be activated in the next cycle.
        if self._channel.occupant is not None:
            new_events.append(_ActivateChannelEvent(self.timestamp + 1, self._channel))

        # If the old occupant has moved into a new channel as that channel's occupant,
        # the new channel should also be activated in the next cycle.
        if new_channel is not None and new_channel.occupant is self._packet:
            new_events.append(_ActivateChannelEvent(self.timestamp + 1, new_channel))

        return new_events

    def __str__(self) -> str:
        """Return a string representation of this event."""
        # Note: This method must be called *before* the handle_event method. (Because self._packet.next_stop
        # is modified after the packet moves to a different channel.)
        ends = {node.address for node in self._channel.endpoints}
        return f'[{self.timestamp}] Channel {ends} activated. Packet {self._packet.identifier} '\
               f'moved to {self._packet.next_stop.address}'


class _EventQueueHeap:
    """A heap of events that can be dequeued in cycle order."""
    # Private Instance Attributes:
    #   - _events: a heap of events
    #   - _entry_count: a non-decreasing counter storing all events ever
    #                   enqueued (used to break ties for heapq)
    _events: list[tuple[int, int, _Event]]
    _entry_count: int

    def __init__(self) -> None:
        """Initialize a new and empty event queue."""
        self._events = []
        self._entry_count = 0

    def is_empty(self) -> bool:
        """Return whether this event queue contains no items."""
        return self._events == []

    def enqueue(self, event: _Event) -> None:
        """Add an event to this event queue."""
        heapq.heappush(self._events, (event.timestamp, self._entry_count, event))
        self._entry_count += 1

    def dequeue(self) -> _Event:
        """Remove and return the earliest event in this event queue.

        Preconditions:
        - not self.is_empty()
        """
        _, _, event = heapq.heappop(self._events)
        return event


###############################################################################
# Classes for tracking packet statistics
###############################################################################
class _StatisticsTracker:
    """A class to keep track of packet statistics."""
    packets: dict[int, PacketStats]

    def __init__(self) -> None:
        """Initialize this object."""
        self.packets = {}

    def update(self, timestamp: int, node: NodeAddress, packet: Packet) -> None:
        """Update the statistics based on the arrival of packet at the given node and timestamp."""
        if packet.identifier not in self.packets:
            self.packets[packet.identifier] = PacketStats(identifier=packet.identifier, created_at=timestamp)

        self.packets[packet.identifier].route.append(node)

        if node == packet.destination:
            self.packets[packet.identifier].arrived_at = timestamp


@dataclass
class PacketStats:
    """A data class to track some statistics for a single packet during a simulation.

    Instance Attributes:
        - identifier: The packet identifier.
        - created_at: The timestamp when the packet was created.
        - arrived_at: The timestamp when the packet arrived at its destination,
                      or None if the packet has not yet arrived.
        - route: A list of the NodeAddresses the packet has visited.
    """
    identifier: int
    created_at: int
    arrived_at: Optional[int] = None
    # The following sets the default to be an empty list. Understanding dataclasses.field
    # is beyond the scope of this course.
    route: list[NodeAddress] = field(default_factory=list)


###################################################################################################
# Classes for generating traffic patterns
###################################################################################################
class _TrafficPattern:
    """An abstract class representing an algorithm for generating traffic patterns in a network simulation.
    """
    def generate(self) -> tuple[NodeAddress, NodeAddress]:
        """Return a tuple of two node addresses where the first is the source and the second is the destination.
        """
        raise NotImplementedError

    def generate_destination(self, source: NodeAddress) -> NodeAddress:
        """Return a destination address for the given source address.
        """
        raise NotImplementedError


class _UniformRandomTraffic(_TrafficPattern):
    """A traffic pattern that selects packet source/destination locations uniformly at random across the network.
    """
    _node_ids: list[NodeAddress]

    def __init__(self, network: AbstractNetwork) -> None:
        """Initialize this traffic generator with the given network.
        """
        self._node_ids = list(network.get_node_addresses())

    def generate(self) -> tuple[NodeAddress, NodeAddress]:
        """Return a tuple of two node addresses where the first is the source and the second is the destination.
        """
        return random.sample(self._node_ids, 2)

    def generate_destination(self, source: NodeAddress) -> NodeAddress:
        """Return a destination address for the given source address.
        """
        choices = [address for address in self._node_ids if address != source]
        destination = random.choice(choices)

        return destination


class _HardTraffic(_TrafficPattern):
    """A class that tries to select source/destination pairs that maximize the shortest-path
    distance between them.

    It is OPTIONAL for you to implement this class.
    """
    _node_ids: list[NodeAddress]
    _network: AbstractNetwork

    def __init__(self, network: AbstractNetwork) -> None:
        """Initialize this traffic generator with the given network.
        """
        self._node_ids = list(network.get_node_addresses())
        self._network = network

    def generate(self) -> tuple[NodeAddress, NodeAddress]:
        """Return a tuple of two node addresses where the first is the source and the second is the destination.
        """
        source = random.choice(self._node_ids)
        return source, self.generate_destination(source)

    def generate_destination(self, source: NodeAddress) -> NodeAddress:
        """Return a destination address for the given source address.

        It is OPTIONAL to implement this method.
        If you'd like to attempt it, we've provided some structure and hints in the body below.
        Note that using an if statement to distinguish between types of graph topology is not great design
        (better to add a new abstract method to AbstractNetwork). We haven't done so for this assignment
        because this part is optional.
        """
        if isinstance(self._network, AbstractRing):
            # Pick the destination that's roughly (radix // 2) away from source
            destination = ...
        elif isinstance(self._network, AbstractTorus):
            # Pick the destination that's roughly (radix // 2) away from source in both dimensions
            destination = ...
        else:  # isinstance(self._network, AbstractStar)
            # Pick an outer node (that's not the same as the source node)
            destination = ...

        return destination


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'extra-imports': ['heapq', 'random', 'a3_network', 'a3_part1'],
        'allowed-io': ['NetworkSimulation.run_with_initial_packets'],
        'max-nested-blocks': 4
    })
