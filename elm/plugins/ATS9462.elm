port module ATS9462 exposing (main)

import AlazarTech exposing (..)
import Json.Encode as E
import Metadata exposing (Metadata)


common : Metadata
common =
    { title = "AlazarTech ATS 9462"
    , authors = [ "Paul Freeman" ]
    , maintainer = "Jonathan Simpson"
    , email = "jsim921@aucklanduni.ac.nz"
    , url = "https://github.com/palab/place"
    , elm =
        { moduleName = "ATS9462"
        }
    , python =
        { moduleName = "alazartech"
        , className = "ATS9462"
        }
    , defaultPriority = "100"
    }


default : AlazarInstrument
default =
    { active = False
    , priority = common.defaultPriority
    , metadata = common
    , config = defaultConfig
    , progress = E.null
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


options : Options
options =
    { sampleRateOptions =
        sampleRateOptions
            [ ( "SAMPLE_RATE_1KSPS", "1K" )
            , ( "SAMPLE_RATE_2KSPS", "2K" )
            , ( "SAMPLE_RATE_5KSPS", "5K" )
            , ( "SAMPLE_RATE_10KSPS", "10K" )
            , ( "SAMPLE_RATE_20KSPS", "20K" )
            , ( "SAMPLE_RATE_50KSPS", "50K" )
            , ( "SAMPLE_RATE_100KSPS", "100K" )
            , ( "SAMPLE_RATE_200KSPS", "200K" )
            , ( "SAMPLE_RATE_500KSPS", "500K" )
            , ( "SAMPLE_RATE_1MSPS", "1M" )
            , ( "SAMPLE_RATE_2MSPS", "2M" )
            , ( "SAMPLE_RATE_5MSPS", "5M" )
            , ( "SAMPLE_RATE_10MSPS", "10M" )
            , ( "SAMPLE_RATE_20MSPS", "20M" )
            , ( "SAMPLE_RATE_50MSPS", "50M" )
            , ( "SAMPLE_RATE_100MSPS", "100M" )
            , ( "SAMPLE_RATE_125MSPS", "125M" )
            , ( "SAMPLE_RATE_160MSPS", "160M" )
            , ( "SAMPLE_RATE_180MSPS", "180M" )
            , ( "SAMPLE_RATE_USER_DEF", "user-defined" )
            ]
    , clockSourceOptions =
        clockSourceOptions
            [ ( "INTERNAL_CLOCK", "Internal Clock" )
            , ( "FAST_EXTERNAL_CLOCK", "External Clock (fast)" )
            , ( "SLOW_EXTERNAL_CLOCK", "External Clock (slow)" )
            , ( "EXTERNAL_CLOCK_10_MHZ_REF", "External Clock (10MHz)" )
            ]
    , clockEdgeOptions =
        clockEdgeOptions
            [ ( "CLOCK_EDGE_RISING", "rising edge" )
            , ( "CLOCK_EDGE_FALLING", "falling edge" )
            ]
    , channelOptions =
        channelOptions
            [ ( "CHANNEL_A", "channel A" )
            , ( "CHANNEL_B", "channel B" )
            ]
    , inputChannelOptions =
        inputChannelOptions
            [ ( "AC_COUPLING", "AC coupling" )
            , ( "DC_COUPLING", "DC coupling" )
            ]
    , inputRangeOptions =
        inputRangeOptions
            [ ( "200mv-50ohm", "+/- 200 mV, 50 ohm" )
            , ( "400mv-50ohm", "+/- 400 mV, 50 ohm" )
            , ( "800mv-50ohm", "+/- 800 mV, 50 ohm" )
            , ( "2v-50ohm", "+/- 2 V, 50 ohm" )
            , ( "4v-50ohm", "+/- 4 V, 50 ohm" )
            , ( "8v-50ohm", "+/- 8 V, 50 ohm" )
            , ( "16v-50ohm", "+/- 16 V, 50 ohm" )
            , ( "200mv-1Mohm", "+/- 200 mV, 1 Mohm" )
            , ( "400mv-1Mohm", "+/- 400 mV, 1 Mohm" )
            , ( "800mv-1Mohm", "+/- 800 mV, 1 Mohm" )
            , ( "2v-1Mohm", "+/- 2 V, 1 Mohm" )
            , ( "4v-1Mohm", "+/- 4 V, 1 Mohm" )
            , ( "8v-1Mohm", "+/- 8 V, 1 Mohm" )
            , ( "16v-1Mohm", "+/- 16 V, 1 Mohm" )
            ]
    , triggerOperationOptions =
        triggerOperationOptions
            [ ( "TRIG_ENGINE_OP_J", "Trigger J goes low to high" )
            , ( "TRIG_ENGINE_OP_K", "Trigger K goes low to high" )
            , ( "TRIG_ENGINE_OP_J_OR_K", "(J OR K) goes low to high" )
            , ( "TRIG_ENGINE_OP_J_AND_K", "(J AND K) goes low to high" )
            , ( "TRIG_ENGINE_OP_J_XOR_K", "(J XOR K) goes low to high" )
            , ( "TRIG_ENGINE_OP_J_AND_NOT_K", "(J AND (NOT K)) goes low to high" )
            , ( "TRIG_ENGINE_OP_NOT_J_AND_K", "((NOT J) AND K) goes low to high" )
            ]
    , triggerEngineOptions =
        triggerEngineOptions
            [ ( "TRIG_ENGINE_J", "Trigger engine J" )
            , ( "TRIG_ENGINE_K", "Trigger engine K" )
            ]
    , triggerChannelOptions =
        triggerChannelOptions
            [ ( "TRIG_CHAN_A", "channel A" )
            , ( "TRIG_CHAN_B", "channel B" )
            , ( "TRIG_EXTERNAL", "external trigger" )
            , ( "TRIG_DISABLE", "disabled" )
            , ( "TRIG_FORCE", "instant trigger" )
            ]
    , triggerSlopeOptions =
        triggerSlopeOptions
            [ ( "TRIGGER_SLOPE_POSITIVE", "Positive trigger" )
            , ( "TRIGGER_SLOPE_NEGATIVE", "Negative trigger" )
            ]
    }


main : Program Never AlazarInstrument Msg
main =
    commonMain options default
