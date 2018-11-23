=============================
Frequently Asked Questions
=============================

.. highlight:: sh

------------------------------------------------------------------------------------------------------------------------------------
PLACE gives me an error, saying I don't have permission to access the serial port. How do I fix this? Do I need to run as ``sudo``?
------------------------------------------------------------------------------------------------------------------------------------

    While running as ``sudo`` may fix the issue, this is not a correct fix.
    Linux systems typically assign ownership of the serial ports to the
    ``dialout`` group. If you add yourself to this group, you will be able to
    access the serial ports without needing ``sudo``. On most Linux systems,
    this can be accomplished by an administrative user by running:
    
    ::
    
        sudo usermod -a -G dialout <username>

----------------------------------------------------------------------------------------------------------------------
Something on the web interface is not reflecting my recent code change. What did I do wrong?
----------------------------------------------------------------------------------------------------------------------

    Most web browsers will cache files so they don't need to redownload them.
    Try forcing a reload of the PLACE webpage (ctrl+click the refresh button in
    Google Chrome) and see if this fixes the issue.

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
The PLACE server is giving me an error, and telling me to add a value (IP address/port/serial path/etc.) to my ``.place.cfg`` file. I don't know this value. What should I do?
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    The values in the ``.place.cfg`` file are typically unique to your specific
    lab, which is why they are not hard-coded into the PLACE or plugin code.

    You can typically find these values by looking in the manufacturer's manual
    for the instrument you are using.

    Oftentimes, someone else will have already used the instrument you wish to
    use and will have the values you need in their ``.place.cfg`` file (each
    user has their own configuration file). Ask them to send you their settings
    and put them into your configuration file.

----------------------------------------------
How do I build the PLACE documentation?
----------------------------------------------

    The documentation is all designed to be built using Sphinx. The ``.rst``
    files used to generate the Sphinx documentation are found in the
    ``place/sphinx`` directory. From this directory, you can build the
    documentation by running:

    ::

        sphinx-build -b html . ../placeweb/static/placeweb/documentation

    If you do not have ``sphinx-build`` you need to `install Sphinx
    <https://www.sphinx-doc.org/en/master/index.html>`_

------------------------------------------------------------------------------------------------------
When I run ``sphinx-build``, it says "No module name 'sphinx_py3doc_enhanced_theme'". What do I do?
------------------------------------------------------------------------------------------------------

    The current theme used for the PLACE docs is not installed with Sphinx, but
    it is available on ``pip``. Just run:

    ::

        pip install sphinx_py3doc_enhanced_theme
        
-----------------------------------------------------------------------------------------------
When I start ``place_server`` it tells me the port is already in use. What should I do?
-----------------------------------------------------------------------------------------------

    This is most often occurs when another user already has a PLACE server running
    on that port. First, you should ensure there isn't an experiment running on
    the machine. But, if it seems like the server was left on by mistake, you have
    a few options.
    
    1. You can change the Django port number in your ``~/.place.cfg`` file. Then try
       starting the server again.
    2. You can logout the other user, by restarting the computer or via some fancy
       `Linux method <https://www.cyberciti.biz/faq/linux-logout-user-howto/>`_.
    3. You can use their server. This isn't ideal, because you won't be able to see
       any server errors, but if you just have to do a quick experiment, this
       should work fine.

-----------------------------------------------------------------------------------------------
I am trying to monitor my experiment from another device, but the PLACE webpage is not found.
-----------------------------------------------------------------------------------------------

    Some operating systems will block access to PLACE server from external devices.
    On CentOS, you need to unblock ``http`` and ``https`` TCP access for the port your
    PLACE server is using. `More info here 
    <https://stackoverflow.com/questions/24729024/open-firewall-port-on-centos-7>`_.
    
    Additionally, check your ``~/.place.cfg`` and ensure your Django IP address
    (Django is the service that runs the PLACE server) is not set to the internal
    IP address 127.0.0.1.
