module Alazartech exposing (..)

{-| The Alazartech view for PLACE
-}

import Html exposing (..)
import Html.Events exposing (onInput)
import Html.Attributes exposing (selected, value)
import Json.Encode exposing (encode)


{-| main
-}
main : Program Never Instrument Msg
main =
    Html.beginnerProgram
        { model = default
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
    | ChangeDecimation Int


update : Msg -> Instrument -> Instrument
update msg instrument =
    case msg of
        ChangeName newValue ->
            ({ instrument | name = newValue })

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
            ({ config | decimation = newValue })


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
            ++ optionView instrument
            ++ [ br [] []
               , br [] []
               , text (encode 4 instrument)
               ]


{-| options view
-}
optionView : Instrument -> List (Html Msg)
optionView instrument =
    if instrument.name == "None" then
        []
    else
        [ h3 [] [ text (instrument.name ++ " configuration") ]
        , h4 [] [ text "Clock configuration" ]
        ]
            ++ [ text "Clock source: "
               , selectClockSource instrument
               , br [] []
               ]
            ++ [ text "Sample rate: "
               , selectSampleRate instrument
               , text " samples/second"
               , br [] []
               ]
            ++ [ text "Clock edge: "
               , selectClockEdge instrument
               , br [] []
               ]
            ++ [ text "Decimation: "
               , inputDecimation instrument
               , br [] []
               ]


{-| clock source select menu
-}
selectClockSource : Instrument -> Html Msg
selectClockSource instrument =
    case instrument.name of
        "ATS660" ->
            select [ onInput (ChangeConfig << ChangeClockSource) ]
                [ option
                    [ value "INTERNAL_CLOCK"
                    , selected (instrument.config.clock_source == "INTERNAL_CLOCK")
                    ]
                    [ text "Internal Clock" ]
                , option
                    [ value "SLOW_EXTERNAL_CLOCK"
                    , selected (instrument.config.clock_source == "SLOW_EXTERNAL_CLOCK")
                    ]
                    [ text "External Clock (slow)" ]
                , option
                    [ value "EXTERNAL_CLOCK_AC"
                    , selected (instrument.config.clock_source == "EXTERNAL_CLOCK_AC")
                    ]
                    [ text "External Clock (AC)" ]
                , option
                    [ value "EXTERNAL_CLOCK_DC"
                    , selected (instrument.config.clock_source == "EXTERNAL_CLOCK_DC")
                    ]
                    [ text "External Clock (DC)" ]
                , option
                    [ value "EXTERNAL_CLOCK_10_MHZ_REF"
                    , selected (instrument.config.clock_source == "EXTERNAL_CLOCK_10_MHZ_REF")
                    ]
                    [ text "External Clock (10MHz)" ]
                ]

        "ATS9440" ->
            select [ onInput (ChangeConfig << ChangeClockSource) ]
                [ option
                    [ value "INTERNAL_CLOCK"
                    , selected (instrument.config.clock_source == "INTERNAL_CLOCK")
                    ]
                    [ text "Internal Clock" ]
                , option
                    [ value "FAST_EXTERNAL_CLOCK"
                    , selected (instrument.config.clock_source == "FAST_EXTERNAL_CLOCK")
                    ]
                    [ text "External Clock (fast)" ]
                , option
                    [ value "SLOW_EXTERNAL_CLOCK"
                    , selected (instrument.config.clock_source == "SLOW_EXTERNAL_CLOCK")
                    ]
                    [ text "External Clock (slow)" ]
                , option
                    [ value "EXTERNAL_CLOCK_10_MHZ_REF"
                    , selected (instrument.config.clock_source == "EXTERNAL_CLOCK_10_MHZ_REF")
                    ]
                    [ text "External Clock (10MHz)" ]
                ]

        otherwise ->
            select [] []


selectSampleRate : Instrument -> Html Msg
selectSampleRate instrument =
    case instrument.name of
        "ATS660" ->
            select [ onInput (ChangeConfig << ChangeSampleRate) ]
                [ option
                    [ value "SAMPLE_RATE_1KSPS"
                    , selected (instrument.config.sample_rate == "SAMPLE_RATE_1KSPS")
                    ]
                    [ text "1K" ]
                , option
                    [ value "SAMPLE_RATE_2KSPS"
                    , selected (instrument.config.sample_rate == "SAMPLE_RATE_2KSPS")
                    ]
                    [ text "2K" ]
                , option
                    [ value "SAMPLE_RATE_5KSPS"
                    , selected (instrument.config.sample_rate == "SAMPLE_RATE_5KSPS")
                    ]
                    [ text "5K" ]
                , option
                    [ value "SAMPLE_RATE_10KSPS"
                    , selected (instrument.config.sample_rate == "SAMPLE_RATE_10KSPS")
                    ]
                    [ text "10K" ]
                , option
                    [ value "SAMPLE_RATE_20KSPS"
                    , selected (instrument.config.sample_rate == "SAMPLE_RATE_20KSPS")
                    ]
                    [ text "20K" ]
                , option
                    [ value "SAMPLE_RATE_50KSPS"
                    , selected (instrument.config.sample_rate == "SAMPLE_RATE_50KSPS")
                    ]
                    [ text "50K" ]
                , option
                    [ value "SAMPLE_RATE_100KSPS"
                    , selected (instrument.config.sample_rate == "SAMPLE_RATE_100KSPS")
                    ]
                    [ text "100K" ]
                , option
                    [ value "SAMPLE_RATE_200KSPS"
                    , selected (instrument.config.sample_rate == "SAMPLE_RATE_200KSPS")
                    ]
                    [ text "200K" ]
                , option
                    [ value "SAMPLE_RATE_500KSPS"
                    , selected (instrument.config.sample_rate == "SAMPLE_RATE_500KSPS")
                    ]
                    [ text "500K" ]
                , option
                    [ value "SAMPLE_RATE_1MSPS"
                    , selected (instrument.config.sample_rate == "SAMPLE_RATE_1MSPS")
                    ]
                    [ text "1M" ]
                , option
                    [ value "SAMPLE_RATE_2MSPS"
                    , selected (instrument.config.sample_rate == "SAMPLE_RATE_2MSPS")
                    ]
                    [ text "2M" ]
                , option
                    [ value "SAMPLE_RATE_5MSPS"
                    , selected (instrument.config.sample_rate == "SAMPLE_RATE_5MSPS")
                    ]
                    [ text "5M" ]
                , option
                    [ value "SAMPLE_RATE_10MSPS"
                    , selected (instrument.config.sample_rate == "SAMPLE_RATE_10MSPS")
                    ]
                    [ text "10M" ]
                , option
                    [ value "SAMPLE_RATE_20MSPS"
                    , selected (instrument.config.sample_rate == "SAMPLE_RATE_20MSPS")
                    ]
                    [ text "20M" ]
                , option
                    [ value "SAMPLE_RATE_50MSPS"
                    , selected (instrument.config.sample_rate == "SAMPLE_RATE_50MSPS")
                    ]
                    [ text "50M" ]
                , option
                    [ value "SAMPLE_RATE_100MSPS"
                    , selected (instrument.config.sample_rate == "SAMPLE_RATE_100MSPS")
                    ]
                    [ text "100M" ]
                , option
                    [ value "SAMPLE_RATE_125MSPS"
                    , selected (instrument.config.sample_rate == "SAMPLE_RATE_125MSPS")
                    ]
                    [ text "125M" ]
                , option
                    [ value "SAMPLE_RATE_USER_DEF"
                    , selected (instrument.config.sample_rate == "SAMPLE_RATE_USER_DEF")
                    ]
                    [ text "user-defined" ]
                ]

        "ATS9440" ->
            select [ onInput (ChangeConfig << ChangeSampleRate) ]
                [ option
                    [ value "SAMPLE_RATE_1KSPS"
                    , selected (instrument.config.sample_rate == "SAMPLE_RATE_1KSPS")
                    ]
                    [ text "1K" ]
                , option
                    [ value "SAMPLE_RATE_2KSPS"
                    , selected (instrument.config.sample_rate == "SAMPLE_RATE_2KSPS")
                    ]
                    [ text "2K" ]
                , option
                    [ value "SAMPLE_RATE_5KSPS"
                    , selected (instrument.config.sample_rate == "SAMPLE_RATE_5KSPS")
                    ]
                    [ text "5K" ]
                , option
                    [ value "SAMPLE_RATE_10KSPS"
                    , selected (instrument.config.sample_rate == "SAMPLE_RATE_10KSPS")
                    ]
                    [ text "10K" ]
                , option
                    [ value "SAMPLE_RATE_20KSPS"
                    , selected (instrument.config.sample_rate == "SAMPLE_RATE_20KSPS")
                    ]
                    [ text "20K" ]
                , option
                    [ value "SAMPLE_RATE_50KSPS"
                    , selected (instrument.config.sample_rate == "SAMPLE_RATE_50KSPS")
                    ]
                    [ text "50K" ]
                , option
                    [ value "SAMPLE_RATE_100KSPS"
                    , selected (instrument.config.sample_rate == "SAMPLE_RATE_100KSPS")
                    ]
                    [ text "100K" ]
                , option
                    [ value "SAMPLE_RATE_200KSPS"
                    , selected (instrument.config.sample_rate == "SAMPLE_RATE_200KSPS")
                    ]
                    [ text "200K" ]
                , option
                    [ value "SAMPLE_RATE_500KSPS"
                    , selected (instrument.config.sample_rate == "SAMPLE_RATE_500KSPS")
                    ]
                    [ text "500K" ]
                , option
                    [ value "SAMPLE_RATE_1MSPS"
                    , selected (instrument.config.sample_rate == "SAMPLE_RATE_1MSPS")
                    ]
                    [ text "1M" ]
                , option
                    [ value "SAMPLE_RATE_2MSPS"
                    , selected (instrument.config.sample_rate == "SAMPLE_RATE_2MSPS")
                    ]
                    [ text "2M" ]
                , option
                    [ value "SAMPLE_RATE_5MSPS"
                    , selected (instrument.config.sample_rate == "SAMPLE_RATE_5MSPS")
                    ]
                    [ text "5M" ]
                , option
                    [ value "SAMPLE_RATE_10MSPS"
                    , selected (instrument.config.sample_rate == "SAMPLE_RATE_10MSPS")
                    ]
                    [ text "10M" ]
                , option
                    [ value "SAMPLE_RATE_20MSPS"
                    , selected (instrument.config.sample_rate == "SAMPLE_RATE_20MSPS")
                    ]
                    [ text "20M" ]
                , option
                    [ value "SAMPLE_RATE_50MSPS"
                    , selected (instrument.config.sample_rate == "SAMPLE_RATE_50MSPS")
                    ]
                    [ text "50M" ]
                , option
                    [ value "SAMPLE_RATE_100MSPS"
                    , selected (instrument.config.sample_rate == "SAMPLE_RATE_100MSPS")
                    ]
                    [ text "100M" ]
                , option
                    [ value "SAMPLE_RATE_125MSPS"
                    , selected (instrument.config.sample_rate == "SAMPLE_RATE_125MSPS")
                    ]
                    [ text "125M" ]
                , option
                    [ value "SAMPLE_RATE_USER_DEF"
                    , selected (instrument.config.sample_rate == "SAMPLE_RATE_USER_DEF")
                    ]
                    [ text "user-defined" ]
                ]

        otherwise ->
            select [] []


selectClockEdge : Instrument -> Html Msg
selectClockEdge instrument =
    select [ onInput (ChangeConfig << ChangeClockEdge) ]
        [ option
            [ value "CLOCK_EDGE_RISING"
            , selected (instrument.config.clock_edge == "CLOCK_EDGE_RISING")
            ]
            [ text "rising edge" ]
        , option
            [ value "CLOCK_EDGE_FALLING"
            , selected (instrument.config.clock_edge == "CLOCK_EDGE_FALLING")
            ]
            [ text "falling edge" ]
        ]


inputDecimation : Instrument -> Html Msg
inputDecimation instrument =
    input [ onInput (ChangeConfig << ChangeDecimation) ] []


default : Instrument
default =
    { name = "None"
    , config =
        { clock_source = "INTERNAL_CLOCK"
        , sample_rate = "SAMPLE_RATE_10MSPS"
        , clock_edge = "CLOCK_EDGE_RISING"
        , decimation = 0
        , analog_inputs = []
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
    }
