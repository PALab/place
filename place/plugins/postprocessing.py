"""Post-processing base class for PLACE"""
class PostProcessing:
    """Generic interface for post-processing data generated in PLACE.

    This class is a base class for performing calculations during a PLACE
    experiment before data is written to disk. This allows a great deal of
    customization in the data stored by PLACE. For example, many records can be
    collected with an oscilloscope device and post-processed down to a single
    record before they are saved - greatly reducing file size. Additionally,
    this base class could be used to remove unneeded fields, rename fields, or
    perform other basic tasks which cater the data to suit a variety of needs.
    """
    def __init__(self, config):
        """Constructor

        Stores the JSON config data submitted for the experiment into a class
        dictionary and sets a default post-processing priority. Subclasses can
        certainly repeat this or override it, but it is done here anyway.

        Subclass priority is used by PLACE to determine the order of execution.
        Lower values of priorty are updated before higher ones. If this seems
        backwards to you, use the phrase "this is my number one priority" to
        help you remember.

        Post-processing priority defaults to 1000 to avoid clashes with the
        default Instrument priority (100). However, this is not enforced and
        sub classes may use any priority they like.

        :param config: configuration data (from JSON)
        :type config: dict
        """
        self._config = config
        self.priority = 1000

    def config(self, metadata):
        """Configure the post-processing.

        Called once at the beginning of a scan. Post-processing modules should
        use this function sparingly, mostly to record metadata.

        :param metadata: PLACE maintains metadata for each experiment in a
                         dictionary object. During the configuration phase,
                         this dictionary is passed to each module so that
                         relevant data can be recorded into it. As with
                         Instruments, PostProcessing modules should record
                         information that is relevant to the entire scan, but
                         is also specific to the module. PLACE will write all
                         the metadata collected into a single file for each
                         experiment.
        :type metadata: dict

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    def update(self, data):
        """Update the data by performing post-processing on one or more fields.

        Called one or more times during an experiment. During this method, the
        post-processing module will receive a numpy array containing all the
        data recorded by PLACE so far during this update only. It can be
        thought of as one row of the total data collected by PLACE during the
        experiment.

        The data will be stored in a NumPy structured array, meaning that it
        will have labelled headings. Most post-processing will generally target
        one field in this one row of data. This can be thought of as a *cell*
        in a spreadsheet. During each update cycle, PLACE is collecting cell
        data to populate one row. So, generally, this function will be looking
        for a specific cell in the row of data sent as input. This cell will be
        removed, processed, and re-inserted into the data - then returned to
        PLACE. For example, if you want to post-process trace data collected by
        the Alazartech ATS9440 during this update, you will use the named
        heading (probably 'ATS9440-trace') and row 0.

        Here is an example of how a typical update occurs when post-processing
        data::

            import numpy as np
            from numpy.lib import recfunctions as rfn

            # our target field name
            field = 'ATS9440-trace'
            # each update only has 1 row, so this is always 0
            row = 0

            # copy the desired cell out of the data
            data_to_process = data[field][row].copy()

            # delete the cell from the data, but save the other data (optional)
            other_data = rfn.drop_fields(data, field, usemask=False)

            # perform post-processing - should return a NumPy array with shape (1,)
            processed_data = post_processing(data_to_process)

            # insert and return the new data
            return rfn.merge_arrays([other_data, processed_data], flatten=True, usemask=False)

        .. note::

            It is important that the data returned by this function be the same
            size every time it gets called. For example, if an array of 256
            64-bit floats is returned during the first update, then 256 64-bit
            floats must be returned during each subsequent update.

        :param data: row data collected so far from other instruments
        :type data: numpy.array, structured array of shape (1,)

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError
