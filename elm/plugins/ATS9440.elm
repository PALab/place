port module AlazarTech exposing (main)

import Html exposing (Html)
import Html.Events
import Html.Attributes
import Json.Encode
import ModuleHelpers exposing (..)


attributions : Attributions
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
    titleWithAttributions "AlazarTech PC oscilloscope"
        instrument.active
        ToggleActive
        Close
        attributions
        ++ if instrument.active then
            nameView instrument
                :: configView instrument
                :: [ displayAllProgress instrument.progress ]
           else
            [ Html.text "" ]


type alias AlazarInstrument =
    { name : String
    , priority : String
    , config : Config
    , active : Bool
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
    , decimation : String
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
    , pre_trigger_samples : String
    , post_trigger_samples : String
    , records : String
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
            update SendJson { instrument | priority = newValue }

        ChangeConfig configMsg ->
            update SendJson <|
                { instrument
                    | config = updateConfig configMsg instrument.config
                }

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
            ({ config | decimation = newValue })

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
            ({ config | pre_trigger_samples = newValue })

        ChangePostTriggerSamples newValue ->
            ({ config | post_trigger_samples = newValue })

        ChangeRecords newValue ->
            ({ config | records = newValue })

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
    Html.div [] <|
        [ dropDownBox "Name"
            instrument.name
            ChangeName
            [ ( "None", "None" )
            , ( "ATS660", "ATS660" )
            , ( "ATS9440", "ATS9440" )
            ]
        ]
            ++ (if instrument.name == "None" then
                    [ Html.text "" ]
                else
                    [ floatField "Priority" instrument.priority ChangePriority
                    , dropDownBox "Plot"
                        instrument.config.plot
                        (ChangeConfig << ChangePlot)
                        [ ( "yes", "yes" ), ( "no", "no" ) ]
                    ]
               )


configView : AlazarInstrument -> Html Msg
configView instrument =
    Html.div [ Html.Attributes.id "alazarConfigView" ] <|
        if instrument.name == "None" then
            [ Html.text "" ]
        else
            [ singlePortView instrument
            , timebaseView instrument
            , analogInputsView instrument
            , triggerControlView instrument
            ]


singlePortView : AlazarInstrument -> Html Msg
singlePortView instrument =
    let
        preTime =
            toString (calculateTime instrument.config.pre_trigger_samples instrument.config.sample_rate)

        postTime =
            toString (calculateTime instrument.config.post_trigger_samples instrument.config.sample_rate)
    in
        Html.div [ Html.Attributes.id "alazarSinglePortView" ] <|
            [ Html.h4 [] [ Html.text "Single port acquisition" ]
            , integerField "Pre-trigger samples" instrument.config.pre_trigger_samples (ChangeConfig << ChangePreTriggerSamples)
            , Html.p [] [ Html.text <| "(" ++ preTime ++ " microsecs)" ]
            , integerField "Post-trigger samples" instrument.config.post_trigger_samples (ChangeConfig << ChangePostTriggerSamples)
            , Html.p [] [ Html.text <| "(" ++ postTime ++ " microsecs)" ]
            , integerField "Number of records" instrument.config.records (ChangeConfig << ChangeRecords)
            , checkbox "Average all records together" instrument.config.average (ChangeConfig <| ToggleAverage)
            ]


timebaseView : AlazarInstrument -> Html Msg
timebaseView instrument =
    Html.div [ Html.Attributes.id "alazarTimebaseView" ] <|
        [ Html.h4 [] [ Html.text "Clock configuration" ]
        , dropDownBox "Clock source" instrument.config.clock_source (ChangeConfig << ChangeClockSource) (clockSourceOptions instrument.name)
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


clockSourceOptions : String -> List ( String, String )
clockSourceOptions name =
    case name of
        "ATS660" ->
            [ ( "INTERNAL_CLOCK", "Internal Clock" )
            , ( "SLOW_EXTERNAL_CLOCK", "External Clock (slow)" )
            , ( "EXTERNAL_CLOCK_AC", "External Clock (AC)" )
            , ( "EXTERNAL_CLOCK_DC", "External Clock (DC)" )
            , ( "EXTERNAL_CLOCK_10_MHZ_REF", "External Clock (10MHz)" )
            ]

        "ATS9440" ->
            [ ( "INTERNAL_CLOCK", "Internal Clock" )
            , ( "FAST_EXTERNAL_CLOCK", "External Clock (fast)" )
            , ( "SLOW_EXTERNAL_CLOCK", "External Clock (slow)" )
            , ( "EXTERNAL_CLOCK_10_MHZ_REF", "External Clock (10MHz)" )
            ]

        otherwise ->
            []


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
                    [ Html.Attributes.class "pluginInternalButton"
                    , Html.Events.onClick (ChangeConfig <| ChangeAnalogInputs AddAnalogInput)
                    ]
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
                    [ Html.Attributes.class "pluginInternalButton"
                    , Html.Events.onClick (ChangeConfig <| ChangeAnalogInputs << DeleteAnalogInput <| num)
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


calculateTime : String -> String -> Float
calculateTime numberSamples sampleRate =
    let
        samples =
            case String.toFloat numberSamples of
                Err _ ->
                    0.0

                Ok float ->
                    float
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
        [ Html.Attributes.value instrument.config.decimation
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



--------------
-- DEFAULTS --
--------------


default : String -> AlazarInstrument
default name =
    if name == "None" then
        { name = name
        , priority = "100"
        , config = defaultConfig
        , active = False
        , progress = Nothing
        }
    else
        { name = name
        , priority = "100"
        , config = defaultConfig
        , active = True
        , progress = Nothing
        }


defaultConfig : Config
defaultConfig =
    { clock_source = "INTERNAL_CLOCK"
    , sample_rate = "SAMPLE_RATE_10MSPS"
    , clock_edge = "CLOCK_EDGE_RISING"
    , decimation = "0"
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
    , pre_trigger_samples = "0"
    , post_trigger_samples = "1024"
    , records = "1"
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
            , ( "priority", Json.Encode.int <| intDefault (.priority (default "None")) instrument.priority )
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
        , ( "decimation", Json.Encode.int <| intDefault defaultConfig.decimation config.decimation )
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
        , ( "pre_trigger_samples", Json.Encode.int <| intDefault defaultConfig.pre_trigger_samples config.pre_trigger_samples )
        , ( "post_trigger_samples", Json.Encode.int <| intDefault defaultConfig.post_trigger_samples config.post_trigger_samples )
        , ( "records", Json.Encode.int <| intDefault defaultConfig.records config.records )
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
