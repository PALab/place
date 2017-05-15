port module AlazarTech exposing (view, AlazarInstrument, Config, AnalogInput)

{-| The AlazarTech web interface for PLACE.


# Main HTML View

@docs view


# Underlying Structure

@docs AlazarInstrument, Config, AnalogInput

-}

import Html exposing (..)
import Html.Events exposing (onInput, onClick)
import Html.Attributes exposing (selected, value, defaultValue)
import Json.Encode exposing (..)
import Result exposing (withDefault)


main =
    Html.program
        { init = ( default "None", Cmd.none )
        , view = view
        , update = update
        , subscriptions = subscriptions
        }



--------------------
-- MAIN HTML VIEW --
--------------------


{-| Presents the configuration data for an `AlazarInstrument` as an HTML `div`
element. The HTML includes interactive components needed to modify the
configuration if needed.

The full HTML is broken down into a hierarchical structure. Please see the
sub-functions for more details.

-}
view : AlazarInstrument -> Html Msg
view instrument =
    div [] <|
        h2 [] [ text "Alazartech Instrument" ]
            :: nameView instrument
            ++ configView instrument


subscriptions : AlazarInstrument -> Sub Msg
subscriptions instrument =
    requestJson SendJson



------------------
-- DATA RECORDS --
------------------


{-| All PLACE configurations must contain a "name" string and a "config"
record. Specific values within "config" are not used by PLACE.

The "name" should match the name of the Python Class written for the
instrument.

The "priority" value is the order in which the Scan will update the
instruments. Lowest values will have the update method called before higher
values.

-}
type alias AlazarInstrument =
    { name : String
    , priority : Int
    , config : Config
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
    , trigger_level_1 : Int
    , trigger_engine_2 : String
    , trigger_source_2 : String
    , trigger_slope_2 : String
    , trigger_level_2 : Int
    , pre_trigger_samples : Int
    , post_trigger_samples : Int
    , averages : Int
    , plot : String
    }


{-| There can be zero to many analog inputs, so we represent these as a list.

This type represents one analog input and can be configured individually.

-}
type alias AnalogInput =
    { input_channel : String
    , input_coupling : String
    , input_range : String
    , input_impedance : String
    }



--------------
-- MESSAGES --
--------------


{-| There are only two messages for changing the instrument. Either the name
changes, or the configuration changes.
-}
type Msg
    = ChangeName String
    | ChangePriority String
    | ChangeConfig ConfigMsg
    | SendJson String


{-| The update method is called by the web interface whenever something is changed.

If the instrument name is changed, the config is reset to the defaults for the
new instrument. If a configuration is changed, that change comes with a new
message that is used to indicate the config change desired.

-}
update : Msg -> AlazarInstrument -> ( AlazarInstrument, Cmd Msg )
update msg instrument =
    case msg of
        ChangeName newInstrument ->
            ( default newInstrument
            , Cmd.none
            )

        ChangePriority newValue ->
            ( { instrument | priority = withDefault 100 (String.toInt newValue) }
            , Cmd.none
            )

        ChangeConfig configMsg ->
            ( { instrument | config = updateConfig configMsg instrument.config }
            , Cmd.none
            )

        SendJson str ->
            ( instrument, jsonData <| toJson instrument )


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
    | ChangeAverages String
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
            ({ config | decimation = withDefault 0 (String.toInt newValue) })

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
            ({ config | trigger_level_1 = clampWithDefault 128 0 256 newValue })

        ChangeTriggerLevel2 newValue ->
            ({ config | trigger_level_2 = clampWithDefault 128 0 256 newValue })

        ChangePreTriggerSamples newValue ->
            ({ config | pre_trigger_samples = withDefault 0 <| String.toInt newValue })

        ChangePostTriggerSamples newValue ->
            ({ config | post_trigger_samples = withDefault 256 <| String.toInt newValue })

        ChangeAverages newValue ->
            ({ config | averages = clampWithDefault 1 1 1000 newValue })

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
    | ChangeInputImpedance Int String


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

        ChangeInputImpedance n newValue ->
            let
                change =
                    List.head ((List.drop (n - 1)) analog_inputs)
            in
                case change of
                    Nothing ->
                        analog_inputs

                    Just changeMe ->
                        List.take (n - 1) analog_inputs
                            ++ [ { changeMe | input_impedance = newValue } ]
                            ++ List.drop n analog_inputs



---------------
-- HTML DATA --
---------------


nameView : AlazarInstrument -> List (Html Msg)
nameView instrument =
    h3 [] [ text "Alazar instrument selection" ]
        :: [ text "Name: "
           , select [ onInput ChangeName ]
                [ anOption instrument.name "None" "None"
                , anOption instrument.name "ATS660" "ATS660"
                , anOption instrument.name "ATS9440" "ATS9440"
                ]
           , br [] []
           , text "Priority: "
           , inputPriority instrument
           ]


configView : AlazarInstrument -> List (Html Msg)
configView instrument =
    if instrument.name == "None" then
        []
    else
        h3 [] [ text (instrument.name ++ " configuration") ]
            :: timebaseView instrument
            ++ analogInputsView instrument
            ++ triggerControlView instrument
            ++ singlePortView instrument


timebaseView : AlazarInstrument -> List (Html Msg)
timebaseView instrument =
    h4 [] [ text "Clock configuration" ]
        :: [ text "Clock source: "
           , selectClockSource instrument
           , br [] []
           , text "Sample rate: "
           , selectSampleRate instrument
           , text " samples/second"
           , br [] []
           , text "Clock edge: "
           , selectClockEdge instrument
           , br [] []
           , text "Decimation: "
           , inputDecimation instrument
           , br [] []
           ]


analogInputsView : AlazarInstrument -> List (Html Msg)
analogInputsView instrument =
    let
        channelsMax =
            List.length (channelOptions instrument.name "")

        channels =
            List.length instrument.config.analog_inputs
    in
        h4 [] [ text "Input control" ]
            :: (if channels < channelsMax then
                    [ button
                        [ onClick (ChangeConfig <| ChangeAnalogInputs AddAnalogInput) ]
                        [ text "Add input" ]
                    ]
                else
                    []
               )
            ++ (if channels /= 0 then
                    List.concat
                        (List.map2
                            (analogInputView instrument)
                            (List.range 1 32)
                            instrument.config.analog_inputs
                        )
                else
                    []
               )


analogInputView : AlazarInstrument -> Int -> AnalogInput -> List (Html Msg)
analogInputView instrument num analogInput =
    h5 [] [ text ("Channel " ++ toString num ++ " configuration") ]
        :: [ text "Input channel: "
           , selectInputChannel instrument analogInput num
           , br [] []
           , text "Input coupling: "
           , selectInputCoupling analogInput num
           , br [] []
           , text "Input range: "
           , selectInputRange instrument analogInput num
           , br [] []
           , text "Input impedance: "
           , selectInputImpedance instrument analogInput num
           , br [] []
           , button
                [ onClick (ChangeConfig <| ChangeAnalogInputs << DeleteAnalogInput <| num) ]
                [ text "Delete input" ]
           ]


triggerControlView : AlazarInstrument -> List (Html Msg)
triggerControlView instrument =
    h4 [] [ text "Trigger control" ]
        :: [ text "Trigger operation: "
           , selectTriggerOperation instrument
           ]
        ++ [ h5 [] [ text "Trigger 1" ]
           , text "Trigger engine: "
           , selectTriggerEngine1 instrument
           , br [] []
           , text "Trigger source: "
           , selectTriggerSource1 instrument
           ]
        ++ (if instrument.config.trigger_source_1 == "TRIG_DISABLE" then
                []
            else if instrument.config.trigger_source_1 == "TRIG_FORCE" then
                []
            else
                [ br [] []
                , text "Trigger slope: "
                , selectTriggerSlope1 instrument
                , br [] []
                , text "Trigger level: "
                , inputTriggerLevel1 instrument
                ]
           )
        ++ [ h5 [] [ text "Trigger 2" ]
           , text "Trigger engine: "
           , selectTriggerEngine2 instrument
           , br [] []
           , text "Trigger source: "
           , selectTriggerSource2 instrument
           ]
        ++ (if instrument.config.trigger_source_2 == "TRIG_DISABLE" then
                []
            else if instrument.config.trigger_source_1 == "TRIG_FORCE" then
                []
            else
                [ br [] []
                , text "Trigger slope: "
                , selectTriggerSlope2 instrument
                , br [] []
                , text "Trigger level: "
                , inputTriggerLevel2 instrument
                ]
           )


singlePortView : AlazarInstrument -> List (Html Msg)
singlePortView instrument =
    h4 [] [ text "Single port acquisition" ]
        :: [ text "Pre-trigger samples: "
           , inputPreTriggerSamples
           , br [] []
           , text "Post-trigger samples: "
           , inputPostTriggerSamples
           , br [] []
           , text "Averages: "
           , inputAverages
           , br [] []
           , text "Plot: "
           , selectPlot instrument
           ]



------------------------
-- SELECTION ELEMENtS --
------------------------


inputPriority : AlazarInstrument -> Html Msg
inputPriority instrument =
    input [ defaultValue "100", onInput ChangePriority ] []


selectTriggerOperation : AlazarInstrument -> Html Msg
selectTriggerOperation instrument =
    let
        val =
            instrument.config.trigger_operation
    in
        select [ onInput (ChangeConfig << ChangeTriggerOperation) ] <|
            triggerOperationOptions val


selectTriggerEngine1 : AlazarInstrument -> Html Msg
selectTriggerEngine1 instrument =
    let
        val =
            instrument.config.trigger_engine_1
    in
        select [ onInput (ChangeConfig << ChangeTriggerEngine1) ] <|
            triggerEngineOptions val


selectTriggerEngine2 : AlazarInstrument -> Html Msg
selectTriggerEngine2 instrument =
    let
        val =
            instrument.config.trigger_engine_2
    in
        select [ onInput (ChangeConfig << ChangeTriggerEngine2) ] <|
            triggerEngineOptions val


selectTriggerSource1 : AlazarInstrument -> Html Msg
selectTriggerSource1 instrument =
    let
        name =
            instrument.name

        val =
            instrument.config.trigger_source_1
    in
        select [ onInput (ChangeConfig << ChangeTriggerSource1) ] <|
            triggerChannelOptions name val


selectTriggerSource2 : AlazarInstrument -> Html Msg
selectTriggerSource2 instrument =
    let
        name =
            instrument.name

        val =
            instrument.config.trigger_source_2
    in
        select [ onInput (ChangeConfig << ChangeTriggerSource2) ] <|
            triggerChannelOptions name val


selectTriggerSlope1 : AlazarInstrument -> Html Msg
selectTriggerSlope1 instrument =
    let
        val =
            instrument.config.trigger_slope_1
    in
        select [ onInput (ChangeConfig << ChangeTriggerSlope1) ] <|
            triggerSlopeOptions val


selectTriggerSlope2 : AlazarInstrument -> Html Msg
selectTriggerSlope2 instrument =
    let
        val =
            instrument.config.trigger_slope_2
    in
        select [ onInput (ChangeConfig << ChangeTriggerSlope2) ] <|
            triggerSlopeOptions val


inputTriggerLevel1 : AlazarInstrument -> Html Msg
inputTriggerLevel1 instrument =
    input [ defaultValue "128", onInput (ChangeConfig << ChangeTriggerLevel1) ] []


inputTriggerLevel2 : AlazarInstrument -> Html Msg
inputTriggerLevel2 instrument =
    input [ defaultValue "128", onInput (ChangeConfig << ChangeTriggerLevel2) ] []


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
        select [ onInput (ChangeConfig << ChangeClockSource) ] <|
            clockSourceOptions name val


selectSampleRate : AlazarInstrument -> Html Msg
selectSampleRate instrument =
    let
        name =
            instrument.name

        val =
            instrument.config.sample_rate
    in
        select [ onInput (ChangeConfig << ChangeSampleRate) ] <|
            sampleRateOptions name val


selectClockEdge : AlazarInstrument -> Html Msg
selectClockEdge instrument =
    let
        val =
            instrument.config.clock_edge
    in
        select [ onInput (ChangeConfig << ChangeClockEdge) ] <|
            clockEdgeOptions val


inputDecimation : AlazarInstrument -> Html Msg
inputDecimation instrument =
    input [ defaultValue "0", onInput (ChangeConfig << ChangeDecimation) ] []


selectInputChannel : AlazarInstrument -> AnalogInput -> Int -> Html Msg
selectInputChannel instrument analogInput num =
    let
        name =
            instrument.name

        val =
            analogInput.input_channel
    in
        select
            [ onInput (ChangeConfig << ChangeAnalogInputs << (ChangeInputChannel num)) ]
        <|
            channelOptions name val


selectInputCoupling : AnalogInput -> Int -> Html Msg
selectInputCoupling input num =
    let
        val =
            input.input_coupling
    in
        select
            [ onInput (ChangeConfig << ChangeAnalogInputs << (ChangeInputCoupling num)) ]
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
        select
            [ onInput (ChangeConfig << ChangeAnalogInputs << (ChangeInputRange num)) ]
        <|
            inputRangeOptions name val


selectInputImpedance : AlazarInstrument -> AnalogInput -> Int -> Html Msg
selectInputImpedance instrument input num =
    let
        name =
            instrument.name

        val =
            input.input_impedance
    in
        select
            [ onInput (ChangeConfig << ChangeAnalogInputs << (ChangeInputImpedance num)) ]
        <|
            inputImpedanceOptions name val


inputPreTriggerSamples : Html Msg
inputPreTriggerSamples =
    input [ defaultValue "0", onInput (ChangeConfig << ChangePreTriggerSamples) ] []


inputPostTriggerSamples : Html Msg
inputPostTriggerSamples =
    input [ defaultValue "1024", onInput (ChangeConfig << ChangePostTriggerSamples) ] []


inputAverages : Html Msg
inputAverages =
    input [ defaultValue "1", onInput (ChangeConfig << ChangeAverages) ] []


selectPlot : AlazarInstrument -> Html Msg
selectPlot instrument =
    let
        val =
            instrument.config.plot
    in
        select [ onInput (ChangeConfig << ChangePlot) ] <|
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
            [ anOption val "INPUT_RANGE_PM_200_MV" "+/- 200mV"
            , anOption val "INPUT_RANGE_PM_400_MV" "+/- 400mV"
            , anOption val "INPUT_RANGE_PM_800_MV" "+/- 800mV"
            , anOption val "INPUT_RANGE_PM_2_V" "+/- 2V"
            , anOption val "INPUT_RANGE_PM_4_V" "+/- 4V"
            , anOption val "INPUT_RANGE_PM_8_V" "+/- 8V"
            , anOption val "INPUT_RANGE_PM_16_V" "+/- 16V"
            ]

        "ATS9440" ->
            [ anOption val "INPUT_RANGE_PM_100_MV" "+/- 100mV"
            , anOption val "INPUT_RANGE_PM_200_MV" "+/- 200mV"
            , anOption val "INPUT_RANGE_PM_400_MV" "+/- 400mV"
            , anOption val "INPUT_RANGE_PM_1_V" "+/- 1V"
            , anOption val "INPUT_RANGE_PM_2_V" "+/- 2V"
            , anOption val "INPUT_RANGE_PM_4_V" "+/- 4V"
            ]

        otherwise ->
            []


inputImpedanceOptions : String -> String -> List (Html Msg)
inputImpedanceOptions name val =
    case name of
        "ATS660" ->
            [ anOption val "IMPEDANCE_50_OHM" "50 Ohm"
            , anOption val "IMPEDANCE_1M_OHM" "1 MOhm"
            ]

        "ATS9440" ->
            [ anOption val "IMPEDANCE_50_OHM" "50 Ohm" ]

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
    { name = name
    , priority = 100
    , config = defaultConfig
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
    , trigger_level_1 = 128
    , trigger_engine_2 = "TRIG_ENGINE_K"
    , trigger_source_2 = "TRIG_DISABLE"
    , trigger_slope_2 = "TRIGGER_SLOPE_POSITIVE"
    , trigger_level_2 = 128
    , pre_trigger_samples = 0
    , post_trigger_samples = 1024
    , averages = 1
    , plot = "no"
    }


defaultAnalogInput : AnalogInput
defaultAnalogInput =
    { input_channel = "CHANNEL_A"
    , input_coupling = "DC_COUPLING"
    , input_range = "INPUT_RANGE_PM_800_MV"
    , input_impedance = "IMPEDANCE_50_OHM"
    }



------------------
-- JSON HELPERS --
------------------


port requestJson : (String -> msg) -> Sub msg


port jsonData : Value -> Cmd msg


toJson : AlazarInstrument -> Value
toJson instrument =
    Json.Encode.list
        [ Json.Encode.object
            [ ( "module_name", string "alazartech" )
            , ( "class_name", string instrument.name )
            , ( "priority", int instrument.priority )
            , ( "config", configToJson instrument.config )
            ]
        ]


configToJson : Config -> Value
configToJson config =
    Json.Encode.object
        [ ( "clock_source", string config.clock_source )
        , ( "sample_rate", string config.sample_rate )
        , ( "clock_edge", string config.clock_edge )
        , ( "decimation", int config.decimation )
        , ( "analog_inputs", analogInputsToJson config.analog_inputs )
        , ( "trigger_operation", string config.trigger_operation )
        , ( "trigger_engine_1", string config.trigger_engine_1 )
        , ( "trigger_source_1", string config.trigger_source_1 )
        , ( "trigger_slope_1", string config.trigger_slope_1 )
        , ( "trigger_level_1", int config.trigger_level_1 )
        , ( "trigger_engine_2", string config.trigger_engine_2 )
        , ( "trigger_source_2", string config.trigger_source_2 )
        , ( "trigger_slope_2", string config.trigger_slope_2 )
        , ( "trigger_level_2", int config.trigger_level_2 )
        , ( "pre_trigger_samples", int config.pre_trigger_samples )
        , ( "post_trigger_samples", int config.post_trigger_samples )
        , ( "averages", int config.averages )
        , ( "plot", string config.plot )
        ]


analogInputsToJson : List AnalogInput -> Value
analogInputsToJson analogInputs =
    list (List.map analogInputToJson analogInputs)


analogInputToJson : AnalogInput -> Value
analogInputToJson analogInput =
    Json.Encode.object
        [ ( "input_channel", string analogInput.input_channel )
        , ( "input_coupling", string analogInput.input_coupling )
        , ( "input_range", string analogInput.input_range )
        , ( "input_impedance", string analogInput.input_impedance )
        ]



-------------------
-- OTHER HELPERS --
-------------------


{-| Helper function to present an option in a drop-down selection box.
-}
anOption : String -> String -> String -> Html Msg
anOption str val disp =
    option [ value val, selected (str == val) ] [ text disp ]


{-| Ensures that a string returns an interger within a given range.
-}
clampWithDefault : Int -> Int -> Int -> String -> Int
clampWithDefault default min max intStr =
    clamp min max <|
        withDefault default <|
            String.toInt intStr
