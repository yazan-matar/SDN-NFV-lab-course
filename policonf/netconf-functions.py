"""The ADVA/PoliMi NETCONF SDN course functions."""

from logging import Logger, getLogger

import ncclient.manager

from policonf import netconf
from policonf.magic import course_function


#: The logger instance for mod:`policonf`.
LOG: Logger = getLogger(__package__)

#: An intentionally not-yet-working custom NETCONF client wrapper.
#
#  If you want to generalize your ``ncclient`` connection management, to keep
#  repetitive (re-)connection details out of your course functions, then you
#  can put such features into :class:`policonf.netconf.NETCONF` to make this
#  wrapper actually work. Just be creative... If you like ;)
NETCONF: netconf.NETCONF = netconf.NETCONF()


@course_function(shortcut="t")
def set_transponder_mode():
    """Set transponder mode."""
    LOG.info("Setting transponder mode...")

    # If you want to implement this PoliMi SDN course function, then just
    # remove the following lines and start coding...
    raise NotImplementedError(
        "This ADVA/PoliMi SDN course function needs your implementation :)")


@course_function(shortcut="f")
def set_frequency_and_power():
    """Set frequency and power."""
    LOG.info("Setting frequency and power...")

    # If you want to implement this PoliMi SDN course function, then just
    # remove the following lines and start coding...
    raise NotImplementedError(
        "This ADVA/PoliMi SDN course function needs your implementation :)")


@course_function(shortcut="l")
def create_logical_channel_on_client_side():
    """Create logical channel on client side."""
    LOG.info("Creating logical channel on client side...")

    # If you want to implement this PoliMi SDN course function, then just
    # remove the following lines and start coding...
    raise NotImplementedError(
        "This ADVA/PoliMi SDN course function needs your implementation :)")


@course_function(shortcut="c")
def connect_client_to_network():
    """Connect client to network."""
    LOG.info("Connecting client to network...")

    # If you want to implement this PoliMi SDN course function, then just
    # remove the following lines and start coding...
    raise NotImplementedError(
        "This ADVA/PoliMi SDN course function needs your implementation :)")


@course_function(shortcut="o")
def get_and_filter_optical_channels():
    """Get and filter optical channels."""
    LOG.info("Getting and filtering optical channels...")

    # If you want to implement this PoliMi SDN course function, then just
    # remove the following lines and start coding...
    raise NotImplementedError(
        "This ADVA/PoliMi SDN course function needs your implementation :)")


@course_function(shortcut="p")
def get_and_filter_port_indexes():
    """Get and filter port indexes."""
    LOG.info("Getting and filtering port indexes...")

    # If you want to implement this PoliMi SDN course function, then just
    # remove the following lines and start coding...
    raise NotImplementedError(
        "This ADVA/PoliMi SDN course function needs your implementation :)")


@course_function(shortcut="e")
def tear_down_existing_lightpath():
    """Tear down existing lightpath."""
    LOG.info("Tearing down existing lightpath...")

    # If you want to implement this PoliMi SDN course function, then just
    # remove the following lines and start coding...
    raise NotImplementedError(
        "This ADVA/PoliMi SDN course function needs your implementation :)")
