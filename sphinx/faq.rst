=============================
Frequently Asked Questions
=============================

.. highlight:: sh

-------------------------------------------------------------------------------------------------------------------------------------
PLACE gives me an error, saying I don't have permission to access the serial port. How do I fix this? Do I need to run as ``sudo``?
-------------------------------------------------------------------------------------------------------------------------------------

    While running as ``sudo`` may fix the issue, this is not a correct fix.
    Linux systems typically assign ownership of the serial ports to the
    ``dialout`` group. If you add yourself to this group, you will be able to
    access the serial ports without needing ``sudo``. On most Linux systems,
    this can be accomplished by an administrative user by running:
    
    ::
    
        sudo usermod -a -G dialout <username>
