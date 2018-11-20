PLACE Glossary
==============

.. glossary::
    :sorted:

    binary format
        Binary files are not stored using characters from any readable language
        and are instead written in mathematical values stored as bytes. To read
        the data in a binary file, you generally need use a program which
        understands the binary format of the file. PLACE saves files in the NumPy
        binary format, meaning it can be read using the numpy library in Python.

    command
        Elm uses commands to complete actions safely. Things like writing data to
        disk or sending information over a port can fail, so Elm handles these
        things for us. This doesn't mean these things cannot fail, it just means
        that Elm will simplify the process of checking for failure by doing most
        of the checking for us. `Read more <http://package.elm-lang.org/packages/elm-lang/core/latest/Platform-Cmd>`_

    config phase
        At the beginning of an experiment, each plugin is provided a opportunity
        to perform configuration steps, as specified in the plugin's
        ``config()`` method. Metadata can also be saved during this phase.

    experiment
        Within the PLACE context, an *experiment* refers to any execution of the
        PLACE software. In older versions of PLACE, this may also be referred to
        as a *scan*.

    PLACE
        Python Laboratory Automation, Control, and Experimentation.

    message
        Elm uses messages to communicate changes made by the user, along with some
        other internal changes.  So, for example, when the user picks a new option
        in a dropdown menu, a message is generated in the code to update the model
        to reflect the user's change.

    metadata
        Data about data. This is used by PLACE to describe the values contained in
        the NumPy data file produced by PLACE. It will contain the original configuration
        options used to start the experiment along with other information.

    module
        Previously, this term was used to describe the code used to drive one
        instrument in the modular PLACE ecosystem. However, since both Elm and
        Python refer to code as a module, this term became ambiguous. Referring to
        all the code for one instrument as a "plugin" is now preferred, with each
        plugin typically being composed of at least one Elm module for the user
        interface and one Python module for the server-side execution. See
        :term:`plugin`.

    plugin
        Refers to an independent group of files which instruct PLACE how to
        interact with specific hardware. Typically, this includes both a Python
        backend module and an Elm frontend module with the user. PLACE supports
        dynamic interaction with properly written plugins.

    priority
        All PLACE modules are given a priority value which determines their order
        of execution during an experiment.  Instruments with lower values are
        executed earlier in the rotation than those with higher values. Arguments
        can be made that this is backwards, but that would still be true if the
        order was reversed. Instruments with the same priority are not executed in
        parallel (yet), and PLACE with just select one to go first.

    scan
        Legacy term. See :term:`experiment`.

    update
        Updates occur during the :term:`update phase` of PLACE. It is
        essentially the looping phase of an experiment. Instrument plugins
        written for PLACE must include and update method in their class
        definition. Code in this method should expect to be called one or more
        times during an experiment. The instrument is made aware of both the
        current update number and the total number of updates for an experiment,
        and can thus roughly position itself temporally during an experiment.

    update phase
        This phase is the second phase of a PLACE experiment and is essentially
        the *looping* phase. This phase will run one or more times depending on
        the number of updates selected by the user.