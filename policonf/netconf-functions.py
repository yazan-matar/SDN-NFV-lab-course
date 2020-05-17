"""The ADVA/PoliMi SDN course functions."""


from logging import getLogger

import policonf.netconf
from policonf.magic import course_function
from ncclient.manager import connect as ncconnect


# Other libraries
# import re
# import xml.etree.ElementTree as ET
from lxml.etree import tounicode
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
    print("======================================================================")
    print(type(host))
    print("======================================================================")
    return host



@course_function(shortcut='0')
def get_frequency_and_power():
    """Get frequency and power."""
    print('************************************************************************')
    LOG.info("Starting...")
    print('************************************************************************')

    host = choose_host()

    if host == '10.11.12.19':
        interface_name = '1/2/n2'
    else:
        interface_name = '1/2/n1'

    interface_filter = '''
        <managed-element>
    	    <interface>
                <name>''' + interface_name + '''</name>
    	        <physical-interface/>
    	    </interface>
        </managed-element>
    '''
    print('************************************************************************')
    LOG.info("Connecting to " + host + "...")
    print('************************************************************************')

    with ncconnect(host=host, port="830",  username=USERNAME, password=PASSWORD, hostkey_verify=False) as ncc:
        LOG.info("Retrieving data...")
        reply = ncc.get(filter=('subtree', interface_filter))

        # print("===============================REPLY=============================")
        # print(tounicode(reply.data, pretty_print=True))
        # print("======================================================================")
        # for c in ncc.server_capabilities:
        #     print(c)


        info = questionary.select(
            "Please select an info:",
            choices=[
                'tuned-frequency',
                'opt-setpoint'
            ]).ask()

        info_filter = """//*[name()=$info]"""
        print("======================================================================")
        print(info, "for", interface_name, "interface:", reply.data.xpath(info_filter, info=info)[0].text)
        print("======================================================================")


@course_function(shortcut='1')
def get_pm_data():
    print('************************************************************************')
    LOG.info("Starting...")
    print('************************************************************************')

    host = choose_host()

    print('************************************************************************')
    LOG.info("Connecting to", host + "...")
    print('************************************************************************')

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
                    <pm-current-data>
                        <bin-interval>acor-pmt:interval-indefinite</bin-interval>
                    </pm-current-data>
                </pm-data>
            </get-pm-data>
        '''
        print('************************************************************************')
        LOG.info('Sending RPC...')
        print('************************************************************************')

        result = ncc.dispatch(to_ele(rpc), source='running')
        print("======================================================================")
        print(result)
        print("======================================================================")

        #TODO: capire come convertire l'oggetto in qualcosa di parsabile
        # result.data restituisce None

        # print(type(result.data))
        # print(type(str(result)))
        # print(str(result))
        # print(type(result.data_xml))

        # mon_type = questionary.select(
        #     "Please select mon-type:",
        #     choices=[
        #         'acor-factt:opt-rcv-pwr',
        #         'acor-factt:opt-trmt-pwr',
        #         'acor-factt:fec-ber'
        #     ]).ask()
        #
        # power = questionary.select(
        #     "Please select power:",
        #     choices=[
        #         'lo',
        #         'mean',
        #         'hi'
        #     ]).ask()
        # mon_type = mon_type + '-' + power
        # mt_filter = '''//*[name()='mon-type']'''
        # tags = result.data.xpath(mt_filter)
        # for tag in tags:
        #     if tag.text == mon_type:
        #         print("mon-type:", tag.text)



@course_function(shortcut="2")
def get_and_filter_optical_channels():
    """Get and filter optical channels."""
    print('************************************************************************')
    LOG.info("Starting...")
    print('************************************************************************')

    host = questionary.select(
        "Please choose a host:",
        choices=[
            '10.11.12.19',
            '10.11.12.23'
        ]).ask()  # returns value of selection

    # if host == '10.11.12.19':
    #     interface_name = '1/2/n2'
    # else:
    #     interface_name = '1/2/n1'

    print('************************************************************************')
    LOG.info("Connecting to", host + "...")
    print('************************************************************************')

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

        print('************************************************************************')
        LOG.info('Sending an RPC...')
        print('************************************************************************')

        result = ncc.dispatch(to_ele(rpc), source='running')
        print("======================================================================")
        print(result)
        print("======================================================================")

        # TODO: stesso problema della funzione get_pm_data()


