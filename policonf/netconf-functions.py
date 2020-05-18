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

#: The logger instance for mod:`policonf`.
LOG = getLogger(__package__)

#: The NETCONF client instance.
NETCONF = policonf.netconf.NETCONF()

USERNAME = 'admin'
PASSWORD = 'CHGME.1a'


#TODO: in the iPython environment: %load_ext policonf --> %polirun 0 (or any other shortcut)


###################################################################################################
#                                          My functions                                           #
###################################################################################################
def choose_host():
    host = questionary.select(
        "Please choose a host:",
        choices=[
            '10.11.12.19',
            '10.11.12.23'
        ]).ask()
    return host



@course_function(shortcut='0')
def get_frequency_and_power():
    """Get frequency and power."""
    print(100*'*')
    LOG.info("Starting...")
    print(100*'*')

    host = choose_host()

    interface_name = questionary.select(
        "Please choose a host:",
        choices=[
            '1/2/n1',
            '1/2/n2',
            '1/2/c1',
            '1/2/c3'
        ]).ask()

    interface_filter = '''
        <managed-element>
    	    <interface>
                <name>''' + interface_name + '''</name>
    	        <physical-interface/>
    	    </interface>
        </managed-element>
    '''
    print(100*'*')
    LOG.info("Connecting to " + host + "...")
    print(100*'*')

    with ncconnect(host=host, port="830",  username=USERNAME, password=PASSWORD, hostkey_verify=False) as ncc:
        LOG.info("Retrieving data...")
        reply = ncc.get(filter=('subtree', interface_filter))

        tag = questionary.select(
            "Please select an info:",
            choices=[
                'tuned-frequency',
                'opt-setpoint'
            ]).ask()

        info_filter = """//*[name()=$tag]"""
        value = reply.data.xpath(info_filter, tag=tag)[0].text

        print(100 * '=')
        print(tag, "for", interface_name, "interface:", value)
        print(100 * '=')


@course_function(shortcut='1')
def get_tx_and_rx():
    print(100*'*')
    LOG.info("Starting...")
    print(100*'*')

    host = choose_host()

    print(100*'*')
    LOG.info("Connecting to", host + "...")
    print(100*'*')

    with ncconnect(host=host, port="830",  username=USERNAME, password=PASSWORD, hostkey_verify=False) as ncc:
    # TODO: in <target-entity>, se lascio '1/2/c1/et100' funziona solo per .19
    #  Se provo a mettere '1/2/c3/et100', non va ne per .19 ne per .23
    #  Guardare slide

        rpc = '''
          <get-pm-data xmlns="http://www.advaoptical.com/aos/netconf/aos-core-pm"
                    xmlns:me="http://www.advaoptical.com/aos/netconf/aos-core-managed-element"
                    xmlns:fac="http://www.advaoptical.com/aos/netconf/aos-core-facility">
            <target-entity>/me:managed-element[me:entity-name="1"]/fac:interface[fac:name="1/2/n2"]/fac:physical-interface/fac:lr-phys-optical</target-entity>
            <pm-data>
              <pm-current-data/>
            </pm-data>
          </get-pm-data>
        '''
        print(100 * '*')
        LOG.info('Sending RPC...')
        print(100 * '*')

        result = ncc.dispatch(to_ele(rpc), source='running')
        result = result.xml.encode()
        root = etree.fromstring(result)

        prefix = 'acor-factt:'

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

        info = prefix + power_type + power_range
        mt_filter = '''//*[name()='mon-type']'''
        tags = root.xpath(mt_filter)

        for tag in tags:
            time_interval = tag.getparent().getparent().getchildren()[0]
            if tag.text == info and time_interval.text != 'acor-pmt:interval-24hour':
                print(100 * '*')
                print("Info for", time_interval.text + ":", tag.text)
                print("Value:", tag.getnext().text)
                print(100 * '*')

@course_function(shortcut='2')
def get_ber():

    print(100*'*')
    LOG.info("Starting...")
    print(100*'*')

    host = choose_host()

    print(100*'*')
    LOG.info("Connecting to", host + "...")
    print(100*'*')

    with ncconnect(host=host, port="830",  username=USERNAME, password=PASSWORD, hostkey_verify=False) as ncc:
    # TODO: in <target-entity>, se lascio '1/2/c1/et100' funziona solo per .19
    #  Se provo a mettere '1/2/c3/et100', non va ne per .19 ne per .23
    #  Guardare slide

        rpc = '''
          <get-pm-data xmlns="http://www.advaoptical.com/aos/netconf/aos-core-pm"
                    xmlns:me="http://www.advaoptical.com/aos/netconf/aos-core-managed-element"
                    xmlns:fac="http://www.advaoptical.com/aos/netconf/aos-core-facility"
                xmlns:eth="http://www.advaoptical.com/aos/netconf/aos-core-ethernet">
            <target-entity>/me:managed-element[me:entity-name="1"]/fac:interface[fac:name="1/2/c1/et100"]/fac:logical-interface/eth:ety6</target-entity>
            <pm-data>
              <pm-current-data/>
            </pm-data>
          </get-pm-data>
        '''
        print(100 * '*')
        LOG.info('Sending RPC...')
        print(100 * '*')

        result = ncc.dispatch(to_ele(rpc), source='running')
        result = result.xml.encode()
        root = etree.fromstring(result)

        prefix = 'acor-factt:'
        ber = 'fec-ber'
        ber_range = questionary.select(
            "Please select power:",
            choices=[
                '',
                '-mean'
            ]).ask()

        info = prefix + ber + ber_range
        mt_filter = '''//*[name()='mon-type']'''
        tags = root.xpath(mt_filter)

        for tag in tags:
            time_interval = tag.getparent().getparent().getchildren()[0]
            if tag.text == info and time_interval.text != 'acor-pmt:interval-24hour':
                print(100 * '*')
                print("Info for", time_interval.text + ":", tag.text)
                print("Value:", tag.getnext().text)
                print(100 * '*')




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
    LOG.info("Connecting to", host + "...")
    print(100 * '*')

    with ncconnect(host=host, port="830",  username="admin", password="CHGME.1a", hostkey_verify=False) as ncc:
        # TODO: in <target-entity>, se lascio '1/2/n1/ot100' funziona solo per .19
        #  Se provo a mettere '1/2/n2/ot100', non va ne per .19 ne per .23
        #  Guardare slide

        LOG.info("Getting and filtering optical channels...")

        rpc = '''
            <get-pm-data xmlns="http://www.advaoptical.com/aos/netconf/aos-core-pm"
                         xmlns:me="http://www.advaoptical.com/aos/netconf/aos-core-managed-element"
                         xmlns:eq="http://www.advaoptical.com/aos/netconf/aos-core-equipment"
                         xmlns:fac="http://www.advaoptical.com/aos/netconf/aos-core-facility"
                         xmlns:otn="http://www.advaoptical.com/aos/netconf/aos-domain-otn">
              <target-entity>/me:managed-element[me:entity-name="1"]/fac:interface[fac:name="1/2/n1/ot100"]/fac:logical-interface/otn:optical-channel</target-entity>
              <pm-data>
                <pm-current-data/>
              </pm-data>
            </get-pm-data>
        '''

        print(100 * '*')
        LOG.info('Sending an RPC...')
        print(100 * '*')

        result = ncc.dispatch(to_ele(rpc), source='running')
        result = result.xml.encode()
        root = etree.fromstring(result)

        prefix ='adom-oduckpat:'
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
        info = prefix + channel_quality + quality_range

        mt_filter = '''//*[name()='mon-type']'''
        tags = root.xpath(mt_filter)

        for tag in tags:
            time_interval = tag.getparent().getparent().getchildren()[0]
            if tag.text == info and time_interval.text != 'acor-pmt:interval-24hour':
                print(100 * '*')
                print("Info for", time_interval.text + ":", tag.text)
                print("Value:", tag.getnext().text)
                print(100 * '*')
