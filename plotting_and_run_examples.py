import csv
from typing import Optional

import plotly.graph_objects as go

from python_ta.contracts import check_contracts

from a3_network import AbstractNetwork, Packet, NodeAddress, Node
from a3_simulation import NetworkSimulation, PacketStats

from a3_part2 import AlwaysRightRing, ShortestPathRing, ShortestPathTorus, ShortestPathStar
from a3_part4 import GreedyChannelRing, GreedyChannelTorus, GreedyChannelStar, \
    GreedyPathRing, GreedyPathTorus, GreedyPathStar


def run_example() -> list[PacketStats]:
    """Run an example simulation.
 
    You may, but are not required to, change the code in this example to experiment with the simulation.
    """
    network = AlwaysRightRing(5)
    simulation = NetworkSimulation(network)
    packets = [(0, Packet(1, 0, 4))]
    return simulation.run_with_initial_packets(packets, print_events=True)


@check_contracts
def read_packet_csv(csv_file: str) -> tuple[AbstractNetwork, list[tuple[int, Packet]]]:
    """Load network and packet data from a CSV file.

    Return a tuple of two values:
        - the first element is the network created from the specification in the first line
          of the CSV file
        - the second element is a list of tuples, where each tuple is of the form (timestamp, packet),
          created from all other lines of the CSV file

    Preconditions:
        - csv_file refers to a valid CSV file 
    """
    with open(csv_file) as file:
        reader = csv.reader(file)
        header = file.readline().strip().split(',')
        network_type = header[0]

        if network_type not in {'ShortestPathStar', 'GreedyChannelStar', 'GreedyPathStar'}:
            network_arg = int(header[1])
            if network_type == 'AlwaysRightRing':
                network_type_object = AlwaysRightRing(network_arg)
            elif network_type == 'ShortestPathRing':
                network_type_object = ShortestPathRing(network_arg)
            elif network_type == 'ShortestPathTorus':
                network_type_object = ShortestPathTorus(network_arg)
            elif network_type == 'GreedyChannelRing':
                network_type_object = GreedyChannelRing(network_arg)
            elif network_type == 'GreedyChannelTorus':
                network_type_object = GreedyChannelTorus(network_arg)
            elif network_type == 'GreedyPathRing':
                network_type_object = GreedyPathRing(network_arg)
            else:
                network_type_object = GreedyPathTorus(network_arg)
        else:
            network_arg_1 = int(header[1])
            network_arg_2 = int(header[2])
            if network_type == 'GreedyChannelStar':
                network_type_object = GreedyChannelStar(network_arg_1, network_arg_2)
            elif network_type == 'GreedyPathStar':
                network_type_object = GreedyPathStar(network_arg_1, network_arg_2)
            else:
                network_type_object = ShortestPathStar(network_arg_1, network_arg_2)

        lst = []
        counter = 0
        for network in reader:
            timestamp = int(network[0])

            if network_type in {'ShortestPathTorus', 'GreedyChannelTorus', 'GreedyPathTorus'}:
                source = (int(network[1]), int(network[2]))
                destination = (int(network[3]), int(network[4]))
            else:
                source = int(network[1])
                destination = int(network[2])

            lst.append((timestamp, Packet(counter, source, destination)))
            counter += 1
        return (network_type_object, lst)


def plot_packet_latencies(packet_stats: list[PacketStats]) -> None:
    """Use plotly to plot a histogram of the packet latencies for the given stats.

    The packet latency is defined as the difference between the arrived_at and created_at times.
    It represents the total amount of time the packet spent in the network.

    We have provided some starter code for you.

    Preconditions:
        - packet_stats != []
    """
    packet_latencies = [stats.arrived_at - stats.created_at for stats in packet_stats]

    fig = go.Figure(data=[
        go.Histogram(
            x=packet_latencies,
        )
    ])
    # Set the graph title and axis labels
    fig.update_layout(
        title='Packet Latency Histogram',
        xaxis_title_text='Packet Latency',
        yaxis_title_text='Count'
    )
    fig.show()


def plot_route_lengths(packet_stats: list[PacketStats]) -> None:
    """Use plotly to plot a histogram of the route lengths for the given stats.

    The route length is defined as the number of channels traversed by the packet to arrive at its destination.

    We have not provided any code, but your implementation should be pretty similar to plot_packet_latencies.
    Remember to update the histogram title and axis labels!

    Preconditions:
        - packet_stats != []
    """
    route_length = []
    for stat in packet_stats:
        route_length.append(len(stat.route) - 1)

    fig = go.Figure(data=[
        go.Histogram(
            x=route_length,
        )
    ])

    # Set the graph title and axis labels
    fig.update_layout(
        title='Route Length Histogram',
        xaxis_title_text='Route Length',
        yaxis_title_text='Count'
    )
    fig.show()


@check_contracts
def part3_runner(csv_file: str, plot_type: Optional[str] = None) -> dict[str, float]:
    """Run a simulation based on the data from the given csv file.

    If plot_type == 'latencies', plot a histogram of the packet latencies.
    If plot_type == 'route-lengths', plot a histogram of the packet route lengths.

    Return a dictionary with two keys:
        - 'average latency', whose associated value is the average packet latency
        - 'average route length', whose associated value is the average route length

    Preconditions:
        - csv_file refers to a valid CSV file in the format described on the assignment handout
        - plot_type in {None, 'latencies', 'route-lengths'}
    """
    data = read_packet_csv(csv_file)
    network = NetworkSimulation(data[0])

    packet = data[1]
    packet_stats = network.run_with_initial_packets(packet, print_events=True)
    avg_latency = sum(stats.arrived_at - stats.created_at for stats in packet_stats) / len(packet_stats)
    avg_route_length = sum(len(stats.route) - 1 for stats in packet_stats) / len(packet_stats)

    if plot_type == 'latencies':
        plot_packet_latencies(packet_stats)
    elif plot_type == 'route-lengths':
        plot_route_lengths(packet_stats)

    return {
        'average latency': avg_latency,
        'average route length': avg_route_length
    }




if __name__ == '__main__':
    # Here is a sample call to part3_runner. Feel free to change it or add new calls!
    print(part3_runner('data/ring_single.csv', 'latencies'))


    import python_ta

    python_ta.check_all(config={
        'max-line-length': 120,
        'extra-imports': ['csv', 'plotly.graph_objects', 'a3_network', 'a3_simulation', 'a3_part2', 'a3_part4'],
        'disable': ['unused-import'],
        'allowed-io': ['read_packet_csv', 'part3_runner_optional']
    })
