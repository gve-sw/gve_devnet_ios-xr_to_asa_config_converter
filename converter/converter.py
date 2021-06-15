#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (c) 2021 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

__author__ = "Josh Ingeniero <jingenie@cisco.com>"
__copyright__ = "Copyright (c) 2021 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"

import re
import socket
import struct
import os

object_group_port = '^object-group port '
object_group_network_ipv4 = '^object-group network ipv4 '
object_group_network_ipv6 = '^object-group network ipv6 '
acl_ipv4 = '^ipv4 access-list '
acl_ipv6 = '^ipv6 access-list '


def cidr_to_netmask(cidr):
    network, net_bits = cidr.split('/')
    host_bits = 32 - int(net_bits)
    netmask = socket.inet_ntoa(struct.pack('!I', (1 << 32) - (1 << host_bits)))
    return network, netmask


def conversion(input_file, output_file):
    with open(input_file) as infile:
        with open(output_file, 'w') as outfile:
            current_command = ''
            details = ''
            count = 0
            for line in infile:
                count = count + 1
                try:
                    if re.match(object_group_port, line):
                        details = re.split(object_group_port, line)[1].strip(' ').rstrip('\n')
                        command = f"object-group service {details} tcp-udp\n"
                        outfile.writelines([command])
                        current_command = 'object_group_port'
                    elif re.match(object_group_network_ipv4, line):
                        details = re.split(object_group_network_ipv4, line)[1].strip(' ')
                        command = f"object-group network {details}"
                        outfile.writelines([command])
                        current_command = 'object_group_network_ipv4'
                    elif re.match(object_group_network_ipv6, line):
                        details = re.split(object_group_network_ipv6, line)[1].strip(' ')
                        command = f"object-group network {details}"
                        outfile.writelines([command])
                        current_command = 'object_group_network_ipv6'
                    elif re.match(acl_ipv4, line):
                        details = re.split(acl_ipv4, line)[1].strip(' ').rstrip('\n')
                        details = f"access-list {details} line "
                        current_command = 'acl_ipv4'
                    elif re.match(acl_ipv6, line):
                        details = re.split(acl_ipv6, line)[1].strip(' ').rstrip('\n')
                        details = f"access-list {details} line "
                        current_command = 'acl_ipv6'
                    elif re.match('^!$', line):
                        details = ''
                        current_command = ''
                        outfile.writelines(['!\n'])
                    else:
                        if current_command == 'acl_ipv4':
                            acl_details = line.lstrip().split(' ', 2)
                            number = acl_details[0]
                            acl_command = acl_details[1]
                            acl_details = acl_details[2]
                            if 'net-group' in acl_details:
                                acl_details = re.sub('net-group', 'object-group', acl_details)
                            if 'port-group' in acl_details:
                                acl_details = re.sub('port-group', 'object-group', acl_details)
                            if 'established' in acl_details:
                                acl_details = re.sub('established', '', acl_details)
                            if 'counter legacy-modbus' in acl_details:
                                acl_details = re.sub('counter legacy-modbus', '', acl_details)
                            if re.match('^remark', acl_command):
                                outfile.writelines([f"{details}{number} {acl_command} {acl_details}"])
                            elif re.match('^permit', acl_command):
                                outfile.writelines([f"{details}{number} extended {acl_command} {acl_details}"])
                            elif re.match('^deny', acl_command):
                                outfile.writelines([f"{details}{number} extended {acl_command} {acl_details}"])
                        elif current_command == 'acl_ipv6':
                            acl_details = line.lstrip().split(' ', 2)
                            number = acl_details[0]
                            acl_command = acl_details[1]
                            acl_details = acl_details[2]
                            if 'net-group' in acl_details:
                                acl_details = re.sub('net-group', 'object-group', acl_details)
                            if 'port-group' in acl_details:
                                acl_details = re.sub('port-group', 'object-group', acl_details)
                            if 'established' in acl_details:
                                acl_details = re.sub('established', '', acl_details)
                            if 'counter legacy-modbus' in acl_details:
                                acl_details = re.sub('counter legacy-modbus', '', acl_details)
                            if re.match('^remark', acl_command):
                                outfile.writelines([f"{details}{number} {acl_command} {acl_details}"])
                            elif re.match('^permit', acl_command):
                                outfile.writelines([f"{details}{number} {acl_command} {acl_details}"])
                            elif re.match('^deny', acl_command):
                                outfile.writelines([f"{details}{number} {acl_command} {acl_details}"])
                        elif current_command == 'object_group_port':
                            details = line.lstrip()
                            command = f"port-object {details}"
                            outfile.writelines([command])
                        elif current_command == 'object_group_network_ipv4':
                            ip_cidr = cidr_to_netmask(line.lstrip())
                            command = f"network-object {ip_cidr[0]} {ip_cidr[1]}\n"
                            outfile.writelines([command])
                        elif current_command == 'object_group_network_ipv6':
                            command = f"network-object {line.lstrip()}"
                            outfile.writelines([command])
                except Exception as e:
                    print(f"ERROR {e} at Line {count} - {line}")


if __name__ == '__main__':
    print('*'*30)
    print('Welcome to the IOS-XR to ASA Conversion Script')
    input_file = input('Please enter the input filename: ')
    output_file = input('Please enter the output filename: ')
    while(os.path.exists(output_file)):
        output_file = input('File exists!!! Enter another output filename: ')
    print(f'Starting conversion from {input_file} to {output_file}!')
    print('*'*30)
    conversion(input_file, output_file)
    print('*'*30)
    print(f'Conversion complete! Check {output_file}!')
