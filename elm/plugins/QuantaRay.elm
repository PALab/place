port module QuantaRay exposing (main)

import Html exposing (Html)
import Json.Decode as D
import Json.Decode.Pipeline exposing (optional, required)
import Json.Encode as E
import Metadata exposing (Metadata)
import Plugin exposing (Plugin)
import PluginHelpers


common : Metadata
common =
    { title = "QuantaRay INDI laser"
    , authors = [ "Jonathan Simpson", "Paul Freeman" ]
    , maintainer = "Jonathan Simpson"
    , email = "jsim921@aucklanduni.ac.nz"
    , url = "https://github.com/palab/place"
    , elm =
        { moduleName = "QuantaRay"
        }
    , python =
        { moduleName = "quanta_ray"
        , className = "QuantaRayINDI"
        }
    , defaultPriority = "0"
    }


type alias Model =
    { watchdog : String
    , power_mode : String
    , start_power : String
    , end_power : String
    , specify_shots : Bool
    , number_of_shots : String
    , shot_interval : String
    , usr_prof_csv : String
    }


default : Model
default =
    { watchdog = "60"
    , power_mode = "const_power"
    , start_power = "50"
    , end_power = "50"
    , specify_shots = False
    , number_of_shots = "200"
    , shot_interval = "0.1"
    , usr_prof_csv = ""
    }


type Msg
    = ChangeWatchdog String
    | ChangePowerMode String
    | ChangeStartPower String
    | ChangeEndPower String
    | ToggleSpecifyShots
    | ChangeNumShots String
    | ChangeShotInt String
    | ChangeUserProfileCsv String



update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        ChangeWatchdog newWatch ->
            ( { model | watchdog = newWatch }, Cmd.none )

        ChangePowerMode newMode ->
            ( { model | power_mode = newMode, end_power = model.start_power }, Cmd.none )

        ChangeStartPower newPower ->
            ( { model | start_power = newPower, end_power = if model.power_mode == "const_power" then newPower else model.end_power }, Cmd.none )

        ChangeEndPower newPower ->
            ( { model | end_power = newPower }, Cmd.none )

        ToggleSpecifyShots ->
            ( { model | specify_shots = not model.specify_shots, number_of_shots = default.number_of_shots, shot_interval = default.shot_interval }, Cmd.none )

        ChangeNumShots newNum ->
            ( { model | number_of_shots = newNum }, Cmd.none )

        ChangeShotInt newInt ->
            ( { model | shot_interval = newInt }, Cmd.none )

        ChangeUserProfileCsv newValue ->
            ( { model | usr_prof_csv = newValue }, Cmd.none )

        


userInteractionsView : Model -> List (Html Msg)
userInteractionsView model =
    [ PluginHelpers.integerField "Watchdog" model.watchdog ChangeWatchdog
    , PluginHelpers.dropDownBox "Power mode" model.power_mode ChangePowerMode [ ( "const_power", "Constant Power" ), ( "var_power", "Variable Power" ), ( "usr_profile", "User Profile" ) ]
    ]
        ++ (if model.power_mode == "const_power" then
                [ PluginHelpers.integerField "Power" model.start_power ChangeStartPower
                ]

            else
                (if model.power_mode == "var_power" then
                    [ PluginHelpers.integerField "Start power" model.start_power ChangeStartPower
                    , PluginHelpers.integerField "End power" model.end_power ChangeEndPower
                    ]
                else
                    [ PluginHelpers.stringField "Path to .csv profile" model.usr_prof_csv ChangeUserProfileCsv
                    , Html.text "Note: .csv file must contain one column, where each row contains the power percentage for the corresponding update."
                    ]
                )
            )

                ++  [ PluginHelpers.checkbox "Specify shots per update" model.specify_shots ToggleSpecifyShots
                    ]

                        ++ (if model.specify_shots then
                                [ PluginHelpers.integerField "Number of shots" model.number_of_shots ChangeNumShots
                                , PluginHelpers.floatField "Time between shots (s)" model.shot_interval ChangeShotInt
                                ]

                            else
                                []
                            )



encode : Model -> List ( String, E.Value )
encode model =
    [ ( "watchdog_time", E.int (PluginHelpers.intDefault default.watchdog model.watchdog) )
    , ( "power_mode", E.string model.power_mode )
    , ( "start_power_percentage", E.int (PluginHelpers.intDefault default.start_power model.start_power) )
    , ( "end_power_percentage", E.int (PluginHelpers.intDefault default.end_power model.end_power) )
    , ( "specify_shots", E.bool model.specify_shots ) 
    , ( "number_of_shots", E.int (PluginHelpers.intDefault default.number_of_shots model.number_of_shots) )
    , ( "shot_interval", E.float (PluginHelpers.floatDefault default.shot_interval model.shot_interval) )
    , ( "usr_prof_csv", E.string model.usr_prof_csv )
    ]


decode : D.Decoder Model
decode =
    D.succeed
        Model
        |> required "watchdog_time" (D.int |> D.andThen (D.succeed << toString))
        |> required "power_mode" D.string
        |> required "start_power_percentage" (D.int |> D.andThen (D.succeed << toString))
        |> required "end_power_percentage" (D.int |> D.andThen (D.succeed << toString))
        |> required "specify_shots" D.bool
        |> required "number_of_shots" (D.int |> D.andThen (D.succeed << toString))
        |> required "shot_interval" (D.float |> D.andThen (D.succeed << toString))
        |> optional "usr_prof_csv" D.string default.usr_prof_csv



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
                            , metadata = common
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
                                    , metadata = common
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
