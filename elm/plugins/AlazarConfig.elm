module AlazarConfig exposing
    ( AnalogInput
    , Instrument
    , Model
    , Msg(ChangePlot)
    , Options
    , channelOptions
    , clockEdgeOptions
    , clockSourceOptions
    , fromJson
    , inputChannelOptions
    , inputRangeOptions
    , sampleRateOptions
    , toJson
    , triggerChannelOptions
    , triggerEngineOptions
    , triggerOperationOptions
    , triggerSlopeOptions
    , update
    , view
    )

import Html exposing (Html)
import Html.Attributes
import Html.Events
import Json.Decode as D
import Json.Decode.Pipeline exposing (hardcoded, required)
import Json.Encode as E
import Metadata exposing (Metadata)
import Plugin exposing (Plugin)
import PluginHelpers exposing (..)


type alias Instrument =
    { active : Bool
    , priority : String
    , metadata : Metadata
    , config : Model
    , progress : E.Value
    }


type alias Model =
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


type alias AnalogInput =
    { input_channel : String
    , input_coupling : String
    , input_range : String
    }


type alias Options =
    { sampleRateOptions : String -> List (Html Msg)
    , clockSourceOptions : List ( String, String )
    , clockEdgeOptions : String -> List (Html Msg)
    , channelOptions : String -> List (Html Msg)
    , inputChannelOptions : String -> List (Html Msg)
    , inputRangeOptions : String -> List (Html Msg)
    , triggerOperationOptions : String -> List (Html Msg)
    , triggerEngineOptions : String -> List (Html Msg)
    , triggerChannelOptions : String -> List (Html Msg)
    , triggerSlopeOptions : String -> List (Html Msg)
    }


type Msg
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


type AnalogInputsMsg
    = AddAnalogInput
    | DeleteAnalogInput Int
    | ChangeInputChannel Int String
    | ChangeInputRange Int String
    | ChangeInputCoupling Int String


update : Model -> Msg -> Model -> Model
update default configMsg config =
    case configMsg of
        ChangeClockSource newValue ->
            { config | clock_source = newValue }

        ChangeSampleRate newValue ->
            { config | sample_rate = newValue }

        ChangeClockEdge newValue ->
            { config | clock_edge = newValue }

        ChangeDecimation newValue ->
            { config | decimation = newValue }

        ChangeAnalogInputs analogInputsMsg ->
            { config
                | analog_inputs =
                    updateAnalogInputs default.analog_inputs analogInputsMsg config.analog_inputs
            }

        ChangeTriggerOperation newValue ->
            { config | trigger_operation = newValue }

        ChangeTriggerEngine1 newValue ->
            { config | trigger_engine_1 = newValue }

        ChangeTriggerEngine2 newValue ->
            { config | trigger_engine_2 = newValue }

        ChangeTriggerSource1 newValue ->
            { config | trigger_source_1 = newValue }

        ChangeTriggerSource2 newValue ->
            { config | trigger_source_2 = newValue }

        ChangeTriggerSlope1 newValue ->
            { config | trigger_slope_1 = newValue }

        ChangeTriggerSlope2 newValue ->
            { config | trigger_slope_2 = newValue }

        ChangeTriggerLevel1 newValue ->
            { config | triggerLevelString1 = newValue }

        ChangeTriggerLevel2 newValue ->
            { config | triggerLevelString2 = newValue }

        ChangePreTriggerSamples newValue ->
            { config | pre_trigger_samples = newValue }

        ChangePostTriggerSamples newValue ->
            { config | post_trigger_samples = newValue }

        ChangeRecords newValue ->
            { config | records = newValue }

        ToggleAverage ->
            { config | average = not config.average }

        ChangePlot newValue ->
            { config | plot = newValue }


updateAnalogInputs : List AnalogInput -> AnalogInputsMsg -> List AnalogInput -> List AnalogInput
updateAnalogInputs default analogInputsMsg analog_inputs =
    case analogInputsMsg of
        AddAnalogInput ->
            List.append analog_inputs default

        DeleteAnalogInput n ->
            List.take (n - 1) analog_inputs ++ List.drop n analog_inputs

        ChangeInputChannel n newValue ->
            let
                change =
                    List.head (List.drop (n - 1) analog_inputs)
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
                    List.head (List.drop (n - 1) analog_inputs)
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
                    List.head (List.drop (n - 1) analog_inputs)
            in
            case change of
                Nothing ->
                    analog_inputs

                Just changeMe ->
                    List.take (n - 1) analog_inputs
                        ++ [ { changeMe | input_coupling = newValue } ]
                        ++ List.drop n analog_inputs


view : Options -> Model -> Html Msg
view options config =
    Html.div [ Html.Attributes.id "alazarConfigView" ]
        [ singlePortView config
        , timebaseView options config
        , analogInputsView options config
        , triggerControlView options config
        ]


singlePortView : Model -> Html Msg
singlePortView config =
    let
        preTime =
            toString (calculateTime config.pre_trigger_samples config.sample_rate)

        postTime =
            toString (calculateTime config.post_trigger_samples config.sample_rate)
    in
    Html.div [ Html.Attributes.id "alazarSinglePortView" ] <|
        [ Html.h4 [] [ Html.text "Single port acquisition" ]
        , integerField "Pre-trigger samples" config.pre_trigger_samples ChangePreTriggerSamples
        , Html.p [] [ Html.text <| "(" ++ preTime ++ " microsecs)" ]
        , integerField "Post-trigger samples" config.post_trigger_samples ChangePostTriggerSamples
        , Html.p [] [ Html.text <| "(" ++ postTime ++ " microsecs)" ]
        , integerField "Number of records" config.records ChangeRecords
        , checkbox "Average all records together" config.average ToggleAverage
        ]


timebaseView : Options -> Model -> Html Msg
timebaseView options config =
    Html.div [ Html.Attributes.id "alazarTimebaseView" ] <|
        [ Html.h4 [] [ Html.text "Clock configuration" ]
        , dropDownBox "Clock source" config.clock_source ChangeClockSource options.clockSourceOptions
        , Html.text "Sample rate: "
        , selectSampleRate options config
        , Html.text " samples/second"
        , Html.br [] []
        , Html.text "Clock edge: "
        , selectClockEdge options config
        , Html.br [] []
        , Html.text "Decimation: "
        , inputDecimation config
        , Html.br [] []
        ]


analogInputsView : Options -> Model -> Html Msg
analogInputsView options config =
    let
        channelsMax =
            List.length (options.channelOptions "")

        channels =
            List.length config.analog_inputs
    in
    Html.div [] <| analogInputsView_ channels channelsMax options config


analogInputsView_ : Int -> Int -> Options -> Model -> List (Html Msg)
analogInputsView_ channels channelsMax options config =
    Html.div []
        (if channels /= 0 then
            List.map2
                (analogInputView options)
                (List.range 1 32)
                config.analog_inputs

         else
            [ Html.text "" ]
        )
        :: (if channels < channelsMax then
                [ Html.button
                    [ Html.Attributes.class "pluginInternalButton"
                    , Html.Events.onClick (ChangeAnalogInputs AddAnalogInput)
                    ]
                    [ Html.text "Add input" ]
                ]

            else
                [ Html.text "" ]
           )


analogInputView : Options -> Int -> AnalogInput -> Html Msg
analogInputView options num analogInput =
    Html.div [ Html.Attributes.class "horizontal-align" ] <|
        Html.h4 [] [ Html.text ("Channel " ++ toString num) ]
            :: [ Html.text "Input channel: "
               , selectInputChannel options analogInput num
               , Html.br [] []
               , Html.text "Input coupling: "
               , selectInputCoupling options analogInput num
               , Html.br [] []
               , Html.text "Input range: "
               , selectInputRange options analogInput num
               , Html.br [] []
               , Html.button
                    [ Html.Attributes.class "pluginInternalButton"
                    , Html.Events.onClick (ChangeAnalogInputs << DeleteAnalogInput <| num)
                    ]
                    [ Html.text "Delete input" ]
               ]


triggerControlView : Options -> Model -> Html Msg
triggerControlView options config =
    Html.div [] <|
        [ Html.div [ Html.Attributes.class "horizontal-align" ] <|
            [ Html.h4 [] [ Html.text "Trigger 1" ]
            , Html.text "Trigger source: "
            , selectTriggerSource1 options config
            ]
                ++ (if config.trigger_source_1 == "TRIG_DISABLE" then
                        [ Html.text "" ]

                    else if config.trigger_source_1 == "TRIG_FORCE" then
                        [ Html.text "" ]

                    else
                        [ Html.br [] []
                        , Html.text "Trigger engine: "
                        , selectTriggerEngine1 options config
                        , Html.br [] []
                        , Html.text "Trigger slope: "
                        , selectTriggerSlope1 options config
                        , Html.br [] []
                        , Html.text "Trigger level: "
                        , inputTriggerLevel1 config
                        , Html.text " volts"
                        ]
                            ++ (if config.trigger_source_1 == "TRIG_EXTERNAL" then
                                    [ Html.text "" ]

                                else
                                    rangeError (calculatedTrigger1 config)
                               )
                   )
        , Html.div [ Html.Attributes.class "horizontal-align" ] <|
            [ Html.h4 [] [ Html.text "Trigger 2" ]
            , Html.text "Trigger source: "
            , selectTriggerSource2 options config
            ]
                ++ (if config.trigger_source_2 == "TRIG_DISABLE" then
                        [ Html.text "" ]

                    else if config.trigger_source_2 == "TRIG_FORCE" then
                        [ Html.text "" ]

                    else
                        [ Html.br [] []
                        , Html.text "Trigger engine: "
                        , selectTriggerEngine2 options config
                        , Html.br [] []
                        , Html.text "Trigger slope: "
                        , selectTriggerSlope2 options config
                        , Html.br [] []
                        , Html.text "Trigger level: "
                        , inputTriggerLevel2 config
                        , Html.text " volts"
                        ]
                            ++ (if config.trigger_source_2 == "TRIG_EXTERNAL" then
                                    [ Html.text "" ]

                                else
                                    rangeError (calculatedTrigger2 config)
                               )
                   )
        , Html.div []
            [ Html.text "Trigger operation: "
            , selectTriggerOperation options config
            ]
        ]


toJson : Model -> Model -> E.Value
toJson default config =
    E.object
        [ ( "clock_source", E.string config.clock_source )
        , ( "sample_rate", E.string config.sample_rate )
        , ( "clock_edge", E.string config.clock_edge )
        , ( "decimation", E.int <| intDefault default.decimation config.decimation )
        , ( "analog_inputs", analogInputsToJson config.analog_inputs )
        , ( "trigger_operation", E.string config.trigger_operation )
        , ( "trigger_engine_1", E.string config.trigger_engine_1 )
        , ( "trigger_source_1", E.string config.trigger_source_1 )
        , ( "trigger_slope_1", E.string config.trigger_slope_1 )
        , ( "trigger_level_1", E.int <| clamp 0 255 <| calculatedTrigger1 config )
        , ( "trigger_volts_str_1", E.string config.triggerLevelString1 )
        , ( "trigger_engine_2", E.string config.trigger_engine_2 )
        , ( "trigger_source_2", E.string config.trigger_source_2 )
        , ( "trigger_slope_2", E.string config.trigger_slope_2 )
        , ( "trigger_level_2", E.int <| clamp 0 255 <| calculatedTrigger2 config )
        , ( "trigger_volts_str_2", E.string config.triggerLevelString2 )
        , ( "pre_trigger_samples", E.int <| intDefault default.pre_trigger_samples config.pre_trigger_samples )
        , ( "post_trigger_samples", E.int <| intDefault default.post_trigger_samples config.post_trigger_samples )
        , ( "records", E.int <| intDefault default.records config.records )
        , ( "average", E.bool config.average )
        , ( "plot", E.string config.plot )
        ]


analogInputsToJson : List AnalogInput -> E.Value
analogInputsToJson analogInputs =
    E.list (List.map analogInputToJson analogInputs)


analogInputToJson : AnalogInput -> E.Value
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

                "8v-50ohm" ->
                    ( "INPUT_RANGE_PM_8_V", "IMPEDANCE_50_OHM" )

                "16v-50ohm" ->
                    ( "INPUT_RANGE_PM_16_V", "IMPEDANCE_50_OHM" )

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
    E.object
        [ ( "input_channel", E.string analogInput.input_channel )
        , ( "input_coupling", E.string analogInput.input_coupling )
        , ( "input_range", E.string range )
        , ( "input_impedance", E.string impedance )
        ]


fromJson : D.Decoder Model
fromJson =
    D.succeed Model
        |> required "clock_source" D.string
        |> required "sample_rate" D.string
        |> required "clock_edge" D.string
        |> required "decimation" (D.int |> D.andThen (\n -> D.succeed <| toString n))
        |> required "analog_inputs" analogInputsFromJson
        |> required "trigger_operation" D.string
        |> required "trigger_engine_1" D.string
        |> required "trigger_source_1" D.string
        |> required "trigger_slope_1" D.string
        |> required "trigger_volts_str_1" D.string
        |> required "trigger_engine_2" D.string
        |> required "trigger_source_2" D.string
        |> required "trigger_slope_2" D.string
        |> required "trigger_volts_str_2" D.string
        |> required "pre_trigger_samples" (D.int |> D.andThen (\n -> D.succeed <| toString n))
        |> required "post_trigger_samples" (D.int |> D.andThen (\n -> D.succeed <| toString n))
        |> required "records" (D.int |> D.andThen (\n -> D.succeed <| toString n))
        |> required "average" D.bool
        |> required "plot" D.string


analogInputsFromJson : D.Decoder (List AnalogInput)
analogInputsFromJson =
    D.list analogInputFromJson


analogInputFromJson : D.Decoder AnalogInput
analogInputFromJson =
    D.field "input_range" D.string
        |> D.andThen
            (\inputRange ->
                D.field "input_impedance" D.string
                    |> D.andThen
                        (\inputImpedance ->
                            let
                                makeInput =
                                    \rangeString ->
                                        D.succeed AnalogInput
                                            |> required "input_channel" D.string
                                            |> required "input_coupling" D.string
                                            |> hardcoded rangeString
                            in
                            case ( inputRange, inputImpedance ) of
                                ( "INPUT_RANGE_PM_100_MV", "IMPEDANCE_50_OHM" ) ->
                                    makeInput "100mv-50ohm"

                                ( "INPUT_RANGE_PM_200_MV", "IMPEDANCE_50_OHM" ) ->
                                    makeInput "200mv-50ohm"

                                ( "INPUT_RANGE_PM_400_MV", "IMPEDANCE_50_OHM" ) ->
                                    makeInput "400mv-50ohm"

                                ( "INPUT_RANGE_PM_800_MV", "IMPEDANCE_50_OHM" ) ->
                                    makeInput "800mv-50ohm"

                                ( "INPUT_RANGE_PM_1_V", "IMPEDANCE_50_OHM" ) ->
                                    makeInput "1v-50ohm"

                                ( "INPUT_RANGE_PM_2_V", "IMPEDANCE_50_OHM" ) ->
                                    makeInput "2v-50ohm"

                                ( "INPUT_RANGE_PM_4_V", "IMPEDANCE_50_OHM" ) ->
                                    makeInput "4v-50ohm"

                                ( "INPUT_RANGE_PM_8_V", "IMPEDANCE_50_OHM" ) ->
                                    makeInput "8v-50ohm"

                                ( "INPUT_RANGE_PM_16_V", "IMPEDANCE_50_OHM" ) ->
                                    makeInput "16v-50ohm"

                                ( "INPUT_RANGE_PM_200_MV", "IMPEDANCE_1M_OHM" ) ->
                                    makeInput "200mv-1Mohm"

                                ( "INPUT_RANGE_PM_400_MV", "IMPEDANCE_1M_OHM" ) ->
                                    makeInput "400mv-1Mohm"

                                ( "INPUT_RANGE_PM_800_MV", "IMPEDANCE_1M_OHM" ) ->
                                    makeInput "800mv-1Mohm"

                                ( "INPUT_RANGE_PM_2_V", "IMPEDANCE_1M_OHM" ) ->
                                    makeInput "2v-1Mohm"

                                ( "INPUT_RANGE_PM_4_V", "IMPEDANCE_1M_OHM" ) ->
                                    makeInput "4v-1Mohm"

                                ( "INPUT_RANGE_PM_8_V", "IMPEDANCE_1M_OHM" ) ->
                                    makeInput "8v-1Mohm"

                                ( "INPUT_RANGE_PM_16_V", "IMPEDANCE_1M_OHM" ) ->
                                    makeInput "16v-1Mohm"

                                otherwise ->
                                    D.fail "unable to decode input range"
                        )
            )



------------------------
-- SELECTION ELEMENtS --
------------------------


selectTriggerOperation : Options -> Model -> Html Msg
selectTriggerOperation options config =
    Html.select [ Html.Events.onInput ChangeTriggerOperation ]
        (options.triggerOperationOptions config.trigger_operation)


selectTriggerEngine1 : Options -> Model -> Html Msg
selectTriggerEngine1 options config =
    Html.select [ Html.Events.onInput ChangeTriggerEngine1 ]
        (options.triggerEngineOptions config.trigger_engine_1)


selectTriggerEngine2 : Options -> Model -> Html Msg
selectTriggerEngine2 options config =
    Html.select [ Html.Events.onInput ChangeTriggerEngine2 ]
        (options.triggerEngineOptions config.trigger_engine_2)


selectTriggerSource1 : Options -> Model -> Html Msg
selectTriggerSource1 options config =
    Html.select [ Html.Events.onInput ChangeTriggerSource1 ]
        (options.triggerChannelOptions config.trigger_source_1)


selectTriggerSource2 : Options -> Model -> Html Msg
selectTriggerSource2 options config =
    Html.select
        [ Html.Events.onInput ChangeTriggerSource2 ]
        (options.triggerChannelOptions config.trigger_source_2)


selectTriggerSlope1 : Options -> Model -> Html Msg
selectTriggerSlope1 options config =
    Html.select
        [ Html.Events.onInput ChangeTriggerSlope1 ]
        (options.triggerSlopeOptions config.trigger_slope_1)


selectTriggerSlope2 : Options -> Model -> Html Msg
selectTriggerSlope2 options config =
    Html.select
        [ Html.Events.onInput ChangeTriggerSlope2 ]
        (options.triggerSlopeOptions config.trigger_slope_2)


inputTriggerLevel1 : Model -> Html Msg
inputTriggerLevel1 config =
    Html.input
        [ Html.Attributes.value config.triggerLevelString1
        , Html.Events.onInput ChangeTriggerLevel1
        ]
        []


inputTriggerLevel2 : Model -> Html Msg
inputTriggerLevel2 config =
    Html.input
        [ Html.Attributes.value config.triggerLevelString2
        , Html.Events.onInput ChangeTriggerLevel2
        ]
        []


selectSampleRate : Options -> Model -> Html Msg
selectSampleRate options config =
    Html.select
        [ Html.Events.onInput ChangeSampleRate ]
        (options.sampleRateOptions config.sample_rate)


selectClockEdge : Options -> Model -> Html Msg
selectClockEdge options config =
    Html.select
        [ Html.Events.onInput ChangeClockEdge ]
        (options.clockEdgeOptions config.clock_edge)


inputDecimation : Model -> Html Msg
inputDecimation config =
    Html.input
        [ Html.Attributes.value config.decimation
        , Html.Events.onInput ChangeDecimation
        ]
        []


selectInputChannel : Options -> AnalogInput -> Int -> Html Msg
selectInputChannel options analogInput num =
    Html.select
        [ Html.Events.onInput (ChangeAnalogInputs << ChangeInputChannel num) ]
        (options.channelOptions analogInput.input_channel)


selectInputCoupling : Options -> AnalogInput -> Int -> Html Msg
selectInputCoupling options input num =
    Html.select
        [ Html.Events.onInput (ChangeAnalogInputs << ChangeInputCoupling num) ]
        (options.inputChannelOptions input.input_coupling)


selectInputRange : Options -> AnalogInput -> Int -> Html Msg
selectInputRange options input num =
    Html.select
        [ Html.Events.onInput (ChangeAnalogInputs << ChangeInputRange num) ]
        (options.inputRangeOptions input.input_range)


sampleRateOptions : List ( String, String ) -> String -> List (Html Msg)
sampleRateOptions options val =
    List.map (\( a, b ) -> anOption val a b) options


clockSourceOptions : List ( String, String ) -> List ( String, String )
clockSourceOptions options =
    options


clockEdgeOptions : List ( String, String ) -> String -> List (Html Msg)
clockEdgeOptions options val =
    List.map (\( a, b ) -> anOption val a b) options


channelOptions : List ( String, String ) -> String -> List (Html Msg)
channelOptions options val =
    List.map (\( a, b ) -> anOption val a b) options


inputChannelOptions : List ( String, String ) -> String -> List (Html Msg)
inputChannelOptions options val =
    List.map (\( a, b ) -> anOption val a b) options


inputRangeOptions : List ( String, String ) -> String -> List (Html Msg)
inputRangeOptions options val =
    List.map (\( a, b ) -> anOption val a b) options


triggerOperationOptions : List ( String, String ) -> String -> List (Html Msg)
triggerOperationOptions options val =
    List.map (\( a, b ) -> anOption val a b) options


triggerEngineOptions : List ( String, String ) -> String -> List (Html Msg)
triggerEngineOptions options val =
    List.map (\( a, b ) -> anOption val a b) options


triggerChannelOptions : List ( String, String ) -> String -> List (Html Msg)
triggerChannelOptions options val =
    List.map (\( a, b ) -> anOption val a b) options


triggerSlopeOptions : List ( String, String ) -> String -> List (Html Msg)
triggerSlopeOptions options val =
    List.map (\( a, b ) -> anOption val a b) options


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

        "SAMPLE_RATE_160MSPS" ->
            samples / 160

        "SAMPLE_RATE_180MSPS" ->
            samples / 180

        otherwise ->
            0.0


calculatedTrigger1 : Model -> Int
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


calculatedTrigger2 : Model -> Int
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

        "8v-50ohm" ->
            8.0

        "8v-1Mohm" ->
            8.0

        "16v-50ohm" ->
            8.0

        "16v-1Mohm" ->
            16.0

        otherwise ->
            -1.0


rangeError : Int -> List (Html msg)
rangeError num =
    if 0 <= num && num <= 255 then
        [ Html.text "" ]

    else
        [ Html.br [] []
        , Html.span [ Html.Attributes.class "error-text" ]
            [ Html.text "Error: trigger voltage is invalid or out of range" ]
        ]


toIntLevel : Float -> Float -> Int
toIntLevel triggerLevelVolts inputRangeVolts =
    128 + (round <| 127.0 * triggerLevelVolts / inputRangeVolts)



-------------------
-- OTHER HELPERS --
-------------------


{-| Helper function to present an option in a drop-down selection box.
-}
anOption : String -> String -> String -> Html msg
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
