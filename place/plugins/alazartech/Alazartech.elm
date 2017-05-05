module Alazartech exposing (..)

{-| The Alazartech view for PLACE
-}

import Html exposing (..)
import Html.Events exposing (onInput, onClick)
import Html.Attributes exposing (selected, value)
import Json.Encode exposing (..)


{-| main
-}
main : Program Never Instrument Msg
main =
    Html.beginnerProgram
        { model = default "None"
        , view = mainView
        , update = update
        }


{-| The model contains all the options needed by the Alazar card.
-}
type alias Instrument =
    { name : String
    , config : Config
    }


{-| The AlazarConfig type contains all the config options/
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
    }


{-| AnalogInput
-}
type alias AnalogInput =
    { input_channel : String
    , input_coupling : String
    , input_range : String
    , input_impedance : String
    }


{-| Messages
-}
type Msg
    = ChangeName String
    | ChangeConfig ConfigMsg


type ConfigMsg
    = ChangeClockSource String
    | ChangeSampleRate String
    | ChangeClockEdge String
    | ChangeDecimation String
    | ChangeAnalogInputs AnalogInputsMsg


type AnalogInputsMsg
    = AddAnalogInput
    | DeleteAnalogInput Int
    | ChangeInputChannel Int String
    | ChangeInputRange Int String
    | ChangeInputCoupling Int String
    | ChangeInputImpedance Int String


update : Msg -> Instrument -> Instrument
update msg instrument =
    case msg of
        ChangeName newValue ->
            default newValue

        ChangeConfig configMsg ->
            ({ instrument | config = updateConfig configMsg instrument.config })


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
            ({ config | analog_inputs = updateAnalogInputs analogInputsMsg config.analog_inputs })


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


{-| Test view
-}
mainView : Instrument -> Html Msg
mainView instrument =
    div [] <|
        [ h2 [] [ text "Alazartech Instrument" ]
        , select [ onInput ChangeName ]
            [ option [ value "None", selected (instrument.name == "None") ] [ text "None" ]
            , option [ value "ATS660", selected (instrument.name == "ATS660") ] [ text "ATS660" ]
            , option [ value "ATS9440", selected (instrument.name == "ATS9440") ] [ text "ATS9440" ]
            ]
        ]
            ++ configView instrument
            ++ [ h3 [] [ text "JSON text" ]
               , pre [] [ text (encode 4 (toJson instrument)) ]
               ]


{-| options view
-}
configView : Instrument -> List (Html Msg)
configView instrument =
    if instrument.name == "None" then
        []
    else
        [ h3 [] [ text (instrument.name ++ " configuration") ] ]
            ++ [ h4 [] [ text "Clock configuration" ]
               , text "Clock source: "
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
            ++ analogInputsView instrument


analogInputsView : Instrument -> List (Html Msg)
analogInputsView instrument =
    let
        channelsMax =
            List.length (channelOptions instrument.name "")

        channels =
            List.length instrument.config.analog_inputs
    in
        h4 [] [ text "Analog inputs" ]
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


analogInputView : Instrument -> Int -> AnalogInput -> List (Html Msg)
analogInputView instrument num analogInput =
    h5 [] [ text ("Channel " ++ toString num ++ " configuration") ]
        :: [ text "Input channel: "
           , selectInputChannel instrument analogInput num
           , br [] []
           , text "Input coupling: "
           , selectInputCoupling analogInput.input_coupling num
           , br [] []
           , text "Input range: "
           , selectInputRange instrument.name analogInput.input_range num
           , br [] []
           , text "Input impedance: "
           , selectInputImpedance instrument.name analogInput.input_impedance num
           , br [] []
           , button
                [ onClick (ChangeConfig <| ChangeAnalogInputs << DeleteAnalogInput <| num) ]
                [ text "Delete input" ]
           ]


{-| clock source select menu
-}
selectClockSource : Instrument -> Html Msg
selectClockSource instrument =
    let
        val =
            instrument.config.clock_source
    in
        case instrument.name of
            "ATS660" ->
                select [ onInput (ChangeConfig << ChangeClockSource) ]
                    [ anOption val "INTERNAL_CLOCK" "Internal Clock"
                    , anOption val "SLOW_EXTERNAL_CLOCK" "External Clock (slow)"
                    , anOption val "EXTERNAL_CLOCK_AC" "External Clock (AC)"
                    , anOption val "EXTERNAL_CLOCK_DC" "External Clock (DC)"
                    , anOption val "EXTERNAL_CLOCK_10_MHZ_REF" "External Clock (10MHz)"
                    ]

            "ATS9440" ->
                select [ onInput (ChangeConfig << ChangeClockSource) ]
                    [ anOption val "INTERNAL_CLOCK" "Internal Clock"
                    , anOption val "FAST_EXTERNAL_CLOCK" "External Clock (fast)"
                    , anOption val "SLOW_EXTERNAL_CLOCK" "External Clock (slow)"
                    , anOption val "EXTERNAL_CLOCK_10_MHZ_REF" "External Clock (10MHz)"
                    ]

            otherwise ->
                select [] []


anOption : String -> String -> String -> Html Msg
anOption str val disp =
    option [ value val, selected (str == val) ] [ text disp ]


selectSampleRate : Instrument -> Html Msg
selectSampleRate instrument =
    let
        val =
            instrument.config.sample_rate
    in
        case instrument.name of
            "ATS660" ->
                select [ onInput (ChangeConfig << ChangeSampleRate) ]
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
                select [ onInput (ChangeConfig << ChangeSampleRate) ]
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
                select [] []


selectClockEdge : Instrument -> Html Msg
selectClockEdge instrument =
    select [ onInput (ChangeConfig << ChangeClockEdge) ]
        [ anOption instrument.config.clock_edge "CLOCK_EDGE_RISING" "rising edge"
        , anOption instrument.config.clock_edge "CLOCK_EDGE_FALLING" "falling edge"
        ]


inputDecimation : Instrument -> Html Msg
inputDecimation instrument =
    input [ onInput (ChangeConfig << ChangeDecimation) ] []


selectInputChannel : Instrument -> AnalogInput -> Int -> Html Msg
selectInputChannel instrument analogInput num =
    select
        [ onInput (ChangeConfig << ChangeAnalogInputs << (ChangeInputChannel num)) ]
        (channelOptions instrument.name analogInput.input_channel)


channelOptions : String -> String -> List (Html Msg)
channelOptions name channel =
    case name of
        "ATS660" ->
            [ anOption channel "CHANNEL_A" "channel A"
            , anOption channel "CHANNEL_B" "channel B"
            ]

        "ATS9440" ->
            [ anOption channel "CHANNEL_A" "channel A"
            , anOption channel "CHANNEL_B" "channel B"
            , anOption channel "CHANNEL_C" "channel C"
            , anOption channel "CHANNEL_D" "channel D"
            ]

        otherwise ->
            []


selectInputCoupling : String -> Int -> Html Msg
selectInputCoupling currentCoupling num =
    select
        [ onInput (ChangeConfig << ChangeAnalogInputs << (ChangeInputCoupling num)) ]
        [ anOption currentCoupling "AC_COUPLING" "AC coupling"
        , anOption currentCoupling "DC_COUPLING" "DC coupling"
        ]


selectInputRange : String -> String -> Int -> Html Msg
selectInputRange name currentRange num =
    select
        [ onInput (ChangeConfig << ChangeAnalogInputs << (ChangeInputRange num)) ]
        (inputRangeOptions name currentRange)


inputRangeOptions : String -> String -> List (Html Msg)
inputRangeOptions name currentRange =
    case name of
        "ATS660" ->
            [ anOption currentRange "INPUT_RANGE_PM_200_MV" "+/- 200mV"
            , anOption currentRange "INPUT_RANGE_PM_400_MV" "+/- 400mV"
            , anOption currentRange "INPUT_RANGE_PM_800_MV" "+/- 800mV"
            , anOption currentRange "INPUT_RANGE_PM_2_V" "+/- 2V"
            , anOption currentRange "INPUT_RANGE_PM_4_V" "+/- 4V"
            , anOption currentRange "INPUT_RANGE_PM_8_V" "+/- 8V"
            , anOption currentRange "INPUT_RANGE_PM_16_V" "+/- 16V"
            ]

        "ATS9440" ->
            [ anOption currentRange "INPUT_RANGE_PM_100_MV" "+/- 100mV"
            , anOption currentRange "INPUT_RANGE_PM_200_MV" "+/- 200mV"
            , anOption currentRange "INPUT_RANGE_PM_400_MV" "+/- 400mV"
            , anOption currentRange "INPUT_RANGE_PM_1_V" "+/- 1V"
            , anOption currentRange "INPUT_RANGE_PM_2_V" "+/- 2V"
            , anOption currentRange "INPUT_RANGE_PM_4_V" "+/- 4V"
            ]

        otherwise ->
            []


selectInputImpedance : String -> String -> Int -> Html Msg
selectInputImpedance name currentImpedance num =
    case name of
        "ATS660" ->
            select
                [ onInput (ChangeConfig << ChangeAnalogInputs << (ChangeInputImpedance num)) ]
                [ anOption currentImpedance "IMPEDANCE_50_OHM" "50 Ohm"
                , anOption currentImpedance "IMPEDANCE_1M_OHM" "1 MOhm"
                ]

        "ATS9440" ->
            text "50 Ohm"

        otherwise ->
            text ""


default : String -> Instrument
default name =
    { name = name
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
    , post_trigger_samples = 256
    }


defaultAnalogInput : AnalogInput
defaultAnalogInput =
    { input_channel = "CHANNEL_A"
    , input_coupling = "DC_COUPLING"
    , input_range = "INPUT_RANGE_PM_800_MV"
    , input_impedance = "IMPEDANCE_50_OHM"
    }


toJson : Instrument -> Value
toJson instrument =
    Json.Encode.object
        [ ( "name", string instrument.name )
        , ( "config", configToJson instrument.config )
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
