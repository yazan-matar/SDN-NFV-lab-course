PoliCONF
========

The ADVA/PoliMi SDN+NETCONF/RESTCONF+Python programming course
--------------------------------------------------------------

[![Gitter](
    https://badges.gitter.im/sdn-nfv-lab-course-2019-2020/policonf.svg)](
    https://gitter.im/sdn-nfv-lab-course-2019-2020/policonf?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)

### Before you start coding

### Start coding

You will do all your course programming in the files
`policonf/netconf-functions.py` and `policonf/restconf-functions.py`

Those course programming files contain Python function definitions like:

```python
@course_function(shortcut="t")
def set_transponder_mode():
    """Set transponder mode."""
    LOG.info("Setting transponder mode...")

    # If you want to implement this PoliMi SDN course function, then just
    # remove the following lines and start coding...
    raise NotImplementedError(
        "This ADVA/PoliMi SDN course function needs your implementation :)")
```

Every SDN student group is assigned to one or more of those course functions.
Just ignore the course functions you are not assigned to.

For implementing the course functions, the `policonf/netconf-functions.py`
and `policonf/restconf-functions.py` modules contain the following global
helpers for programming convenience:

* `LOG`: The Python logger instance for the `policonf` package, providing
  the following logging methods:

  - `.debug()`
  - `.info()`
  - `.warning()`
  - `.error()`
  - `.critical()`

`policonf/netconf-functions.py` contains additional helpers:

* `NETCONF`: An intentionally not-yet-working custom NETCONF client wrapper :)

  - If you want to generalize your ``ncclient`` connection management, to keep
    repetitive (re-)connection details out of your course functions, then you
    can put such features into the `policonf.netconf.NETCONF` class to make
    this wrapper actually work. Just be creative... If you like ;)

### Run your functions

You can test and run your course functions either from your IDE or by using
the `policonf` command line tool.

The latter starts a customized interactive IPython shell, which explains all
further details at startup:

```
$ policonf
Python 3.8.1 (default, Jan  8 2020, 15:55:49) [MSC v.1916 64 bit (AMD64)]
Type 'copyright', 'credits' or 'license' for more information
IPython 7.13.0 -- An enhanced Interactive Python. Type '?' for help.
INFO:policonf:Loading PoliCONF/IPython magic...
INFO:policonf:(Re-)Loading ADVA/PoliMi SDN course functions...

Available ADVA/PoliMi NETCONF SDN course functions:

[t] Set transponder mode.
[f] Set frequency and power.
[l] Create logical channel on client side.
[c] Connect client to network.
[o] Get and filter optical channels.
[p] Get and filter port indexes.
[e] Tear down existing lightpath.

Available ADVA/PoliMi RESTCONF SDN course functions:

[t] Get full TAPI context.
[s] Get service interface points from TAPI.
[u] Get topology UUIDs from TAPI.
[n] Get node UUIDs from TAPI.
[l] Get link UUIDs from TAPI.
[c] Get connection UUIDs from TAPI.

Run a course function by using the %polirun command,
followed by either netconf(nc) or restconf(rc)
and the function's [shortcut].

For example, to run the RESTCONF "Get connection UUIDs from TAPI." function:

%polirun rc c

For convenience, you can use %ncrun and %rcrun instead of %polirun nc
and %polirun rc, respectively:

%rcrun c

In [1]: _
```

As you can see above, the most important is the `%polirun` command:

```
In [1]: %polirun netconf t
INFO:policonf:(Re-)Loading ADVA/PoliMi SDN course functions...
INFO:policonf:Setting transponder mode...
```

Each execution of the `%polirun` command reloads all Python code from
`policonf/netconf-functions.py` and `policonf/restconf-functions.py`

So there is no need to restart the `policonf` shell
after you make any code changes in your course function(s).
