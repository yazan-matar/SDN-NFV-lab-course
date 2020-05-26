"""The ADVA/PoliMi SDN course functions."""

# import logging
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
# LOG = logging.getLogger(__package__)
# LOG.info("\n\n\n\n\n\n\ntesting logger\n\n\n\n\n\n\n\n\n")
# sys.stdout = sys.__stdout__

LOG = getLogger(__package__)

#: The NETCONF client instance.
NETCONF = policonf.netconf.NETCONF()

USERNAME = 'admin'
PASSWORD = 'CHGME.1a'


# TODO: in the iPython environment: %load_ext policonf --> %polirun 0 (or any other shortcut)
# TODO: wrap sensible codes in try/except blocks

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

# TODO: togliere host
def set_frequency_and_power_filter(host, ncc, interface_name, tags):
    global LOG
    LOG.info("Getting frequency and/or power...")

    interface_filter = '''
        <managed-element>
            <interface>
                <name>''' + interface_name + '''</name>
                <physical-interface/>
            </interface>
        </managed-element>
    '''

    reply = ncc.get(filter=('subtree', interface_filter))

    for tag in tags:
        info_filter = """//*[name()=$tag]"""
        values = reply.data.xpath(info_filter, tag=tag)
        if len(values) != 0:
            for value in values:
                print(100 * '*')
                print(tag, "for", interface_name, "interface:", value.text)
                print(100 * '=')
        else:
            LOG.info("No matching tag for <" + tag + ">")


def set_tx_and_rx_filter(ncc, interface_names, power_types, power_ranges):
    LOG.info('Getting optical receiver and/or transmitter power...')

    ### Nel caso non periodico cicla una sola volta

    for interface_name in interface_names:
        ### Nelle interfacce c1 e c3 il tag 'lr-phys-optical' si chiama 'lr-physm-optical'
        condition = interface_name != '1/2/c1' and interface_name != '1/2/c3'
        m = "" if condition else "m"

        rpc = ''' 
        <get-pm-data xmlns="http://www.advaoptical.com/aos/netconf/aos-core-pm"
                                   xmlns:me="http://www.advaoptical.com/aos/netconf/aos-core-managed-element"
                                   xmlns:fac="http://www.advaoptical.com/aos/netconf/aos-core-facility"
                               xmlns:eth="http://www.advaoptical.com/aos/netconf/aos-core-ethernet">
           <target-entity>/me:managed-element[me:entity-name="1"]/fac:interface[fac:name="''' + interface_name + '''"]/fac:physical-interface/fac:lr-phys''' + m + '''-optical</target-entity>
           <pm-data>
             <pm-current-data/>
           </pm-data>
         </get-pm-data> '''

        result = ncc.dispatch(to_ele(rpc), source='running').xml.encode()
        root = etree.fromstring(result)
        prefix = 'acor-factt:'
        tags = list()

        for pt in power_types:
            for pr in power_ranges:
                info = prefix + pt + pr
                mt_filter = '''//*[name()='mon-type']'''
                tags = tags + root.xpath(mt_filter)  # unisco le varie liste risultanti in un'unica lista

        for tag in tags:
            time_interval = tag.getparent().getparent().getchildren()[0]
            if tag.text == info and time_interval.text != 'acor-pmt:interval-24hour':
                print(100 * '*')
                print("Info for", time_interval.text + ":", tag.text)
                print("Value:", tag.getnext().text)
                print(100 * '*')


def set_ber_filter(ncc, interface_names, ber_ranges):

    for interface_name in interface_names:
        cond1 = interface_name == '1/2/n2/ot100'
        cond2 = interface_name == '1/2/c3/et100'
        # cond3 = interface_name == '1/2/n2/ot100/odu4' or interface_name == '1/2/c3/et100/odu4'

        if cond1:
            target = '/optical-channel'
        elif cond2:
            target = '/eth:ety6'
        else:
            target = '/odu4'

        rpc = ''' 
        <get-pm-data xmlns="http://www.advaoptical.com/aos/netconf/aos-core-pm"
            xmlns:me="http://www.advaoptical.com/aos/netconf/aos-core-managed-element"
            xmlns:fac="http://www.advaoptical.com/aos/netconf/aos-core-facility"
	        xmlns:eth="http://www.advaoptical.com/aos/netconf/aos-core-ethernet">
	        xmlns:otn="http://www.advaoptical.com/aos/netconf/aos-domain-otn">
                <target-entity>/me:managed-element[me:entity-name="1"]/fac:interface[fac:name="''' + interface_name + '''"]/fac:logical-interface''' + target +'''</target-entity>
                <pm-data>
                    <pm-current-data/>
                </pm-data>
        </get-pm-data>
        '''

        LOG.info('Getting bit error rate...')

        result = ncc.dispatch(to_ele(rpc), source='running')
        print(result)
        result = result.xml.encode()

        root = etree.fromstring(result)

        prefix = 'acor-factt:'
        ber = 'fec-ber'
        tags = list()
        # TODO: Gestire caso in cui non trova ber (casi odu4), quindi mi restituisce una lista vuota

        for r in ber_ranges:
            info = prefix + ber + r
            mt_filter = '''//*[name()='mon-type']'''

            tags = tags + root.xpath(mt_filter)

        for tag in tags:
            time_interval = tag.getparent().getparent().getchildren()[0]
            if tag.text == info and time_interval.text != 'acor-pmt:interval-24hour':
                print(100 * '*')
                print("Info for", time_interval.text + ":", tag.text)
                print("Value:", tag.getnext().text)
                print(100 * '*')


def set_optical_channel_filter(ncc, interface_names, channel_qualities, quality_ranges):
    for interface_name in interface_names:
        rpc = ''' <get-pm-data xmlns="http://www.advaoptical.com/aos/netconf/aos-core-pm"
                            xmlns:me="http://www.advaoptical.com/aos/netconf/aos-core-managed-element"
                            xmlns:eq="http://www.advaoptical.com/aos/netconf/aos-core-equipment"
                            xmlns:fac="http://www.advaoptical.com/aos/netconf/aos-core-facility"
                            xmlns:otn="http://www.advaoptical.com/aos/netconf/aos-domain-otn">
                        <target-entity>/me:managed-element[me:entity-name="1"]/fac:interface[fac:name="''' + interface_name + '''"]/fac:logical-interface/optical-channel</target-entity>
                            <pm-data>
                                <pm-current-data/>
                            </pm-data>
                </get-pm-data> '''

        LOG.info('Getting SNR, q-factor and/or group delay...')

        result = ncc.dispatch(to_ele(rpc), source='running').xml.encode()
        root = etree.fromstring(result)

        prefix = 'adom-oduckpat:'
        tags = list()

        for cq in channel_qualities:
            for qr in quality_ranges:
                info = prefix + cq + qr
                mt_filter = '''//*[name()='mon-type']'''
                tags = tags + root.xpath(mt_filter)

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
    """Get tuned frequency and optical set-point."""

    LOG.info("Starting...")

    host = choose_host()

    interface_name = questionary.select(
        "Please choose an interface:",
        choices=[
            '1/2/n1',
            '1/2/n2'
        ]).ask()

    LOG.info("Connecting to " + host + "...")

    with ncconnect(host=host, port="830", username=USERNAME, password=PASSWORD, hostkey_verify=False) as ncc:
        LOG.info("Retrieving data...")

        tags = list()
        tag = questionary.select(
            "Please select an info:",
            choices=[
                'tuned-frequency',
                'opt-setpoint'
            ]).ask()
        tags.append(tag)

        set_frequency_and_power_filter(host, ncc, interface_name, tags)


@course_function(shortcut='1')
def get_tx_and_rx():
    """Get optical received and transmitted power."""
    LOG.info("Starting...")

    host = choose_host()

    LOG.info("Connecting to " + host + "...")

    with ncconnect(host=host, port="830", username=USERNAME, password=PASSWORD, hostkey_verify=False) as ncc:

        power_types = list()
        power_ranges = list()
        interface_names = list()

        interface_name = questionary.select(
            "Please choose an interface:",
            choices=[
                '1/2/n1',
                '1/2/n2',
                '1/2/c1',
                '1/2/c3'
            ]).ask()

        power_type = questionary.select(
            "Please select type:",
            choices=[
                'opt-rcv-pwr',
                'opt-trmt-pwr',
            ]).ask()
        power_range = questionary.select(
            "Please select range:",
            choices=[
                '',
                '-lo',
                '-mean',
                '-hi'
            ]).ask()

        power_types.append(power_type)
        power_ranges.append(power_range)
        interface_names.append(interface_name)

        set_tx_and_rx_filter(ncc, interface_names, power_types, power_ranges)


@course_function(shortcut='2')
def get_ber():
    """Get bit error rate."""
    LOG.info("Starting...")
    host = choose_host()

    LOG.info("Connecting to " + host + "...")

    with ncconnect(host=host, port="830", username=USERNAME, password=PASSWORD, hostkey_verify=False) as ncc:
        # TODO: Da quel che ho capito, il parametro BER si trova solo nelle interfacce logiche, che tra l'altro
        #  si trovano solo nell'host .23, e solo per n2 e c3
        #  Altra cosa, il BER si trova soltanto in 1/2/c3/et100
        #  Chiedere chiarimenti prima del 30 maggio

        ber_ranges = list()
        interface_names = list()

        interface_name = questionary.select(
            "Please choose an interface:",
            choices=[
                # '1/2/n2/ot100',
                # '1/2/n2/ot100/odu4',
                '1/2/c3/et100'
                # '1/2/c3/et100/odu4'
            ]).ask()

        ber_range = questionary.select(
            "Please select range:",
            choices=[
                '',
                '-mean'
            ]).ask()

        ber_ranges.append(ber_range)
        interface_names.append(interface_name)

        set_ber_filter(ncc, interface_names, ber_ranges)


@course_function(shortcut="3")
def get_and_filter_optical_channels():
    """Get and SNR, q-factor and differential group delay."""
    LOG.info("Starting...")

    host = choose_host()

    LOG.info("Connecting to " + host + "...")

    with ncconnect(host=host, port="830", username="admin", password="CHGME.1a", hostkey_verify=False) as ncc:

        LOG.info("Getting and filtering optical channels...")

        channel_qualities = list()
        quality_ranges = list()
        interface_names = list()

        interface_name = questionary.select(
            "Please choose an interface:",
            choices=[
                # '1/2/n1/ot100',
                '1/2/n2/ot100',
            ]).ask()

        channel_quality = questionary.select(
            "Please select parameter:",
            choices=[
                'signal-to-noise-ratio',
                'q-factor',
                'differential-group-delay'
            ]).ask()
        quality_range = questionary.select(
            "Please select range:",
            choices=[
                '',
                '-lo',
                '-mean',
                '-hi'
            ]).ask()

        channel_qualities.append(channel_quality)
        quality_ranges.append(quality_range)
        interface_names.append(interface_name)

        set_optical_channel_filter(ncc, interface_names,channel_qualities, quality_ranges)

@course_function(shortcut='4')
def get_interfaces():
    filter = '''
        <managed-element xmlns="http://www.advaoptical.com/aos/netconf/aos-core-managed-element">
            <interface xmlns="http://www.advaoptical.com/aos/netconf/aos-core-facility">
                <name/>
                <physical-interface/>
                <logical-interface/>
            </interface>
        </managed-element>
    '''

    host = choose_host()

    LOG.info("Connecting to " + host + "...")

    with ncconnect(host=host, port="830", username="admin", password="CHGME.1a", hostkey_verify=False) as ncc:

        result = ncc.get_config(source='running', filter=('subtree', filter))
        print(result)

#TODO: Sistemare le funzioni periodiche


@course_function(shortcut="5")
def periodic_requests():
    """Periodically iterates all the previous requests"""
    # global LOG
    # LOG = logging.getLogger(__package__)
    LOG.info("Starting...")

    ################################################################################################
    #                DATA INPUT PHASE                                                              #
    ################################################################################################

    host = choose_host()

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

    control_period = input("Insert time between two consecutive requests: ")

    std_out = questionary.select(
        "Where would you like to see the output?",
        choices=[
            'console',
            'file'
        ]).ask()

    if std_out == "file":
        # file = input("Insert the file path or press enter to use the default log.txt file: ")
        try:
            sys.stdout = open("log.txt", "w")
            # LOG = logging.getLogger("fileLogger")
        except:
            LOG.info("Incorrect file path: writing in log.txt")
            print("Incorrect file path: creating a log.txt file in the current folder")
            sys.stdout = open("log.txt", "w")
            # LOG = logging.getLogger("fileLogger")

    else:
        sys.stdout = sys.__stdout__
        # LOG = logging.getLogger(__package__)

    ################################################################################################
    #                CONNECTION SETUP AND REQUESTS                                                 #
    ################################################################################################
    while (True):
        LOG.info("Connecting to " + host + "...")

        with ncconnect(host=host, port=port, username=username, password=password, hostkey_verify=False) as ncc:
            LOG.info("Retrieving data...")
            LOG.info("Getting tuned-frequency and opt-setpoint...")

            tags = ["tuned-frequency", "opt-setpoint"]
            set_frequency_and_power_filter(host, ncc, interface_name, tags)

            LOG.info("Getting transmitted and received power...")
            power_types = ['opt-rcv-pwr', 'opt-trmt-pwr']
            power_ranges = ['', '-lo', '-mean', '-hi']
            set_tx_and_rx_filter(ncc, power_types, power_ranges)

            LOG.info("Getting signal BER...")
            ber_ranges = ['', '-mean']
            set_ber_filter(ncc, ber_ranges)

            LOG.info("Getting optical channel quality values...")
            channel_qualities = ['signal-to-noise-ratio', 'q-factor', 'differential-group-delay']
            quality_ranges = ['', '-lo', '-mean', '-hi']
            set_optical_channel_filter(ncc, channel_qualities, quality_ranges)

        time.sleep(float(control_period))


@course_function(shortcut="6")
def periodic_variable_requests():
    """
        Periodically iterates all the previous requests, with the possibility
        to change host, interface, or stopping the requests at each iteration
    """
    LOG.info("Starting...")

    ################################################################################################
    #                DATA INPUT PHASE                                                              #
    ################################################################################################

    host = questionary.select(
        "Insert the address of the host you want to connect to:",
        choices=[
            '10.11.12.19',
            '10.11.12.23'
        ]).ask()

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

    # TODO: Ora il logger scrive direttamente su file (vedi __main__.py) e le print su console
    #   quindi non serve più dare la scelta all'utente. Lascio comunque il codice nel caso si vogliano
    #   fare entrambe le cose

    # std_out = questionary.select(
    #     "Where would you like to see the output?",
    #     choices=[
    #         'console',
    #         'file'
    #     ]).ask()

    # if std_out == "file":
    #     file = input("Insert the file path: ")
    #     try:
    #         sys.stdout = open(file, "w")
    #     except:
    #         LOG.info("Incorrect file path: writing in log.txt")
    #         print("Incorrect file path: creating a log.txt file in the current folder")
    #         sys.stdout = open("log.txt", "w")

    ################################################################################################
    #                CONNECTION SETUP AND REQUESTS                                                 #
    ################################################################################################

    isRequesting = True

    while (isRequesting):
        LOG.info("Connecting to " + host + "...")

        with ncconnect(host=host, port=port, username=username, password=password, hostkey_verify=False) as ncc:
            LOG.info("Retrieving data...")
            LOG.info("Getting tuned-frequency and opt-setpoint...")

            tags = ["tuned-frequency", "opt-setpoint"]
            set_frequency_and_power_filter(host, ncc, interface_name, tags)

            LOG.info("Getting transmitted and received power...")
            power_types = ['opt-rcv-pwr', 'opt-trmt-pwr']
            power_ranges = ['', '-lo', '-mean', '-hi']
            set_tx_and_rx_filter(ncc, power_types, power_ranges)

            LOG.info("Getting signal BER...")
            ber_ranges = ['', '-mean']
            set_ber_filter(ncc, ber_ranges)

            LOG.info("Getting optical channel quality values...")
            channel_qualities = ['signal-to-noise-ratio', 'q-factor', 'differential-group-delay']
            quality_ranges = ['', '-lo', '-mean', '-hi']
            set_optical_channel_filter(ncc, channel_qualities, quality_ranges)

            answer = questionary.select(
                'Do you want to continue?',
                choices=[
                    'Yes',
                    'No',
                    'Change host',
                    'Change interface'
                ]).ask()

        if answer == 'Change host':
            host = questionary.select(
                "Insert the address of the host you want to connect to:",
                choices=[
                    '10.11.12.19',
                    '10.11.12.23'
                ]).ask()
        if answer == 'Change interface':
            interface_name = questionary.select(
                "Please choose an interface:",
                choices=[
                    '1/2/n1',
                    '1/2/n2',
                    '1/2/c1',
                    '1/2/c3'
                ]).ask()

        if answer == 'No':
            isRequesting = False

    # sys.stdout.close()
