"""The ADVA/PoliMi SDN course functions."""

from logging import getLogger

import policonf.netconf
from policonf.magic import course_function
from ncclient.manager import connect as ncconnect


# Other libraries
from lxml import etree
# from lxml.etree import tounicode
from ncclient.xml_ import to_ele, to_xml
import questionary
from getpass import getpass
import time
import sys

#: The logger instance for mod:`policonf`.
LOG = getLogger(__package__)

#: The NETCONF client instance.
NETCONF = policonf.netconf.NETCONF()

USERNAME = 'admin'
PASSWORD = 'CHGME.1a'


#TODO: in the iPython environment: %load_ext policonf --> %polirun 0 (or any other shortcut)


###################################################################################################
#                                    AUXILIARY FUNCTIONS                                          #
###################################################################################################
def choose_host():
    host = questionary.select(
        "Please choose a host:",
        choices=[
            '10.11.12.19',
            '10.11.12.23'
        ]).ask()
    return host


def set_frequency_and_power_filter(host, ncc, interface_name, tags):
    print(100*'*')
    LOG.info("Getting frequency and/or power...")
    print(100*'*')

    interface_filter = '''
        <managed-element>
            <interface>
                <name>''' + interface_name + '''</name>
                <physical-interface/>
            </interface>
        </managed-element>
    '''

    reply = ncc.get(filter=('subtree', interface_filter))

    if type(tags) != type([]):
        tags_list = []
        tags_list.append(tags)
    else:
        tags_list = tags

    for tag in tags_list:
        print(tag)
        info_filter = """//*[name()=$tag]"""
        value = reply.data.xpath(info_filter, tag=tag)[0].text

        print(100 * '=')
        print(tag, "for", interface_name, "interface:", value)
        print(100 * '=')


def set_tx_and_rx_filter(ncc, types, ranges):
    print(100 * '*')
    LOG.info('Getting optical receiver and/or transmitter power...')
    print(100 * '*')

    rpc = ''' <get-pm-data xmlns="http://www.advaoptical.com/aos/netconf/aos-core-pm"
                            xmlns:me="http://www.advaoptical.com/aos/netconf/aos-core-managed-element"
                            xmlns:fac="http://www.advaoptical.com/aos/netconf/aos-core-facility">
                <target-entity>/me:managed-element[me:entity-name="1"]/fac:interface[fac:name="1/2/n2"]/fac:physical-interface/fac:lr-phys-optical</target-entity>
                    <pm-data>
                        <pm-current-data/>
                    </pm-data>
                </get-pm-data> '''

    result = ncc.dispatch(to_ele(rpc), source='running').xml.encode()
    root = etree.fromstring(result)

    prefix = 'acor-factt:'

    if type(types) != type([]):
        power_types = [types]
    else:
        power_types = types

    if type(ranges) != type([]):
        power_ranges = [ranges]
    else:
        power_ranges = ranges

    for pt in power_types:
        for pr in power_ranges:
            info = prefix + pt + pr
            mt_filter = '''//*[name()='mon-type']'''
            tags = root.xpath(mt_filter)

            for tag in tags:
                time_interval = tag.getparent().getparent().getchildren()[0]
                if tag.text == info and time_interval.text != 'acor-pmt:interval-24hour':
                    print(100 * '*')
                    print("Info for", time_interval.text + ":", tag.text)
                    print("Value:", tag.getnext().text)
                    print(100 * '*')


def set_ber_filter(ncc, ranges):
    rpc = ''' <get-pm-data xmlns="http://www.advaoptical.com/aos/netconf/aos-core-pm"
                        xmlns:me="http://www.advaoptical.com/aos/netconf/aos-core-managed-element"
                        xmlns:fac="http://www.advaoptical.com/aos/netconf/aos-core-facility"
                    xmlns:eth="http://www.advaoptical.com/aos/netconf/aos-core-ethernet">
                <target-entity>/me:managed-element[me:entity-name="1"]/fac:interface[fac:name="1/2/c1/et100"]/fac:logical-interface/eth:ety6</target-entity>
                <pm-data>
                  <pm-current-data/>
                </pm-data>
              </get-pm-data> '''

    print(100 * '*')
    LOG.info('Getting bit error rate...')
    print(100 * '*')

    result = ncc.dispatch(to_ele(rpc), source='running')
    result = result.xml.encode()
    root = etree.fromstring(result)

    prefix = 'acor-factt:'
    ber = 'fec-ber'

    if type(ranges) != type([]):
        ber_ranges = []
        ber_ranges.append(ranges)
    else:
        ber_ranges = ranges

    for r in ber_ranges:
        info = prefix + ber + r
        mt_filter = '''//*[name()='mon-type']'''
        tags = root.xpath(mt_filter)

        for tag in tags:
            time_interval = tag.getparent().getparent().getchildren()[0]
            if tag.text == info and time_interval.text != 'acor-pmt:interval-24hour':
                print(100 * '*')
                print("Info for", time_interval.text + ":", tag.text)
                print("Value:", tag.getnext().text)
                print(100 * '*')


def set_optical_channel_filter(ncc, channel_qualities, quality_ranges):
    rpc = ''' <get-pm-data xmlns="http://www.advaoptical.com/aos/netconf/aos-core-pm"
                        xmlns:me="http://www.advaoptical.com/aos/netconf/aos-core-managed-element"
                        xmlns:eq="http://www.advaoptical.com/aos/netconf/aos-core-equipment"
                        xmlns:fac="http://www.advaoptical.com/aos/netconf/aos-core-facility"
                        xmlns:otn="http://www.advaoptical.com/aos/netconf/aos-domain-otn">
                    <target-entity>/me:managed-element[me:entity-name="1"]/fac:interface[fac:name="1/2/n1/ot100"]/fac:logical-interface/otn:optical-channel</target-entity>
                        <pm-data>
                            <pm-current-data/>
                        </pm-data>
            </get-pm-data> '''

    print(100 * '*')
    LOG.info('Getting SNR, q-factor and/or group delay...')
    print(100 * '*')

    result = ncc.dispatch(to_ele(rpc), source='running').xml.encode()
    root = etree.fromstring(result)

    prefix = 'adom-oduckpat:'

    if type(channel_qualities) != type([]):
        channel_qualities_list = [channel_qualities]
    else:
        channel_qualities_list = channel_qualities

    if type(quality_ranges) != type([]):
        quality_ranges_list = [quality_ranges]
    else:
        quality_ranges_list = quality_ranges

    for cq in channel_qualities_list:
        for qr in quality_ranges_list:

            info = prefix + cq + qr

            mt_filter = '''//*[name()='mon-type']'''
            tags = root.xpath(mt_filter)

            for tag in tags:
                time_interval = tag.getparent().getparent().getchildren()[0]
                if tag.text == info and time_interval.text != 'acor-pmt:interval-24hour':
                    print(100 * '*')
                    print("Info for", time_interval.text + ":", tag.text)
                    print("Value:", tag.getnext().text)
                    print(100 * '*')


###################################################################################################
#                                        MAIN FUNCTIONS                                           #
###################################################################################################
@course_function(shortcut='0')
def get_frequency_and_power():
    """Get frequency and power."""
    print(100*'*')
    LOG.info("Starting...")
    print(100*'*')

    host = choose_host()

    interface_name = questionary.select(
        "Please choose an interface:",
        choices=[
            '1/2/n1',
            '1/2/n2',
            '1/2/c1',
            '1/2/c3'
        ]).ask()

    print(100 * '*')
    LOG.info("Connecting to " + host + "...")
    print(100 * '*')

    with ncconnect(host=host, port="830",  username=USERNAME, password=PASSWORD, hostkey_verify=False) as ncc:
        LOG.info("Retrieving data...")

        tag = questionary.select(
            "Please select an info:",
            choices=[
                'tuned-frequency',
                'opt-setpoint'
            ]).ask()

        set_frequency_and_power_filter(host, ncc, interface_name, tag)


@course_function(shortcut='1')
def get_tx_and_rx():
    print(100*'*')
    LOG.info("Starting...")
    print(100*'*')

    host = choose_host()

    print(100 * '*')
    LOG.info("Connecting to " + host + "...")
    print(100 * '*')

    with ncconnect(host=host, port="830",  username=USERNAME, password=PASSWORD, hostkey_verify=False) as ncc:
        # TODO: in <target-entity>, se lascio '1/2/c1/et100' funziona solo per .19
        #  Se provo a mettere '1/2/c3/et100', non va ne per .19 ne per .23
        #  Guardare slide

        power_type = questionary.select(
            "Please select info:",
            choices=[
                'opt-rcv-pwr',
                'opt-trmt-pwr',
            ]).ask()
        power_range = questionary.select(
            "Please select power:",
            choices=[
                '',
                '-lo',
                '-mean',
                '-hi'
            ]).ask()

        set_tx_and_rx_filter(ncc, power_type, power_range)


@course_function(shortcut='2')
def get_ber():
    print(100*'*')
    LOG.info("Starting...")
    print(100*'*')

    host = choose_host()

    print(100*'*')
    LOG.info("Connecting to " + host + "...")
    print(100*'*')

    with ncconnect(host=host, port="830",  username=USERNAME, password=PASSWORD, hostkey_verify=False) as ncc:
        # TODO: in <target-entity>, se lascio '1/2/c1/et100' funziona solo per .19
        #  Se provo a mettere '1/2/c3/et100', non va ne per .19 ne per .23
        #  Guardare slide

        ber_range = questionary.select(
            "Please select power:",
            choices=[
                '',
                '-mean'
            ]).ask()

        set_ber_filter(ncc, ber_range)


@course_function(shortcut="3")
def get_and_filter_optical_channels():
    """Get and filter optical channels."""
    print(100 * '*')
    LOG.info("Starting...")
    print(100 * '*')

    host = questionary.select(
        "Please choose a host:",
        choices=[
            '10.11.12.19',
            '10.11.12.23'
        ]).ask()  # returns value of selection

    print(100 * '*')
    LOG.info("Connecting to " + host + "...")
    print(100 * '*')

    with ncconnect(host=host, port="830",  username="admin", password="CHGME.1a", hostkey_verify=False) as ncc:
        # TODO: in <target-entity>, se lascio '1/2/n1/ot100' funziona solo per .19
        #  Se provo a mettere '1/2/n2/ot100', non va ne per .19 ne per .23
        #  Guardare slide

        LOG.info("Getting and filtering optical channels...")

        channel_quality = questionary.select(
            "Please select info:",
            choices=[
                'signal-to-noise-ratio',
                'q-factor',
                'differential-group-delay'
            ]).ask()
        quality_range = questionary.select(
            "Please select power:",
            choices=[
                '',
                '-lo',
                '-mean',
                '-hi'
            ]).ask()

        set_optical_channel_filter(ncc, channel_quality, quality_range)



@course_function(shortcut="4")
def periodic_requests():
    """Periodically iterates all the previous requests"""
    print(100 * '*')
    LOG.info("Starting...")
    print(100 * '*')

    ################################################################################################
    #                DATA INPUT PHASE                                                              #
    ################################################################################################
    host = input('Insert the address of the host you want to connect to: ')

    default = questionary.select(
        'Do you want to use the default port, username and password?',
        choices=[
            'yes',
            'no'
        ]).ask()  # returns value of selection

    if default == 'no':
        port = input('Insert the port: ')
        username = input('Insert the username: ')
        password = getpass('Insert the password: ')
    else:
        port = "830"
        username = USERNAME
        password = PASSWORD

    interface_name = questionary.select(
        "Please choose an interface:",
        choices=[
            '1/2/n1',
            '1/2/n2',
            '1/2/c1',
            '1/2/c3'
        ]).ask()

    std_out = questionary.select(
        "Where would you like to see the output?",
        choices=[
            'console',
            'file'
        ]).ask()

    control_period = input("Insert time between two consecutive requests: ")

    # TODO: Cambiando lo standard out su file vengono portate su file solo le print e non le LOG.info. Trovare una
    #   soluzione oppure cambiare le LOG.info in print
    if std_out == "file":
        file = input("Insert the file path: ")
        sys.stdout = open(file, "w")

    ################################################################################################
    #                CONNECTION SETUP AND REQUESTS                                                 #
    ################################################################################################
    while(1):
        print(100 * '*')
        LOG.info("Connecting to " + host + "...")
        print(100 * '*')

        with ncconnect(host=host, port=port,  username=username, password=password, hostkey_verify=False) as ncc:
            LOG.info("Retrieving data...")
            LOG.info("Getting tuned-frequency and opt-setpoint...")

            tags = ["tuned-frequency", "opt-setpoint"]
            set_frequency_and_power_filter(host, ncc, interface_name, tags)

            power_types = ['opt-rcv-pwr', 'opt-trmt-pwr']
            power_ranges = ['', '-lo', '-mean', '-hi']
            set_tx_and_rx_filter(ncc, power_types, power_ranges)

            ber_ranges = ['', '-mean']
            set_ber_filter(ncc, ber_ranges)

            channel_qualities = ['signal-to-noise-ratio', 'q-factor', 'differential-group-delay']
            quality_ranges = ['', '-lo', '-mean', '-hi']
            set_optical_channel_filter(ncc, channel_qualities, quality_ranges)

        time.sleep(float(control_period))

