port module AlazarTech exposing (main)

import Html exposing (Html)
import Html.Events
import Html.Attributes
import Json.Encode
import ModuleHelpers


attributions : ModuleHelpers.Attributions
attributions =
    { authors = [ "Paul Freeman" ]
    , maintainer = "Paul Freeman"
    , maintainerEmail = "pfre484@aucklanduni.ac.nz"
    }


main : Program Never AlazarInstrument Msg
main =
    Html.program
        { init = ( default "None", Cmd.none )
        , view = \instrument -> Html.div [] (view instrument)
        , update = update
        , subscriptions = always <| processProgress UpdateProgress
        }


view : AlazarInstrument -> List (Html Msg)
view instrument =
    let
        disableInput =
            case instrument.progress of
                Nothing ->
                    False

                Just value ->
                    True
    in
        ModuleHelpers.titleWithAttributions "AlazarTech PC oscilloscope"
            instrument.active
            ToggleActive
            Close
            attributions
            ++ if instrument.active then
                nameView instrument
                    :: configView instrument
                    ++ [ ModuleHelpers.displayAllProgress instrument.progress ]
               else
                [ Html.text "" ]


type alias AlazarInstrument =
    { name : String
    , priority : Int
    , config : Config
    , active : Bool
    , viewOption : String
    , progress : Maybe Json.Encode.Value
    }


{-| This type contains all the configuration options needed by the Alazar card.

These values should not be needed by PLACE outside of the PLACE driver written
for this instrument.

-}
type alias Config =
    { clock_source : String
    , sample_rate : String
    , clock_edge : String
    , decimation : Int
    , analog_inputs : List AnalogInput
    , trigger_operation : String
    , trigger_engine_1 : String
    , trigger_source_1 : String
    , trigger_slope_1 : String
    , triggerLevelString1 : String
    , trigger_engine_2 : String
    , trigger_source_2 : String
    , trigger_slope_2 : String
    , triggerLevelString2 : String
    , pre_trigger_samples : Int
    , post_trigger_samples : Int
    , records : Int
    , average : Bool
    , plot : String
    }


{-| There can be zero to many analog inputs, so we represent these as a list.

This type represents one analog input and can be configured individually.

-}
type alias AnalogInput =
    { input_channel : String
    , input_coupling : String
    , input_range : String
    }



--------------
-- MESSAGES --
--------------


{-| There are only two messages for changing the instrument. Either the name
changes, or the configuration changes.
-}
type Msg
    = ToggleActive
    | ChangeName String
    | ChangePriority String
    | ChangeConfig ConfigMsg
    | ChangeViewOption String
    | SendJson
    | UpdateProgress Json.Encode.Value
    | Close


{-| The update method is called by the web interface whenever something is changed.

If the instrument name is changed, the config is reset to the defaults for the
new instrument. If a configuration is changed, that change comes with a new
message that is used to indicate the config change desired.

-}
update : Msg -> AlazarInstrument -> ( AlazarInstrument, Cmd Msg )
update msg instrument =
    case msg of
        ToggleActive ->
            if instrument.active then
                update SendJson <| default "None"
            else
                update SendJson { instrument | active = True }

        ChangeName newInstrument ->
            update SendJson <| default newInstrument

        ChangePriority newValue ->
            update SendJson <|
                { instrument
                    | priority = Result.withDefault 100 <| String.toInt newValue
                }

        ChangeConfig configMsg ->
            update SendJson <|
                { instrument
                    | config = updateConfig configMsg instrument.config
                }

        ChangeViewOption newValue ->
            update SendJson <| { instrument | viewOption = newValue }

        SendJson ->
            ( instrument, config <| toJson instrument )

        UpdateProgress progress ->
            ( { instrument | progress = Just progress }, Cmd.none )

        Close ->
            let
                ( model, sendJsonCmd ) =
                    update SendJson (default "None")
            in
                model ! [ sendJsonCmd, removeModule "AlazarTech" ]


{-| These messages are used to change config values.
-}
type ConfigMsg
    = ChangeClockSource String
    | ChangeSampleRate String
    | ChangeClockEdge String
    | ChangeDecimation String
    | ChangeAnalogInputs AnalogInputsMsg
    | ChangeTriggerOperation String
    | ChangeTriggerEngine1 String
    | ChangeTriggerEngine2 String
    | ChangeTriggerSource1 String
    | ChangeTriggerSource2 String
    | ChangeTriggerSlope1 String
    | ChangeTriggerSlope2 String
    | ChangeTriggerLevel1 String
    | ChangeTriggerLevel2 String
    | ChangePreTriggerSamples String
    | ChangePostTriggerSamples String
    | ChangeRecords String
    | ToggleAverage
    | ChangePlot String


{-| Processes the change indicated by the message to construct a new
configuration from the current configuration.
-}
updateConfig : ConfigMsg -> Config -> Config
updateConfig configMsg config =
    case configMsg of
        ChangeClockSource newValue ->
            ({ config | clock_source = newValue })

        ChangeSampleRate newValue ->
            ({ config | sample_rate = newValue })

        ChangeClockEdge newValue ->
            ({ config | clock_edge = newValue })

        ChangeDecimation newValue ->
            ({ config | decimation = Result.withDefault 0 (String.toInt newValue) })

        ChangeAnalogInputs analogInputsMsg ->
            ({ config
                | analog_inputs =
                    updateAnalogInputs analogInputsMsg config.analog_inputs
             }
            )

        ChangeTriggerOperation newValue ->
            ({ config | trigger_operation = newValue })

        ChangeTriggerEngine1 newValue ->
            ({ config | trigger_engine_1 = newValue })

        ChangeTriggerEngine2 newValue ->
            ({ config | trigger_engine_2 = newValue })

        ChangeTriggerSource1 newValue ->
            ({ config | trigger_source_1 = newValue })

        ChangeTriggerSource2 newValue ->
            ({ config | trigger_source_2 = newValue })

        ChangeTriggerSlope1 newValue ->
            ({ config | trigger_slope_1 = newValue })

        ChangeTriggerSlope2 newValue ->
            ({ config | trigger_slope_2 = newValue })

        ChangeTriggerLevel1 newValue ->
            ({ config | triggerLevelString1 = newValue })

        ChangeTriggerLevel2 newValue ->
            ({ config | triggerLevelString2 = newValue })

        ChangePreTriggerSamples newValue ->
            ({ config | pre_trigger_samples = Result.withDefault 0 <| String.toInt newValue })

        ChangePostTriggerSamples newValue ->
            ({ config | post_trigger_samples = Result.withDefault 256 <| String.toInt newValue })

        ChangeRecords newValue ->
            ({ config | records = clampWithDefault 1 1 1000 newValue })

        ToggleAverage ->
            ({ config | average = not config.average })

        ChangePlot newValue ->
            ({ config | plot = newValue })


{-| Analog inputs are contained in a list and have special messages associated
with changing them. Typically, these messages specify which element in the list
needs to be modified.
-}
type AnalogInputsMsg
    = AddAnalogInput
    | DeleteAnalogInput Int
    | ChangeInputChannel Int String
    | ChangeInputRange Int String
    | ChangeInputCoupling Int String


{-| Process analog input changes.
-}
updateAnalogInputs : AnalogInputsMsg -> List AnalogInput -> List AnalogInput
updateAnalogInputs analogInputsMsg analog_inputs =
    case analogInputsMsg of
        AddAnalogInput ->
            List.append analog_inputs <| List.singleton defaultAnalogInput

        DeleteAnalogInput n ->
            List.take (n - 1) analog_inputs ++ List.drop n analog_inputs

        ChangeInputChannel n newValue ->
            let
                change =
                    List.head ((List.drop (n - 1)) analog_inputs)
            in
                case change of
                    Nothing ->
                        analog_inputs

                    Just changeMe ->
                        List.take (n - 1) analog_inputs
                            ++ [ { changeMe | input_channel = newValue } ]
                            ++ List.drop n analog_inputs

        ChangeInputRange n newValue ->
            let
                change =
                    List.head ((List.drop (n - 1)) analog_inputs)
            in
                case change of
                    Nothing ->
                        analog_inputs

                    Just changeMe ->
                        List.take (n - 1) analog_inputs
                            ++ [ { changeMe | input_range = newValue } ]
                            ++ List.drop n analog_inputs

        ChangeInputCoupling n newValue ->
            let
                change =
                    List.head ((List.drop (n - 1)) analog_inputs)
            in
                case change of
                    Nothing ->
                        analog_inputs

                    Just changeMe ->
                        List.take (n - 1) analog_inputs
                            ++ [ { changeMe | input_coupling = newValue } ]
                            ++ List.drop n analog_inputs



---------------
-- HTML DATA --
---------------


nameView : AlazarInstrument -> Html Msg
nameView instrument =
    Html.p [] <|
        [ Html.text "Name: "
        , Html.select [ Html.Events.onInput ChangeName ]
            [ anOption instrument.name "None" "None"
            , anOption instrument.name "ATS660" "ATS660"
            , anOption instrument.name "ATS9440" "ATS9440"
            ]
        ]
            ++ (if instrument.name == "None" then
                    []
                else
                    [ selectOption instrument
                    , Html.br [] []
                    , Html.text "Priority: "
                    , inputPriority instrument
                    , Html.br [] []
                    , Html.text "Plot: "
                    , selectPlot instrument
                    ]
               )


configView : AlazarInstrument -> List (Html Msg)
configView instrument =
    if instrument.name == "None" then
        []
    else
        case instrument.viewOption of
            "record" ->
                singlePortView instrument

            "timebase" ->
                timebaseView instrument

            "inputs" ->
                [ analogInputsView instrument ]

            "triggers" ->
                [ triggerControlView instrument ]

            otherwise ->
                []


timebaseView : AlazarInstrument -> List (Html Msg)
timebaseView instrument =
    Html.h4 [] [ Html.text "Clock configuration" ]
        :: [ Html.text "Clock source: "
           , selectClockSource instrument
           , Html.br [] []
           , Html.text "Sample rate: "
           , selectSampleRate instrument
           , Html.text " samples/second"
           , Html.br [] []
           , Html.text "Clock edge: "
           , selectClockEdge instrument
           , Html.br [] []
           , Html.text "Decimation: "
           , inputDecimation instrument
           , Html.br [] []
           ]


analogInputsView : AlazarInstrument -> Html Msg
analogInputsView instrument =
    let
        channelsMax =
            List.length (channelOptions instrument.name "")

        channels =
            List.length instrument.config.analog_inputs
    in
        Html.div [] <| analogInputsView_ channels channelsMax instrument


analogInputsView_ : Int -> Int -> AlazarInstrument -> List (Html Msg)
analogInputsView_ channels channelsMax instrument =
    Html.div []
        (if channels /= 0 then
            List.map2
                (analogInputView instrument)
                (List.range 1 32)
                instrument.config.analog_inputs
         else
            [ Html.text "" ]
        )
        :: (if channels < channelsMax then
                [ Html.button
                    [ Html.Events.onClick (ChangeConfig <| ChangeAnalogInputs AddAnalogInput) ]
                    [ Html.text "Add input" ]
                ]
            else
                [ Html.text "" ]
           )


analogInputView : AlazarInstrument -> Int -> AnalogInput -> Html Msg
analogInputView instrument num analogInput =
    Html.div [ Html.Attributes.class "horizontal-align" ] <|
        Html.h4 [] [ Html.text ("Channel " ++ toString num) ]
            :: [ Html.text "Input channel: "
               , selectInputChannel instrument analogInput num
               , Html.br [] []
               , Html.text "Input coupling: "
               , selectInputCoupling analogInput num
               , Html.br [] []
               , Html.text "Input range: "
               , selectInputRange instrument analogInput num
               , Html.br [] []
               , Html.button
                    [ Html.Events.onClick
                        (ChangeConfig <|
                            ChangeAnalogInputs
                                << DeleteAnalogInput
                            <|
                                num
                        )
                    ]
                    [ Html.text "Delete input" ]
               ]


triggerControlView : AlazarInstrument -> Html Msg
triggerControlView instrument =
    Html.div [] <|
        [ Html.div [ Html.Attributes.class "horizontal-align" ] <|
            [ Html.h4 [] [ Html.text "Trigger 1" ]
            , Html.text "Trigger source: "
            , selectTriggerSource1 instrument
            ]
                ++ (if instrument.config.trigger_source_1 == "TRIG_DISABLE" then
                        [ Html.text "" ]
                    else if instrument.config.trigger_source_1 == "TRIG_FORCE" then
                        [ Html.text "" ]
                    else
                        [ Html.br [] []
                        , Html.text "Trigger engine: "
                        , selectTriggerEngine1 instrument
                        , Html.br [] []
                        , Html.text "Trigger slope: "
                        , selectTriggerSlope1 instrument
                        , Html.br [] []
                        , Html.text "Trigger level: "
                        , inputTriggerLevel1 instrument
                        , Html.text " volts"
                        ]
                            ++ if instrument.config.trigger_source_1 == "TRIG_EXTERNAL" then
                                [ Html.text "" ]
                               else
                                rangeError (calculatedTrigger1 instrument.config)
                   )
        , Html.div [ Html.Attributes.class "horizontal-align" ] <|
            [ Html.h4 [] [ Html.text "Trigger 2" ]
            , Html.text "Trigger source: "
            , selectTriggerSource2 instrument
            ]
                ++ (if instrument.config.trigger_source_2 == "TRIG_DISABLE" then
                        [ Html.text "" ]
                    else if instrument.config.trigger_source_2 == "TRIG_FORCE" then
                        [ Html.text "" ]
                    else
                        [ Html.br [] []
                        , Html.text "Trigger engine: "
                        , selectTriggerEngine2 instrument
                        , Html.br [] []
                        , Html.text "Trigger slope: "
                        , selectTriggerSlope2 instrument
                        , Html.br [] []
                        , Html.text "Trigger level: "
                        , inputTriggerLevel2 instrument
                        , Html.text " volts"
                        ]
                            ++ if instrument.config.trigger_source_2 == "TRIG_EXTERNAL" then
                                [ Html.text "" ]
                               else
                                rangeError (calculatedTrigger2 instrument.config)
                   )
        , Html.div []
            [ Html.text "Trigger operation: "
            , selectTriggerOperation instrument
            ]
        ]


rangeError : Int -> List (Html Msg)
rangeError num =
    if 0 <= num && num <= 255 then
        [ Html.text "" ]
    else
        [ Html.br [] []
        , Html.span [ Html.Attributes.class "error-text" ]
            [ Html.text "Error: trigger voltage is invalid or out of range" ]
        ]


calculatedTrigger1 : Config -> Int
calculatedTrigger1 config =
    let
        value =
            case String.toFloat config.triggerLevelString1 of
                Err _ ->
                    0.0

                Ok num ->
                    num

        trig_source =
            case config.trigger_source_1 of
                "TRIG_CHAN_A" ->
                    "CHANNEL_A"

                "TRIG_CHAN_B" ->
                    "CHANNEL_B"

                "TRIG_CHAN_C" ->
                    "CHANNEL_C"

                "TRIG_CHAN_D" ->
                    "CHANNEL_D"

                otherwise ->
                    "nothing"

        inputHead =
            List.head <|
                List.filter
                    (\x -> x.input_channel == trig_source)
                    config.analog_inputs
    in
        if config.trigger_source_1 == "TRIG_EXTERNAL" then
            toIntLevel value 5.0
        else
            case inputHead of
                Nothing ->
                    -1

                Just input ->
                    toIntLevel value <| getInputRange input


calculatedTrigger2 : Config -> Int
calculatedTrigger2 config =
    let
        value =
            case String.toFloat config.triggerLevelString2 of
                Err _ ->
                    0.0

                Ok num ->
                    num

        trig_source =
            case config.trigger_source_2 of
                "TRIG_CHAN_A" ->
                    "CHANNEL_A"

                "TRIG_CHAN_B" ->
                    "CHANNEL_B"

                "TRIG_CHAN_C" ->
                    "CHANNEL_C"

                "TRIG_CHAN_D" ->
                    "CHANNEL_D"

                otherwise ->
                    "nothing"

        inputList =
            List.head <|
                List.filter
                    (\x -> x.input_channel == trig_source)
                    config.analog_inputs
    in
        if config.trigger_source_2 == "TRIG_EXTERNAL" then
            toIntLevel value 5.0
        else
            case inputList of
                Nothing ->
                    -1

                Just input ->
                    toIntLevel value <| getInputRange input


getInputRange : AnalogInput -> Float
getInputRange input =
    case input.input_range of
        "100mv-50ohm" ->
            0.1

        "200mv-50ohm" ->
            0.2

        "200mv-1Mohm" ->
            0.2

        "400mv-50ohm" ->
            0.4

        "400mv-1Mohm" ->
            0.4

        "800mv-50ohm" ->
            0.8

        "800mv-1Mohm" ->
            0.8

        "1v-50ohm" ->
            1.0

        "1v-1Mohm" ->
            1.0

        "2v-50ohm" ->
            2.0

        "2v-1Mohm" ->
            2.0

        "4v-50ohm" ->
            4.0

        "4v-1Mohm" ->
            4.0

        "8v-1Mohm" ->
            8.0

        "16v-1Mohm" ->
            16.0

        otherwise ->
            -1.0


toIntLevel : Float -> Float -> Int
toIntLevel triggerLevelVolts inputRangeVolts =
    128 + (round <| 127.0 * triggerLevelVolts / inputRangeVolts)


singlePortView : AlazarInstrument -> List (Html Msg)
singlePortView instrument =
    Html.h4 [] [ Html.text "Single port acquisition" ]
        :: [ Html.text "Pre-trigger samples: "
           , inputPreTriggerSamples instrument
           , Html.text <|
                " ("
                    ++ toString
                        (calculateTime
                            instrument.config.pre_trigger_samples
                            instrument.config.sample_rate
                        )
                    ++ " microsecs)"
           , Html.br [] []
           , Html.text "Post-trigger samples: "
           , inputPostTriggerSamples instrument
           , Html.text <|
                " ("
                    ++ toString
                        (calculateTime
                            instrument.config.post_trigger_samples
                            instrument.config.sample_rate
                        )
                    ++ " microsecs)"
           , Html.br [] []
           , Html.text "Number of records: "
           , inputRecords instrument
           , Html.br [] []
           , Html.text "Average all records together: "
           , Html.input
                [ Html.Attributes.type_ "checkbox"
                , Html.Attributes.checked instrument.config.average
                , Html.Events.onClick (ChangeConfig <| ToggleAverage)
                ]
                []
           ]


calculateTime : Int -> String -> Float
calculateTime numberSamples sampleRate =
    let
        samples =
            toFloat numberSamples
    in
        case sampleRate of
            "SAMPLE_RATE_1KSPS" ->
                samples / 0.001

            "SAMPLE_RATE_2KSPS" ->
                samples / 0.002

            "SAMPLE_RATE_5KSPS" ->
                samples / 0.005

            "SAMPLE_RATE_10KSPS" ->
                samples / 0.01

            "SAMPLE_RATE_20KSPS" ->
                samples / 0.02

            "SAMPLE_RATE_50KSPS" ->
                samples / 0.05

            "SAMPLE_RATE_100KSPS" ->
                samples / 0.1

            "SAMPLE_RATE_200KSPS" ->
                samples / 0.2

            "SAMPLE_RATE_500KSPS" ->
                samples / 0.5

            "SAMPLE_RATE_1MSPS" ->
                samples / 1

            "SAMPLE_RATE_2MSPS" ->
                samples / 2

            "SAMPLE_RATE_5MSPS" ->
                samples / 5

            "SAMPLE_RATE_10MSPS" ->
                samples / 10

            "SAMPLE_RATE_20MSPS" ->
                samples / 20

            "SAMPLE_RATE_50MSPS" ->
                samples / 50

            "SAMPLE_RATE_100MSPS" ->
                samples / 100

            "SAMPLE_RATE_125MSPS" ->
                samples / 125

            otherwise ->
                0.0



------------------------
-- SELECTION ELEMENtS --
------------------------


selectOption : AlazarInstrument -> Html Msg
selectOption instrument =
    if instrument.name == "None" then
        Html.text ""
    else
        Html.select [ Html.Events.onInput ChangeViewOption ]
            [ anOption instrument.viewOption "none" "Options"
            , anOption instrument.viewOption "record" "Configure record"
            , anOption instrument.viewOption "timebase" "Configure clock"
            , anOption instrument.viewOption "inputs" "Configure Inputs"
            , anOption instrument.viewOption "triggers" "Configure triggers"
            ]


inputPriority : AlazarInstrument -> Html Msg
inputPriority instrument =
    Html.input
        [ Html.Attributes.value <| toString instrument.priority
        , Html.Attributes.type_ "number"
        , Html.Events.onInput ChangePriority
        ]
        []


selectTriggerOperation : AlazarInstrument -> Html Msg
selectTriggerOperation instrument =
    let
        val =
            instrument.config.trigger_operation
    in
        Html.select [ Html.Events.onInput (ChangeConfig << ChangeTriggerOperation) ] <|
            triggerOperationOptions val


selectTriggerEngine1 : AlazarInstrument -> Html Msg
selectTriggerEngine1 instrument =
    let
        val =
            instrument.config.trigger_engine_1
    in
        Html.select [ Html.Events.onInput (ChangeConfig << ChangeTriggerEngine1) ] <|
            triggerEngineOptions val


selectTriggerEngine2 : AlazarInstrument -> Html Msg
selectTriggerEngine2 instrument =
    let
        val =
            instrument.config.trigger_engine_2
    in
        Html.select [ Html.Events.onInput (ChangeConfig << ChangeTriggerEngine2) ] <|
            triggerEngineOptions val


selectTriggerSource1 : AlazarInstrument -> Html Msg
selectTriggerSource1 instrument =
    let
        name =
            instrument.name

        val =
            instrument.config.trigger_source_1
    in
        Html.select [ Html.Events.onInput (ChangeConfig << ChangeTriggerSource1) ] <|
            triggerChannelOptions name val


selectTriggerSource2 : AlazarInstrument -> Html Msg
selectTriggerSource2 instrument =
    let
        name =
            instrument.name

        val =
            instrument.config.trigger_source_2
    in
        Html.select [ Html.Events.onInput (ChangeConfig << ChangeTriggerSource2) ] <|
            triggerChannelOptions name val


selectTriggerSlope1 : AlazarInstrument -> Html Msg
selectTriggerSlope1 instrument =
    let
        val =
            instrument.config.trigger_slope_1
    in
        Html.select [ Html.Events.onInput (ChangeConfig << ChangeTriggerSlope1) ] <|
            triggerSlopeOptions val


selectTriggerSlope2 : AlazarInstrument -> Html Msg
selectTriggerSlope2 instrument =
    let
        val =
            instrument.config.trigger_slope_2
    in
        Html.select [ Html.Events.onInput (ChangeConfig << ChangeTriggerSlope2) ] <|
            triggerSlopeOptions val


inputTriggerLevel1 : AlazarInstrument -> Html Msg
inputTriggerLevel1 instrument =
    Html.input
        [ Html.Attributes.value instrument.config.triggerLevelString1
        , Html.Events.onInput (ChangeConfig << ChangeTriggerLevel1)
        ]
        []


inputTriggerLevel2 : AlazarInstrument -> Html Msg
inputTriggerLevel2 instrument =
    Html.input
        [ Html.Attributes.value instrument.config.triggerLevelString2
        , Html.Events.onInput (ChangeConfig << ChangeTriggerLevel2)
        ]
        []


{-| clock source select menu
-}
selectClockSource : AlazarInstrument -> Html Msg
selectClockSource instrument =
    let
        name =
            instrument.name

        val =
            instrument.config.clock_source
    in
        Html.select [ Html.Events.onInput (ChangeConfig << ChangeClockSource) ] <|
            clockSourceOptions name val


selectSampleRate : AlazarInstrument -> Html Msg
selectSampleRate instrument =
    let
        name =
            instrument.name

        val =
            instrument.config.sample_rate
    in
        Html.select [ Html.Events.onInput (ChangeConfig << ChangeSampleRate) ] <|
            sampleRateOptions name val


selectClockEdge : AlazarInstrument -> Html Msg
selectClockEdge instrument =
    let
        val =
            instrument.config.clock_edge
    in
        Html.select [ Html.Events.onInput (ChangeConfig << ChangeClockEdge) ] <|
            clockEdgeOptions val


inputDecimation : AlazarInstrument -> Html Msg
inputDecimation instrument =
    Html.input
        [ Html.Attributes.value <| toString instrument.config.decimation
        , Html.Attributes.type_ "number"
        , Html.Events.onInput (ChangeConfig << ChangeDecimation)
        ]
        []


selectInputChannel : AlazarInstrument -> AnalogInput -> Int -> Html Msg
selectInputChannel instrument analogInput num =
    let
        name =
            instrument.name

        val =
            analogInput.input_channel
    in
        Html.select
            [ Html.Events.onInput (ChangeConfig << ChangeAnalogInputs << (ChangeInputChannel num)) ]
        <|
            channelOptions name val


selectInputCoupling : AnalogInput -> Int -> Html Msg
selectInputCoupling input num =
    let
        val =
            input.input_coupling
    in
        Html.select
            [ Html.Events.onInput (ChangeConfig << ChangeAnalogInputs << (ChangeInputCoupling num)) ]
        <|
            inputChannelOptions val


selectInputRange : AlazarInstrument -> AnalogInput -> Int -> Html Msg
selectInputRange instrument input num =
    let
        name =
            instrument.name

        val =
            input.input_range
    in
        Html.select
            [ Html.Events.onInput (ChangeConfig << ChangeAnalogInputs << (ChangeInputRange num)) ]
        <|
            inputRangeOptions name val


inputPreTriggerSamples : AlazarInstrument -> Html Msg
inputPreTriggerSamples instrument =
    Html.input
        [ Html.Attributes.value <| toString instrument.config.pre_trigger_samples
        , Html.Attributes.type_ "number"
        , Html.Events.onInput (ChangeConfig << ChangePreTriggerSamples)
        ]
        []


inputPostTriggerSamples : AlazarInstrument -> Html Msg
inputPostTriggerSamples instrument =
    Html.input
        [ Html.Attributes.value <| toString instrument.config.post_trigger_samples
        , Html.Attributes.type_ "number"
        , Html.Events.onInput (ChangeConfig << ChangePostTriggerSamples)
        ]
        []


inputRecords : AlazarInstrument -> Html Msg
inputRecords instrument =
    Html.input
        [ Html.Attributes.value <| toString instrument.config.records
        , Html.Attributes.type_ "number"
        , Html.Events.onInput (ChangeConfig << ChangeRecords)
        ]
        []


selectPlot : AlazarInstrument -> Html Msg
selectPlot instrument =
    let
        val =
            instrument.config.plot
    in
        Html.select [ Html.Events.onInput (ChangeConfig << ChangePlot) ] <|
            plotOptions val



-------------
-- OPTIONS --
-------------


sampleRateOptions : String -> String -> List (Html Msg)
sampleRateOptions name val =
    case name of
        "ATS660" ->
            [ anOption val "SAMPLE_RATE_1KSPS" "1K"
            , anOption val "SAMPLE_RATE_2KSPS" "2K"
            , anOption val "SAMPLE_RATE_5KSPS" "5K"
            , anOption val "SAMPLE_RATE_10KSPS" "10K"
            , anOption val "SAMPLE_RATE_20KSPS" "20K"
            , anOption val "SAMPLE_RATE_50KSPS" "50K"
            , anOption val "SAMPLE_RATE_100KSPS" "100K"
            , anOption val "SAMPLE_RATE_200KSPS" "200K"
            , anOption val "SAMPLE_RATE_500KSPS" "500K"
            , anOption val "SAMPLE_RATE_1MSPS" "1M"
            , anOption val "SAMPLE_RATE_2MSPS" "2M"
            , anOption val "SAMPLE_RATE_5MSPS" "5M"
            , anOption val "SAMPLE_RATE_10MSPS" "10M"
            , anOption val "SAMPLE_RATE_20MSPS" "20M"
            , anOption val "SAMPLE_RATE_50MSPS" "50M"
            , anOption val "SAMPLE_RATE_100MSPS" "100M"
            , anOption val "SAMPLE_RATE_125MSPS" "125M"
            , anOption val "SAMPLE_RATE_USER_DEF" "user-defined"
            ]

        "ATS9440" ->
            [ anOption val "SAMPLE_RATE_1KSPS" "1K"
            , anOption val "SAMPLE_RATE_2KSPS" "2K"
            , anOption val "SAMPLE_RATE_5KSPS" "5K"
            , anOption val "SAMPLE_RATE_10KSPS" "10K"
            , anOption val "SAMPLE_RATE_20KSPS" "20K"
            , anOption val "SAMPLE_RATE_50KSPS" "50K"
            , anOption val "SAMPLE_RATE_100KSPS" "100K"
            , anOption val "SAMPLE_RATE_200KSPS" "200K"
            , anOption val "SAMPLE_RATE_500KSPS" "500K"
            , anOption val "SAMPLE_RATE_1MSPS" "1M"
            , anOption val "SAMPLE_RATE_2MSPS" "2M"
            , anOption val "SAMPLE_RATE_5MSPS" "5M"
            , anOption val "SAMPLE_RATE_10MSPS" "10M"
            , anOption val "SAMPLE_RATE_20MSPS" "20M"
            , anOption val "SAMPLE_RATE_50MSPS" "50M"
            , anOption val "SAMPLE_RATE_100MSPS" "100M"
            , anOption val "SAMPLE_RATE_125MSPS" "125M"
            , anOption val "SAMPLE_RATE_USER_DEF" "user-defined"
            ]

        otherwise ->
            []


clockSourceOptions : String -> String -> List (Html Msg)
clockSourceOptions name val =
    case name of
        "ATS660" ->
            [ anOption val "INTERNAL_CLOCK" "Internal Clock"
            , anOption val "SLOW_EXTERNAL_CLOCK" "External Clock (slow)"
            , anOption val "EXTERNAL_CLOCK_AC" "External Clock (AC)"
            , anOption val "EXTERNAL_CLOCK_DC" "External Clock (DC)"
            , anOption val "EXTERNAL_CLOCK_10_MHZ_REF" "External Clock (10MHz)"
            ]

        "ATS9440" ->
            [ anOption val "INTERNAL_CLOCK" "Internal Clock"
            , anOption val "FAST_EXTERNAL_CLOCK" "External Clock (fast)"
            , anOption val "SLOW_EXTERNAL_CLOCK" "External Clock (slow)"
            , anOption val "EXTERNAL_CLOCK_10_MHZ_REF" "External Clock (10MHz)"
            ]

        otherwise ->
            []


clockEdgeOptions : String -> List (Html Msg)
clockEdgeOptions val =
    [ anOption val "CLOCK_EDGE_RISING" "rising edge"
    , anOption val "CLOCK_EDGE_FALLING" "falling edge"
    ]


channelOptions : String -> String -> List (Html Msg)
channelOptions name val =
    case name of
        "ATS660" ->
            [ anOption val "CHANNEL_A" "channel A"
            , anOption val "CHANNEL_B" "channel B"
            ]

        "ATS9440" ->
            [ anOption val "CHANNEL_A" "channel A"
            , anOption val "CHANNEL_B" "channel B"
            , anOption val "CHANNEL_C" "channel C"
            , anOption val "CHANNEL_D" "channel D"
            ]

        otherwise ->
            []


inputChannelOptions : String -> List (Html Msg)
inputChannelOptions val =
    [ anOption val "AC_COUPLING" "AC coupling"
    , anOption val "DC_COUPLING" "DC coupling"
    ]


inputRangeOptions : String -> String -> List (Html Msg)
inputRangeOptions name val =
    case name of
        "ATS660" ->
            [ anOption val "200mv-50ohm" "+/- 200 mV, 50 ohm"
            , anOption val "400mv-50ohm" "+/- 400 mV, 50 ohm"
            , anOption val "800mv-50ohm" "+/- 800 mV, 50 ohm"
            , anOption val "2v-50ohm" "+/- 2 V, 50 ohm"
            , anOption val "4v-50ohm" "+/- 4 V, 50 ohm"
            , anOption val "200mv-1Mohm" "+/- 200 mV, 1 Mohm"
            , anOption val "400mv-1Mohm" "+/- 400 mV, 1 Mohm"
            , anOption val "800mv-1Mohm" "+/- 800 mV, 1 Mohm"
            , anOption val "2v-1Mohm" "+/- 2 V, 1 Mohm"
            , anOption val "4v-1Mohm" "+/- 4 V, 1 Mohm"
            , anOption val "8v-1Mohm" "+/- 8 V, 1 Mohm"
            , anOption val "16v-1Mohm" "+/- 16 V, 1 Mohm"
            ]

        "ATS9440" ->
            [ anOption val "100mv-50ohm" "+/- 100 mV, 50 ohm"
            , anOption val "200mv-50ohm" "+/- 200 mV, 50 ohm"
            , anOption val "400mv-50ohm" "+/- 400 mV, 50 ohm"
            , anOption val "1v-50ohm" "+/- 1 V, 50 ohm"
            , anOption val "2v-50ohm" "+/- 2 V, 50 ohm"
            , anOption val "4v-50ohm" "+/- 4 V, 50 ohm"
            ]

        otherwise ->
            []


triggerOperationOptions : String -> List (Html Msg)
triggerOperationOptions val =
    [ anOption val "TRIG_ENGINE_OP_J" "Trigger J goes low to high"
    , anOption val "TRIG_ENGINE_OP_K" "Trigger K goes low to high"
    , anOption val "TRIG_ENGINE_OP_J_OR_K" "(J OR K) goes low to high"
    , anOption val "TRIG_ENGINE_OP_J_AND_K" "(J AND K) goes low to high"
    , anOption val "TRIG_ENGINE_OP_J_XOR_K" "(J XOR K) goes low to high"
    , anOption val "TRIG_ENGINE_OP_J_AND_NOT_K" "(J AND (NOT K)) goes low to high"
    , anOption val "TRIG_ENGINE_OP_NOT_J_AND_K" "((NOT J) AND K) goes low to high"
    ]


triggerEngineOptions : String -> List (Html Msg)
triggerEngineOptions val =
    [ anOption val "TRIG_ENGINE_J" "Trigger engine J"
    , anOption val "TRIG_ENGINE_K" "Trigger engine K"
    ]


triggerChannelOptions : String -> String -> List (Html Msg)
triggerChannelOptions name val =
    case name of
        "ATS660" ->
            [ anOption val "TRIG_CHAN_A" "channel A"
            , anOption val "TRIG_CHAN_B" "channel B"
            , anOption val "TRIG_EXTERNAL" "external trigger"
            , anOption val "TRIG_DISABLE" "disabled"
            , anOption val "TRIG_FORCE" "instant trigger"
            ]

        "ATS9440" ->
            [ anOption val "TRIG_CHAN_A" "channel A"
            , anOption val "TRIG_CHAN_B" "channel B"
            , anOption val "TRIG_CHAN_C" "channel C"
            , anOption val "TRIG_CHAN_D" "channel D"
            , anOption val "TRIG_EXTERNAL" "external trigger"
            , anOption val "TRIG_DISABLE" "disabled"
            , anOption val "TRIG_FORCE" "instant trigger"
            ]

        otherwise ->
            []


triggerSlopeOptions : String -> List (Html Msg)
triggerSlopeOptions val =
    [ anOption val "TRIGGER_SLOPE_POSITIVE" "Positive trigger"
    , anOption val "TRIGGER_SLOPE_NEGATIVE" "Negative trigger"
    ]


plotOptions : String -> List (Html Msg)
plotOptions val =
    [ anOption val "yes" "yes"
    , anOption val "no" "no"
    ]



--------------
-- DEFAULTS --
--------------


default : String -> AlazarInstrument
default name =
    if name == "None" then
        { name = name
        , priority = 100
        , config = defaultConfig
        , active = False
        , viewOption = "none"
        , progress = Nothing
        }
    else
        { name = name
        , priority = 100
        , config = defaultConfig
        , active = True
        , viewOption = "none"
        , progress = Nothing
        }


defaultConfig : Config
defaultConfig =
    { clock_source = "INTERNAL_CLOCK"
    , sample_rate = "SAMPLE_RATE_10MSPS"
    , clock_edge = "CLOCK_EDGE_RISING"
    , decimation = 0
    , analog_inputs = List.singleton defaultAnalogInput
    , trigger_operation = "TRIG_ENGINE_OP_J"
    , trigger_engine_1 = "TRIG_ENGINE_J"
    , trigger_source_1 = "TRIG_CHAN_A"
    , trigger_slope_1 = "TRIGGER_SLOPE_POSITIVE"
    , triggerLevelString1 = "1.0"
    , trigger_engine_2 = "TRIG_ENGINE_K"
    , trigger_source_2 = "TRIG_DISABLE"
    , trigger_slope_2 = "TRIGGER_SLOPE_POSITIVE"
    , triggerLevelString2 = "1.0"
    , pre_trigger_samples = 0
    , post_trigger_samples = 1024
    , records = 1
    , average = False
    , plot = "yes"
    }


defaultAnalogInput : AnalogInput
defaultAnalogInput =
    { input_channel = "CHANNEL_A"
    , input_coupling = "DC_COUPLING"
    , input_range = "2v-50ohm"
    }


port config : Json.Encode.Value -> Cmd msg


port processProgress : (Json.Encode.Value -> msg) -> Sub msg


port removeModule : String -> Cmd msg


toJson : AlazarInstrument -> Json.Encode.Value
toJson instrument =
    Json.Encode.list
        [ Json.Encode.object
            [ ( "python_module_name", Json.Encode.string "alazartech" )
            , ( "python_class_name", Json.Encode.string instrument.name )
            , ( "elm_module_name", Json.Encode.string "AlazarTech" )
            , ( "priority", Json.Encode.int instrument.priority )
            , ( "data_register"
              , Json.Encode.list
                    (List.map Json.Encode.string [ instrument.name ++ "-trace" ])
              )
            , ( "config", configToJson instrument.config )
            ]
        ]


configToJson : Config -> Json.Encode.Value
configToJson config =
    Json.Encode.object
        [ ( "clock_source", Json.Encode.string config.clock_source )
        , ( "sample_rate", Json.Encode.string config.sample_rate )
        , ( "clock_edge", Json.Encode.string config.clock_edge )
        , ( "decimation", Json.Encode.int config.decimation )
        , ( "analog_inputs", analogInputsToJson config.analog_inputs )
        , ( "trigger_operation", Json.Encode.string config.trigger_operation )
        , ( "trigger_engine_1", Json.Encode.string config.trigger_engine_1 )
        , ( "trigger_source_1", Json.Encode.string config.trigger_source_1 )
        , ( "trigger_slope_1", Json.Encode.string config.trigger_slope_1 )
        , ( "trigger_level_1", Json.Encode.int <| clamp 0 255 <| calculatedTrigger1 config )
        , ( "trigger_engine_2", Json.Encode.string config.trigger_engine_2 )
        , ( "trigger_source_2", Json.Encode.string config.trigger_source_2 )
        , ( "trigger_slope_2", Json.Encode.string config.trigger_slope_2 )
        , ( "trigger_level_2", Json.Encode.int <| clamp 0 255 <| calculatedTrigger2 config )
        , ( "pre_trigger_samples", Json.Encode.int config.pre_trigger_samples )
        , ( "post_trigger_samples", Json.Encode.int config.post_trigger_samples )
        , ( "records", Json.Encode.int config.records )
        , ( "average", Json.Encode.bool config.average )
        , ( "plot", Json.Encode.string config.plot )
        ]


analogInputsToJson : List AnalogInput -> Json.Encode.Value
analogInputsToJson analogInputs =
    Json.Encode.list (List.map analogInputToJson analogInputs)


analogInputToJson : AnalogInput -> Json.Encode.Value
analogInputToJson analogInput =
    let
        ( range, impedance ) =
            case analogInput.input_range of
                "100mv-50ohm" ->
                    ( "INPUT_RANGE_PM_100_MV", "IMPEDANCE_50_OHM" )

                "200mv-50ohm" ->
                    ( "INPUT_RANGE_PM_200_MV", "IMPEDANCE_50_OHM" )

                "400mv-50ohm" ->
                    ( "INPUT_RANGE_PM_400_MV", "IMPEDANCE_50_OHM" )

                "800mv-50ohm" ->
                    ( "INPUT_RANGE_PM_800_MV", "IMPEDANCE_50_OHM" )

                "1v-50ohm" ->
                    ( "INPUT_RANGE_PM_1_V", "IMPEDANCE_50_OHM" )

                "2v-50ohm" ->
                    ( "INPUT_RANGE_PM_2_V", "IMPEDANCE_50_OHM" )

                "4v-50ohm" ->
                    ( "INPUT_RANGE_PM_4_V", "IMPEDANCE_50_OHM" )

                "200mv-1Mohm" ->
                    ( "INPUT_RANGE_PM_200_MV", "IMPEDANCE_1M_OHM" )

                "400mv-1Mohm" ->
                    ( "INPUT_RANGE_PM_400_MV", "IMPEDANCE_1M_OHM" )

                "800mv-1Mohm" ->
                    ( "INPUT_RANGE_PM_800_MV", "IMPEDANCE_1M_OHM" )

                "2v-1Mohm" ->
                    ( "INPUT_RANGE_PM_2_V", "IMPEDANCE_1M_OHM" )

                "4v-1Mohm" ->
                    ( "INPUT_RANGE_PM_4_V", "IMPEDANCE_1M_OHM" )

                "8v-1Mohm" ->
                    ( "INPUT_RANGE_PM_8_V", "IMPEDANCE_1M_OHM" )

                "16v-1Mohm" ->
                    ( "INPUT_RANGE_PM_16_V", "IMPEDANCE_1M_OHM" )

                otherwise ->
                    ( "INPUT_RANGE_PM_2_V", "IMPEDANCE_50_OHM" )
    in
        Json.Encode.object
            [ ( "input_channel", Json.Encode.string analogInput.input_channel )
            , ( "input_coupling", Json.Encode.string analogInput.input_coupling )
            , ( "input_range", Json.Encode.string range )
            , ( "input_impedance", Json.Encode.string impedance )
            ]



-------------------
-- OTHER HELPERS --
-------------------


{-| Helper function to present an option in a drop-down selection box.
-}
anOption : String -> String -> String -> Html Msg
anOption str val disp =
    Html.option [ Html.Attributes.value val, Html.Attributes.selected (str == val) ]
        [ Html.text disp ]


{-| Ensures that a string returns an interger within a given range.
-}
clampWithDefault : Int -> Int -> Int -> String -> Int
clampWithDefault default min max intStr =
    clamp min max <|
        Result.withDefault default <|
            String.toInt intStr
