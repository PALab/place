port module MokuLab exposing (main)

import Html exposing (Html)
import Html.Attributes
import Json.Decode as D
import Json.Decode.Pipeline exposing (hardcoded, optional, required)
import Json.Encode as E
import Metadata exposing (Metadata)
import Plugin exposing (Plugin)
import PluginHelpers


common : Metadata
common =
    { title = "MokuLab"
    , authors = [ "Rabea Pleiss", "Paul Freeman" ]
    , maintainer = "Rabea Pleiss"
    , email = "rple516@aucklanduni.ac.nz"
    , url = "https://github.com/palab/place"
    , elm =
        { moduleName = "MokuLab"
        }
    , python =
        { moduleName = "moku_lab"
        , className = "MokuLab"
        }
    , defaultPriority = "10"
    }


type alias Model =
    { plot : String
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
    }


default : Model
default =
    { plot = "no"
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
    }


type Msg
    = ChangePlot String
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


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        ChangePlot newPlot ->
            ( { model | plot = newPlot }, Cmd.none )

        TogglePause ->
            ( { model | pause = not model.pause }, Cmd.none )

        ToggleSingleSweep ->
            ( { model | singleSweep = not model.singleSweep }, Cmd.none )

        ChangeFreqStart newFreqStart ->
            ( { model | freqStart = newFreqStart }, Cmd.none )

        ChangeFreqEnd newFreqEnd ->
            ( { model | freqEnd = newFreqEnd }, Cmd.none )

        ChangeDataPoints newDataPoints ->
            ( { model | dataPoints = newDataPoints }, Cmd.none )

        ChangeChannel newChannel ->
            ( { model | channel = newChannel }, Cmd.none )

        ChangeCh1Amp newCh1Amp ->
            ( { model | ch1Amp = newCh1Amp }, Cmd.none )

        ChangeCh2Amp newCh2Amp ->
            ( { model | ch2Amp = newCh2Amp }, Cmd.none )

        ChangeAveragingTime newAveragingTime ->
            ( { model | averagingTime = newAveragingTime }, Cmd.none )

        ChangeSettlingTime newSettlingTime ->
            ( { model | settlingTime = newSettlingTime }, Cmd.none )

        ChangeAveragingCycles newAveragingCycles ->
            ( { model | averagingCycles = newAveragingCycles }, Cmd.none )

        ChangeSettlingCycles newSettlingCycles ->
            ( { model | settlingCycles = newSettlingCycles }, Cmd.none )


userInteractionsView : Model -> List (Html Msg)
userInteractionsView model =
    let
        a1 =
            PluginHelpers.floatDefault default.averagingTime model.averagingTime

        a2 =
            PluginHelpers.floatDefault default.averagingCycles model.averagingCycles

        s1 =
            PluginHelpers.floatDefault default.settlingTime model.settlingTime

        s2 =
            PluginHelpers.floatDefault default.settlingCycles model.settlingCycles

        n =
            PluginHelpers.intDefault default.dataPoints model.dataPoints

        ch1_amp =
            PluginHelpers.floatDefault default.ch1Amp model.ch1Amp

        ch2_amp =
            PluginHelpers.floatDefault default.ch2Amp model.ch2Amp

        setup =
            if n < 512 then
                1

            else
                1 * (n // 512)

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
                toString days ++ " days "

             else if days == 1 then
                toString days ++ " day "

             else
                ""
            )
                ++ (if hours > 1 then
                        toString hours ++ " hours "

                    else if hours == 1 then
                        toString hours ++ " hour "

                    else
                        ""
                   )
                ++ (if mins > 1 then
                        toString mins ++ " minutes "

                    else if mins == 1 then
                        toString mins ++ " minute "

                    else
                        ""
                   )
                ++ (if seconds > 1 then
                        toString seconds ++ " seconds "

                    else if seconds == 1 then
                        toString seconds ++ " second or less. "

                    else if pst < 1 then
                        "less than a second."

                    else
                        ""
                   )
    in
    [ PluginHelpers.dropDownBox "Channels" model.channel ChangeChannel [ ( "ch1", "Channel 1" ), ( "ch2", "Channel 2" ), ( "both", "Both channels" ) ]
    , PluginHelpers.floatField "Start frequency (kHz)" model.freqStart ChangeFreqStart
    , PluginHelpers.floatField "End frequency (kHz)" model.freqEnd ChangeFreqEnd
    , PluginHelpers.integerField "Data points" model.dataPoints ChangeDataPoints
    ]
        ++ (if n < 32 then
                [ Html.p []
                    [ Html.span [ Html.Attributes.class "error-text" ]
                        [ Html.text "Lower bound breached. Please increase to a minimum of 32 points." ]
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
                        [ Html.text "Currently MokuLab only supports even numbers of data points." ]
                    ]
                ]
           )
        ++ [ PluginHelpers.floatField "Ch1 amplitude (V)" model.ch1Amp ChangeCh1Amp
           ]
        ++ (if ch1_amp > 2.0 then
                [ Html.p []
                    [ Html.span [ Html.Attributes.class "error-text" ]
                        [ Html.text "Upper bound breached. Please decrease to a maximum of 2.0 Volts." ]
                    ]
                ]

            else
                []
           )
        ++ [ PluginHelpers.floatField "Ch2 amplitude (V)" model.ch2Amp ChangeCh2Amp
           ]
        ++ (if ch2_amp > 2.0 then
                [ Html.p []
                    [ Html.span [ Html.Attributes.class "error-text" ]
                        [ Html.text "Upper bound breached. Please decrease to a maximum of 2.0 Volts." ]
                    ]
                ]

            else
                []
           )
        ++ [ PluginHelpers.floatField "Averaging time (s)" model.averagingTime ChangeAveragingTime
           ]
        ++ (if a1 < 1.0e-6 then
                [ Html.p []
                    [ Html.span [ Html.Attributes.class "error-text" ]
                        [ Html.text "Lower bound breached. Please increase to a minimum of 1e-06 seconds." ]
                    ]
                ]

            else if a1 > 10 then
                [ Html.p []
                    [ Html.span [ Html.Attributes.class "error-text" ]
                        [ Html.text "Upper bound breached. Please decrease to a maximum of 10 seconds." ]
                    ]
                ]

            else
                []
           )
        ++ [ PluginHelpers.floatField "Settling time (s)" model.settlingTime ChangeSettlingTime
           ]
        ++ (if s1 < 1.0e-6 then
                [ Html.p []
                    [ Html.span [ Html.Attributes.class "error-text" ]
                        [ Html.text "Lower bound breached. Please increase to a minimum of 1e-06 seconds." ]
                    ]
                ]

            else if s1 > 10 then
                [ Html.p []
                    [ Html.span [ Html.Attributes.class "error-text" ]
                        [ Html.text "Upper bound breached. Please decrease to a maximum of 10 seconds." ]
                    ]
                ]

            else
                []
           )
        ++ [ PluginHelpers.integerField "Averaging cycles (no.)" model.averagingCycles ChangeAveragingCycles
           ]
        ++ (if a2 < 1 then
                [ Html.p []
                    [ Html.span [ Html.Attributes.class "error-text" ]
                        [ Html.text "Lower bound breached. Please increase to a minimum of 1 cycle." ]
                    ]
                ]

            else if a2 > 1048576 then
                [ Html.p []
                    [ Html.span [ Html.Attributes.class "error-text" ]
                        [ Html.text "Upper bound breached. Please decrease to a maximum of 1048576 cycle." ]
                    ]
                ]

            else
                []
           )
        ++ [ PluginHelpers.integerField "Settling cycles (no.)" model.settlingCycles ChangeSettlingCycles
           ]
        ++ (if s2 < 1 then
                [ Html.p []
                    [ Html.span [ Html.Attributes.class "error-text" ]
                        [ Html.text "Lower bound breached. Please increase to a minimum of 1 cycle." ]
                    ]
                ]

            else if s2 > 1048576 then
                [ Html.p []
                    [ Html.span [ Html.Attributes.class "error-text" ]
                        [ Html.text "Upper bound breached. Please decrease to a maximum of 1048576 cycle." ]
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


encode : Model -> List ( String, E.Value )
encode model =
    [ ( "plot", E.string model.plot )
    , ( "pause", E.bool model.pause )
    , ( "single_sweep", E.bool model.singleSweep )
    , ( "channel", E.string model.channel )
    , ( "f_start", E.float (PluginHelpers.floatDefault default.freqStart model.freqStart) )
    , ( "f_end", E.float (PluginHelpers.floatDefault default.freqEnd model.freqEnd) )
    , ( "data_points", E.int (PluginHelpers.intDefault default.dataPoints model.dataPoints) )
    , ( "ch1_amp", E.float (PluginHelpers.floatDefault default.ch1Amp model.ch1Amp) )
    , ( "ch2_amp", E.float (PluginHelpers.floatDefault default.ch2Amp model.ch2Amp) )
    , ( "averaging_time", E.float (PluginHelpers.floatDefault default.averagingTime model.averagingTime) )
    , ( "settling_time", E.float (PluginHelpers.floatDefault default.settlingTime model.settlingTime) )
    , ( "averaging_cycles", E.int (PluginHelpers.intDefault default.averagingCycles model.averagingCycles) )
    , ( "settling_cycles", E.int (PluginHelpers.intDefault default.settlingCycles model.settlingCycles) )
    ]


decode : D.Decoder Model
decode =
    D.succeed
        Model
        |> required "plot" D.string
        |> required "pause" D.bool
        |> required "single_sweep" D.bool
        |> required "f_start" (D.float |> D.andThen (D.succeed << toString))
        |> required "f_end" (D.float |> D.andThen (D.succeed << toString))
        |> required "data_points" (D.int |> D.andThen (D.succeed << toString))
        |> required "channel" D.string
        |> required "ch1_amp" (D.float |> D.andThen (D.succeed << toString))
        |> required "ch2_amp" (D.float |> D.andThen (D.succeed << toString))
        |> required "averaging_time" (D.float |> D.andThen (D.succeed << toString))
        |> required "settling_time" (D.float |> D.andThen (D.succeed << toString))
        |> required "averaging_cycles" (D.float |> D.andThen (D.succeed << toString))
        |> required "settling_cycles" (D.float |> D.andThen (D.succeed << toString))


estimatedTime : String -> String -> String -> String -> String -> Float
estimatedTime s_a1 s_a2 s_s1 s_s2 s_n =
    let
        a1 =
            PluginHelpers.floatDefault default.averagingTime s_a1

        a2 =
            PluginHelpers.floatDefault default.averagingCycles s_a2

        s1 =
            PluginHelpers.floatDefault default.settlingTime s_s1

        s2 =
            PluginHelpers.floatDefault default.settlingCycles s_s2

        n =
            PluginHelpers.intDefault default.dataPoints s_n

        f =
            toFloat n
    in
    max (a1 * f) (a2 * f / 37500) + max (s1 * f) (s2 * f / 37500)



----------------------------------------------
-- THINGS YOU PROBABLY DON"T NEED TO CHANGE --
----------------------------------------------


port config : E.Value -> Cmd msg


port removePlugin : String -> Cmd msg


port processProgress : (E.Value -> msg) -> Sub msg


main : Program Never PluginModel PluginMsg
main =
    Html.program
        { init = ( defaultModel, Cmd.none )
        , view = \model -> Html.div [] (viewModel model)
        , update = updatePlugin
        , subscriptions = always <| processProgress UpdateProgress
        }


type alias PluginModel =
    { active : Bool
    , priority : String
    , metadata : Metadata
    , config : Model
    , progress : E.Value
    }


defaultModel : PluginModel
defaultModel =
    { active = False
    , priority = common.defaultPriority
    , metadata = common
    , config = default
    , progress = E.null
    }


type PluginMsg
    = ToggleActive ------------ turn the plugin on and off on the webpage
    | ChangePriority String --- change the order of execution, relative to other plugins
    | ChangePlugin Msg -------- change one of the custom values in the plugin
    | SendToPlace ------------- sends the values in the model to PLACE
    | UpdateProgress E.Value -- update current progress of a running experiment
    | Close ------------------- close the plugin tab on the webpage


newModel : PluginModel -> ( PluginModel, Cmd PluginMsg )
newModel model =
    updatePlugin SendToPlace model


viewModel : PluginModel -> List (Html PluginMsg)
viewModel model =
    PluginHelpers.titleWithAttributions
        common.title
        model.active
        ToggleActive
        Close
        common.authors
        common.maintainer
        common.email
        ++ (if model.active then
                PluginHelpers.integerField "Priority" model.priority ChangePriority
                    :: List.map (Html.map ChangePlugin) (userInteractionsView model.config)
                    ++ [ PluginHelpers.displayAllProgress model.progress ]

            else
                [ Html.text "" ]
           )


updatePlugin : PluginMsg -> PluginModel -> ( PluginModel, Cmd PluginMsg )
updatePlugin msg model =
    case msg of
        ToggleActive ->
            if model.active then
                newModel { model | active = False }

            else
                newModel { model | active = True }

        ChangePriority newPriority ->
            newModel { model | priority = newPriority }

        ChangePlugin pluginMsg ->
            let
                config =
                    model.config

                ( newConfig, cmd ) =
                    update pluginMsg model.config

                newCmd =
                    Cmd.map ChangePlugin cmd

                ( updatedModel, updatedCmd ) =
                    newModel { model | config = newConfig }
            in
            ( updatedModel, Cmd.batch [ newCmd, updatedCmd ] )

        SendToPlace ->
            ( model
            , config <|
                E.object
                    [ ( model.metadata.elm.moduleName
                      , Plugin.encode
                            { active = model.active
                            , priority = PluginHelpers.intDefault model.metadata.defaultPriority model.priority
                            , metadata = model.metadata
                            , config = E.object (encode model.config)
                            , progress = E.null
                            }
                      )
                    ]
            )

        UpdateProgress value ->
            case D.decodeValue Plugin.decode value of
                Err err ->
                    ( { model | progress = E.string <| "Decode plugin error: " ++ err }, Cmd.none )

                Ok plugin ->
                    if plugin.active then
                        case D.decodeValue decode plugin.config of
                            Err err ->
                                ( { model | progress = E.string <| "Decode value error: " ++ err }, Cmd.none )

                            Ok config ->
                                newModel
                                    { active = plugin.active
                                    , priority = toString plugin.priority
                                    , metadata = plugin.metadata
                                    , config = config
                                    , progress = plugin.progress
                                    }

                    else
                        newModel defaultModel

        Close ->
            let
                ( clearModel, clearModelCmd ) =
                    newModel defaultModel
            in
            ( clearModel, Cmd.batch [ clearModelCmd, removePlugin model.metadata.elm.moduleName ] )
