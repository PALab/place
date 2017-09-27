"""Store and recall file commands"""
from .sr850_driver import SR850Driver

class SR850StoreRecallFile(SR850Driver):
    """Store and recall file commands"""
    def fnam(self, filename=None):
        """Sets or queries the active file name.

        :param filename: the name of the file
        :type filename: str
        :returns: the name of the file
        :rtype: str
        """
        if filename is not None:
            self._set('FNAM {}'.format(filename))
        return self._query('FNAM?')

    def sdat(self):
        """Saves the active display data trace.

        This is the same as pressing the Data Save softkey.
        """
        self._set('SDAT')

    def sasc(self):
        """Saves the active disaply's data trace in ascii format.

        This is the same as pressing the Ascii Save softkey.
        """
        self._set('SASC')

    def sset(self):
        """Saves the instrument setup.

        This is the same as pressing the Settings Save softkey.
        """
        self._set('SSET')

    def rdat(self):
        """Recalls the trace data, trace definition, and instrument state.

        This is the same as pressing the Data Recall softkey.
        """
        self._set('RDAT')

    def rset(self):
        """Recalls the instrument setup.

        This is the same as pressing the Setting Recall softkey.
        """
        self._set('RSET')
