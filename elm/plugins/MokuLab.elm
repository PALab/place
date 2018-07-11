-- STEP 1:
-- set the module name to be the same as the file name,
-- but without the .elm extenstion


port module MokuLab exposing (main)

import Html exposing (Html)
import Html.Attributes
import Json.Encode
import ModuleHelpers


attributions : ModuleHelpers.Attributions
attributions =
    { authors = [ "Rabea Pleiss", "Paul Freeman" ]
    , maintainer = "Rabea Pleiss"
    , maintainerEmail = "rple516@aucklanduni.ac.nz"
    }



-- STEP 2:
-- change placeModuleName to be the name that shows as the title
-- of your GUI box within the PLACE interface


placeModuleName : String
placeModuleName =
    "MokuLab"



-- STEP 3:
-- change pythonModuleName to be the name of your Python module


pythonModuleName : String
pythonModuleName =
    "moku_lab"



-- STEP 4:
-- change pythonClassName to be the name of your Python class


pythonClassName : String
pythonClassName =
    "MokuLab"



-- STEP 5:
-- set defaultPriority to be the default PLACE priority


defaultPriority : String
defaultPriority =
    "10"



-- STEP 6:
-- Add variables needed from the user into this data structure.  Generally, you
-- will use Bool or String. Often you will need Int and Float values. These are
-- usually best kept as stings within the Elm code and converted to number
-- formats when the JSON is written.


type alias Model =
    { className : String
    , active : Bool
    , priority : String
    , plot : String
    , pause : Bool
    , singleSweep : Bool
    , freqStart : String
    , freqEnd : String
    , dataPoints : String
    , channel : String
    , ch1Amp : String
    , ch2Amp : String
    , averagingTime : String
    , settlingTime : String
    , averagingCycles : String
    , settlingCycles : String
    , progress : Maybe Json.Encode.Value
    }



-- STEP 7:
-- For each variable you added, assign it a default value in the defaultModel.


defaultModel : Model
defaultModel =
    { className = "None"
    , active = False
    , priority = defaultPriority
    , plot = "no"
    , pause = False
    , singleSweep = True
    , freqStart = "30"
    , freqEnd = "130"
    , dataPoints = "512"
    , channel = "ch1"
    , ch1Amp = "2.0"
    , ch2Amp = "2.0"
    , averagingTime = "0.01"
    , settlingTime = "0.01"
    , averagingCycles = "1"
    , settlingCycles = "1"
    , progress = Nothing
    }



-- STEP 8:
-- Add a message to change each variable you added. If you aren't sure what to
-- name them, general PLACE convention is to prefix Toggle to variable name if
-- it is a boolean or prefix Change if it is one of the other types.
--
-- Note that all UI elements to manipulate Int, Float, and String variables
-- will return a String from the user, so even if you have a Float variable
-- named "mass", your message from the UI will be something like ChangeMass
-- String, because the UI will send a String based on the keyboard input from
-- the user.


type Msg
    = ToggleActive
    | SendJson
    | Close
    | ChangePriority String
    | ChangePlot String
    | TogglePause
    | ToggleSingleSweep
    | ChangeFreqStart String
    | ChangeFreqEnd String
    | ChangeDataPoints String
    | ChangeChannel String
    | ChangeCh1Amp String
    | ChangeCh2Amp String
    | ChangeAveragingTime String
    | ChangeSettlingTime String
    | ChangeAveragingCycles String
    | ChangeSettlingCycles String
    | UpdateProgress Json.Encode.Value



-- STEP 9:
-- In this step, we will write what happens when the UI sends us a message.
-- This message is sent whenever the user changes something on the UI. So, each
-- time the user types a digit into an integer box, we want to make sure we
-- update the value in our model. This means that generally, we will handle
-- messages by simply updating the appropriate variable, depending on the
-- message received. Examples have been provided to get you started.


updateModel : Msg -> Model -> ( Model, Cmd Msg )
updateModel msg model =
    (case msg of
        ToggleActive ->
            toggleActive model

        SendJson ->
            sendJson model

        Close ->
            close

        ChangePlot newPlot ->
            updateModel SendJson { model | plot = newPlot }

        TogglePause ->
            updateModel SendJson { model | pause = not model.pause }

        ToggleSingleSweep ->
            updateModel SendJson { model | singleSweep = not model.singleSweep }

        ChangeFreqStart newFreqStart ->
            updateModel SendJson { model | freqStart = newFreqStart }

        ChangeFreqEnd newFreqEnd ->
            updateModel SendJson { model | freqEnd = newFreqEnd }

        ChangeDataPoints newDataPoints ->
            updateModel SendJson { model | dataPoints = newDataPoints }

        ChangeChannel newChannel ->
            updateModel SendJson { model | channel = newChannel }

        ChangeCh1Amp newCh1Amp ->
            updateModel SendJson { model | ch1Amp = newCh1Amp }

        ChangeCh2Amp newCh2Amp ->
            updateModel SendJson { model | ch2Amp = newCh2Amp }

        ChangeAveragingTime newAveragingTime ->
            updateModel SendJson { model | averagingTime = newAveragingTime }

        ChangeSettlingTime newSettlingTime ->
            updateModel SendJson { model | settlingTime = newSettlingTime }

        ChangeAveragingCycles newAveragingCycles ->
            updateModel SendJson { model | averagingCycles = newAveragingCycles }

        ChangeSettlingCycles newSettlingCycles ->
            updateModel SendJson { model | settlingCycles = newSettlingCycles }

        -- -- EXAMPLE BOOL UPDATE
        -- TogglePlot ->
        --     updateModel SendJson { model | plot = not model.plot }
        --
        -- -- EXAMPLE STRING, INT, FLOAT UPDATE
        -- ChangeNote newNote ->
        --     updateModel SendJson { model | note = newNote }
        --
        -- ChangeSamples newSamples ->
        --     updateModel SendJson { model | samples = newSamples }
        --
        -- ChangeStart newStart ->
        --     updateModel SendJson { model | start = newStart }
        --
        ChangePriority newPriority ->
            changePriority newPriority model

        UpdateProgress progress ->
            ( { model | progress = Just progress }, Cmd.none )
    )



-- STEP 10:
-- Add interactive elements for each variable you added into the model.
--
-- You can add checkboxes to manipulate boolean values, integer input fields,
-- float input fields, and string input fields.  Additionally, there is a
-- dropdown menu element, to allow selection from a limited number of strings.
-- Put all these elements between the square brackets and separated by commas.
--
-- For most of these functions, you pass the text description of the element,
-- the variable to hold the result, and the message to manipulate the variable.
-- So if, for example, I needed the user to manipulate a float value to
-- describe the velocity, my interactive element might be described with this
-- code:
--
--     ModuleHelpers.floatField "Velocity" model.velocity ChangeVelocity
--
-- You can find these functions in the ModuleHelpers.elm file, or you can look
-- at other modules for examples.


userInteractionsView : Model -> List (Html Msg)
userInteractionsView model =
    let
        a1 =
            ModuleHelpers.floatDefault defaultModel.averagingTime model.averagingTime

        a2 =
            ModuleHelpers.floatDefault defaultModel.averagingCycles model.averagingCycles

        s1 =
            ModuleHelpers.floatDefault defaultModel.settlingTime model.settlingTime

        s2 =
            ModuleHelpers.floatDefault defaultModel.settlingCycles model.settlingCycles

        n =
            ModuleHelpers.intDefault defaultModel.dataPoints model.dataPoints

        ch1_amp =
            ModuleHelpers.floatDefault defaultModel.ch1Amp model.ch1Amp

        ch2_amp =
            ModuleHelpers.floatDefault defaultModel.ch2Amp model.ch2Amp

        setup =
            (if n < 512 then
                1
             else
                1 * (n // 512)
            )

        pst =
            setup
                + round
                    (estimatedTime
                        model.averagingTime
                        model.averagingCycles
                        model.settlingTime
                        model.settlingCycles
                        model.dataPoints
                    )

        days =
            pst // (3600 * 24)

        nondays =
            pst % (3600 * 24)

        hours =
            nondays // 3600

        nonhours =
            nondays % 3600

        mins =
            nonhours // 60

        seconds =
            nonhours % 60

        timeString =
            (if days > 1 then
                (toString days) ++ " days "
             else if days == 1 then
                (toString days) ++ " day "
             else
                ""
            )
                ++ (if hours > 1 then
                        (toString hours) ++ " hours "
                    else if hours == 1 then
                        (toString hours) ++ " hour "
                    else
                        ""
                   )
                ++ (if mins > 1 then
                        (toString mins) ++ " minutes "
                    else if mins == 1 then
                        (toString mins) ++ " minute "
                    else
                        ""
                   )
                ++ (if seconds > 1 then
                        (toString seconds) ++ " seconds "
                    else if seconds == 1 then
                        (toString seconds) ++ " second or less. "
                    else if pst < 1 then
                        "less than a second."
                    else
                        ""
                   )
    in
        [ ModuleHelpers.integerField "Priority" model.priority ChangePriority

        --, ModuleHelpers.dropDownBox "Plotting" model.plot ChangePlot [ ( "no", "No plotting" ), ( "live", "Yes, plot live" ), ( "update", "Yes, but only after each update" ) ]
        ]
            {-
               ++ (if model.plot /= "no" then
                       [ ModuleHelpers.checkbox "I want to pause after each update" model.pause TogglePause
                       ]
                   else
                       []
                  )
            -}
            ++ [ --ModuleHelpers.checkbox "Just one sweep? " model.singleSweep ToggleSingleSweep,
                 ModuleHelpers.dropDownBox "Channels" model.channel ChangeChannel [ ( "ch1", "Channel 1" ), ( "ch2", "Channel 2" ), ( "both", "Both channels" ) ]
               , ModuleHelpers.floatField "Start frequency (kHz)" model.freqStart ChangeFreqStart
               , ModuleHelpers.floatField "End frequency (kHz)" model.freqEnd ChangeFreqEnd
               , ModuleHelpers.integerField "Data points" model.dataPoints ChangeDataPoints
               ]
            ++ (if n < 32 then
                    [ Html.p []
                        [ Html.span [ Html.Attributes.class "error-text" ]
                            [ Html.text ("Lower bound breached. Please increase to a minimum of 32 points.") ]
                        ]
                    ]
                else
                    []
               )
            ++ (if n % 2 == 0 then
                    []
                else
                    [ Html.p []
                        [ Html.span [ Html.Attributes.class "error-text" ]
                            [ Html.text ("Currently MokuLab only supports even numbers of data points.") ]
                        ]
                    ]
               )
            ++ [ ModuleHelpers.floatField "Ch1 amplitude (V)" model.ch1Amp ChangeCh1Amp
               ]
            ++ (if ch1_amp > 2.0 then
                    [ Html.p []
                        [ Html.span [ Html.Attributes.class "error-text" ]
                            [ Html.text ("Upper bound breached. Please decrease to a maximum of 2.0 Volts.") ]
                        ]
                    ]
                else
                    []
               )
            ++ [ ModuleHelpers.floatField "Ch2 amplitude (V)" model.ch2Amp ChangeCh2Amp
               ]
            ++ (if ch2_amp > 2.0 then
                    [ Html.p []
                        [ Html.span [ Html.Attributes.class "error-text" ]
                            [ Html.text ("Upper bound breached. Please decrease to a maximum of 2.0 Volts.") ]
                        ]
                    ]
                else
                    []
               )
            ++ [ ModuleHelpers.floatField "Averaging time (s)" model.averagingTime ChangeAveragingTime
               ]
            ++ (if a1 < 1.0e-6 then
                    [ Html.p []
                        [ Html.span [ Html.Attributes.class "error-text" ]
                            [ Html.text ("Lower bound breached. Please increase to a minimum of 1e-06 seconds.") ]
                        ]
                    ]
                else if a1 > 10 then
                    [ Html.p []
                        [ Html.span [ Html.Attributes.class "error-text" ]
                            [ Html.text ("Upper bound breached. Please decrease to a maximum of 10 seconds.") ]
                        ]
                    ]
                else
                    []
               )
            ++ [ ModuleHelpers.floatField "Settling time (s)" model.settlingTime ChangeSettlingTime
               ]
            ++ (if s1 < 1.0e-6 then
                    [ Html.p []
                        [ Html.span [ Html.Attributes.class "error-text" ]
                            [ Html.text ("Lower bound breached. Please increase to a minimum of 1e-06 seconds.") ]
                        ]
                    ]
                else if s1 > 10 then
                    [ Html.p []
                        [ Html.span [ Html.Attributes.class "error-text" ]
                            [ Html.text ("Upper bound breached. Please decrease to a maximum of 10 seconds.") ]
                        ]
                    ]
                else
                    []
               )
            ++ [ ModuleHelpers.integerField "Averaging cycles (no.)" model.averagingCycles ChangeAveragingCycles
               ]
            ++ (if a2 < 1 then
                    [ Html.p []
                        [ Html.span [ Html.Attributes.class "error-text" ]
                            [ Html.text ("Lower bound breached. Please increase to a minimum of 1 cycle.") ]
                        ]
                    ]
                else if a2 > 1048576 then
                    [ Html.p []
                        [ Html.span [ Html.Attributes.class "error-text" ]
                            [ Html.text ("Upper bound breached. Please decrease to a maximum of 1048576 cycle.") ]
                        ]
                    ]
                else
                    []
               )
            ++ [ ModuleHelpers.integerField "Settling cycles (no.)" model.settlingCycles ChangeSettlingCycles
               ]
            ++ (if s2 < 1 then
                    [ Html.p []
                        [ Html.span [ Html.Attributes.class "error-text" ]
                            [ Html.text ("Lower bound breached. Please increase to a minimum of 1 cycle.") ]
                        ]
                    ]
                else if s2 > 1048576 then
                    [ Html.p []
                        [ Html.span [ Html.Attributes.class "error-text" ]
                            [ Html.text ("Upper bound breached. Please decrease to a maximum of 1048576 cycle.") ]
                        ]
                    ]
                else
                    []
               )
            ++ (if pst > 3600 * 24 then
                    [ Html.p []
                        [ Html.span [ Html.Attributes.class "warning-text" ]
                            [ Html.br [] []
                            , Html.text ("Estimated time per update is " ++ timeString)
                            ]
                        ]
                    ]
                else
                    [ Html.p [] [ Html.text ("Estimated time per update is " ++ timeString ++ ". Note this is a rough estimate, lower frequencies take longer.") ]
                    ]
               )
            ++ [ ModuleHelpers.displayAllProgress model.progress ]



-- -- SAMPLE CHECKBOX
-- , ModuleHelpers.checkbox "Plot" model.plot ChangePlot
--
-- -- SAMPLE INTEGER FIELD
-- , ModuleHelpers.integerField "Number of samples" model.samples ChangeSamples
--
-- -- SAMPLE FLOAT FIELD
-- , ModuleHelpers.floatField "Angle" model.angle ChangeAngle
--
-- -- SAMPLE STRING FIELD
-- , ModuleHelpers.stringField "Comment" model.comment ChangeComment
--
-- -- SAMPLER DROPDOWN BOX
-- , ModuleHelpers.dropDownBox "Shape" model.shape ChangeShape [("circle", "Circle"), ("zigzag", "Zig Zag")]
--
-- Note that in the dropdown box, you must also pass the choices. The
-- first string in each tuple is the value saved into the variable and the
-- second is the more descriptive string shown to the user on the web
-- interface.
-- STEP 11:
-- Each time a user interaction is made, PLACE updates the JSON text that will
-- be sent to the PLACE backend when the experiment is started. In this step,
-- we will update the JSON. As with other steps, there is a different way to
-- handle each type of variable, so examples are provided.
--
-- As mentioned previously, it is during this step that our Int and Float
-- values will be converted from the String values used in the web interface.
-- In the event that the user tries to start an experiment with illegal values
-- in the number fields, the default value is used.
--
-- This step is important because this is where you will actually define how
-- your Python module will access the values selected by the user in the web
-- interface. So, for example, if you have a variable named "linearDistance" in
-- the Elm Model and you associate it with the String "linear_distance" in this
-- step, then in your Python code, you would be able to access the linear
-- distance selected by the user by accessing self._config['linear_distance'].


jsonValues : Model -> List ( String, Json.Encode.Value )
jsonValues model =
    [ ( "plot", Json.Encode.string model.plot )
    , ( "pause", Json.Encode.bool model.pause )
    , ( "single_sweep", Json.Encode.bool model.singleSweep )
    , ( "channel", Json.Encode.string model.channel )
    , ( "f_start"
      , Json.Encode.float
            (ModuleHelpers.floatDefault
                defaultModel.freqStart
                model.freqStart
            )
      )
    , ( "f_end"
      , Json.Encode.float
            (ModuleHelpers.floatDefault
                defaultModel.freqEnd
                model.freqEnd
            )
      )
    , ( "data_points"
      , Json.Encode.int
            (ModuleHelpers.intDefault
                defaultModel.dataPoints
                model.dataPoints
            )
      )
    , ( "ch1_amp"
      , Json.Encode.float
            (ModuleHelpers.floatDefault
                defaultModel.ch1Amp
                model.ch1Amp
            )
      )
    , ( "ch2_amp"
      , Json.Encode.float
            (ModuleHelpers.floatDefault
                defaultModel.ch2Amp
                model.ch2Amp
            )
      )
    , ( "averaging_time"
      , Json.Encode.float
            (ModuleHelpers.floatDefault
                defaultModel.averagingTime
                model.averagingTime
            )
      )
    , ( "settling_time"
      , Json.Encode.float
            (ModuleHelpers.floatDefault
                defaultModel.settlingTime
                model.settlingTime
            )
      )
    , ( "averaging_cycles"
      , Json.Encode.int
            (ModuleHelpers.intDefault
                defaultModel.averagingCycles
                model.averagingCycles
            )
      )
    , ( "settling_cycles"
      , Json.Encode.int
            (ModuleHelpers.intDefault
                defaultModel.settlingCycles
                model.settlingCycles
            )
      )

    --
    -- -- STRING
    -- ( "sample_description", Json.Encode.string model.sampleDescription )
    --
    -- -- INT
    -- ( "averages"
    -- , Json.Encode.int
    --       (Result.withDefault defaultModel.averages
    --           (String.toInt model.averages)
    --       )
    -- )
    --
    -- -- FLOAT
    -- ( "temperature"
    -- , Json.Encode.float
    --       (Result.withDefault defaultModel.temp
    --           (String.toFloat model.temp)
    --       )
    -- )
    --
    -- -- BOOL
    -- ( "extraProcessing", Json.Encode.bool model.extraProcessing )
    --
    -- Note: separate each tuple with a comma
    ]



-- STEP 12 (optional):
-- If your PLACE module records data, it is expected to register it in the
-- PLACE user interface. This allows users to get an accurate representation of
-- the data layout using the "Show Data Layout" button in the webapp. This is
-- simply a list of strings describing the data. Elm will prefix each sting
-- with the python class name and a dash, so a string "time" might become
-- "PLACETemplate-time".


dataRegister : Model -> List String
dataRegister model =
    -- example: ["time", "position", "temperature"]
    case model.channel of
        "ch1" ->
            [ "magnitude_dB_ch1", "phase_ch1" ]

        "ch2" ->
            [ "magnitude_dB_ch2", "phase_ch2" ]

        "both" ->
            [ "magnitude_dB_ch1", "phase_ch1", "magnitude_dB_ch2", "phase_ch2" ]

        otherwise ->
            []


estimatedTime : String -> String -> String -> String -> String -> Float
estimatedTime s_a1 s_a2 s_s1 s_s2 s_n =
    let
        a1 =
            ModuleHelpers.floatDefault defaultModel.averagingTime s_a1

        a2 =
            ModuleHelpers.floatDefault defaultModel.averagingCycles s_a2

        s1 =
            ModuleHelpers.floatDefault defaultModel.settlingTime s_s1

        s2 =
            ModuleHelpers.floatDefault defaultModel.settlingCycles s_s2

        n =
            ModuleHelpers.intDefault defaultModel.dataPoints s_n

        f =
            toFloat n
    in
        (max (a1 * f) (a2 * f / 37500)) + (max (s1 * f) (s2 * f / 37500))



----------------------------------------------
-- THINGS YOU PROBABLY DON"T NEED TO CHANGE --
----------------------------------------------


port config : Json.Encode.Value -> Cmd msg


port processProgress : (Json.Encode.Value -> msg) -> Sub msg


port removeModule : String -> Cmd msg


main : Program Never Model Msg
main =
    Html.program
        { init = ( defaultModel, Cmd.none )
        , view = \model -> Html.div [] (viewModel model)
        , update = updateModel
        , subscriptions = \_ -> Sub.none
        }


viewModel : Model -> List (Html Msg)
viewModel model =
    ModuleHelpers.titleWithAttributions
        placeModuleName
        model.active
        ToggleActive
        Close
        attributions
        ++ if model.active then
            userInteractionsView model
           else
            [ Html.text "" ]


toggleActive : Model -> ( Model, Cmd Msg )
toggleActive model =
    if model.active then
        updateModel SendJson
            { model
                | className = "None"
                , active = False
            }
    else
        updateModel SendJson
            { model
                | className = pythonClassName
                , active = True
            }


close : ( Model, Cmd Msg )
close =
    let
        ( clearModel, clearModelCmd ) =
            updateModel SendJson defaultModel
    in
        clearModel ! [ clearModelCmd, removeModule pythonClassName ]


changePriority : String -> Model -> ( Model, Cmd Msg )
changePriority newPriority model =
    updateModel SendJson { model | priority = newPriority }


sendJson : Model -> ( Model, Cmd Msg )
sendJson model =
    ( model
    , config
        (Json.Encode.list
            [ Json.Encode.object
                [ ( "python_module_name", Json.Encode.string pythonModuleName )
                , ( "python_class_name", Json.Encode.string model.className )
                , ( "elm_module_name", Json.Encode.string "MokuLab" )
                , ( "priority"
                  , Json.Encode.int
                        (ModuleHelpers.intDefault defaultModel.priority model.priority)
                  )
                , ( "data_register"
                  , Json.Encode.list
                        (List.map Json.Encode.string
                            (List.map (\s -> (pythonClassName ++ "-" ++ s)) (dataRegister model))
                        )
                  )
                , ( "config", Json.Encode.object (jsonValues model) )
                ]
            ]
        )
    )
