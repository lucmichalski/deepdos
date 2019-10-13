"""
    Module for linux based firewalls
"""
import time

import iptc
from deepdos.firewall.firewall import Firewall
from deepdos.firewall.offender import Offender

# Export the iptables connection error
IPTCError = iptc.ip4tc.IPTCError


class IPtable(Firewall):
    """
        Linux based firewall class

        Args:
            interface - The network interface we're writing rules for.
            interface_data - A dictionary containing data about the interface.
            naughty_count - The maxmimum amount of offenses a flow can have before being banned.

        Properties:
            filter_table - The iptables filter table, where input input and output chains are located.
            input_chain  - The input chain that controls all input rules.
            output_chain - The output chain that controls all output rules.
    """

    def __init__(self, interface: str, interface_data: dict, naughty_count: int):
        super().__init__(interface, interface_data, naughty_count)
        # Instantiate the filter table with the input and output chains readily accessible
        # for writing rules.
        self.filter_table = iptc.Table(iptc.Table.FILTER)
        self.input_chain = iptc.Chain(self.filter_table, "INPUT")
        self.output_chain = iptc.Chain(self.filter_table, "OUTPUT")

    def create_rule(self, offender: Offender) -> None:
        """
            Create a firewall rule that will disable communication between the from_ip and
            to_ip on the desired interface for the specified protocol.

            Args:
                offender - The offending flow to write a rule for.
        """
        # Currently stub out the firewall rule creation
        self.logger.info(f"Creating rule for: {offender.connection}")
        return

        # Unpack some variables
        interface_info = self.interface_data[self.ip_version]
        local_ip = interface_info["address"]

        # Get the from ip and to ip from the offendesr src
        from_ip, to_ip = offender.src.split("/")

        ip = from_ip if from_ip == local_ip else to_ip

        # Create a rule to drop packets for this connection on the currently hooked
        # up interface
        rule = iptc.Rule()
        rule.in_interface = self.interface
        rule.src = ip
        rule.target = iptc.Target(rule, "DROP")

        # Iterate through all of the communication channels
        # and add matches for them
        for port, protocol in list(offender.port_mappings):
            match = iptc.Match(rule, protocol)
            match.dport = port
            rule.add_match(match)

        # Choose which chain to create the rule for
        if offender.outgoing:
            self.output_chain.insert_rule(rule)
            self.output_banned[rule.src] = time.time() // 60
        else:
            self.input_chain.insert_rule(rule)
            self.input_banned[rule.src] = time.time() // 60

    def remove_rule(self):
        """
        Remove a rule from the table. Still waiting to be written
        """
        return 1
