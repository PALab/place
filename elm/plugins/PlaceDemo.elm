port module PlaceDemo exposing (main)

import Html exposing (Html)
import Json.Decode as D
import Json.Encode as E
import Metadata exposing (Metadata)
import Plugin exposing (Plugin)
import PluginHelpers


common : Metadata
common =
    { title = "PLACE Demo Instrument"
    , authors = [ "Paul Freeman" ]
    , maintainer = "Paul Freeman"
    , email = "paul.freeman.cs@gmail.com"
    , url = "https://github.com/palab/place"
    , elm =
        { moduleName = "PlaceDemo"
        }
    , python =
        { moduleName = "place_demo"
        , className = "PlaceDemo"
        }
    , defaultPriority = "10"
    }


type alias Model =
    { points : String
    , configSleep : String
    , updateSleep : String
    , cleanupSleep : String
    , plot : Bool
    }


default : Model
default =
    { points = "128"
    , configSleep = "5.0"
    , updateSleep = "1.0"
    , cleanupSleep = "5.0"
    , plot = True
    }


type Msg
    = ChangeConfigSleep String
    | ChangeUpdateSleep String
    | ChangeCleanupSleep String
    | ChangePoints String
    | TogglePlot


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        ChangeConfigSleep newValue ->
            ( { model | configSleep = newValue }, Cmd.none )

        ChangeUpdateSleep newValue ->
            ( { model | updateSleep = newValue }, Cmd.none )

        ChangeCleanupSleep newValue ->
            ( { model | cleanupSleep = newValue }, Cmd.none )

        ChangePoints newValue ->
            ( { model | points = newValue }, Cmd.none )

        TogglePlot ->
            ( { model | plot = not model.plot }, Cmd.none )


userInteractionsView : Model -> List (Html Msg)
userInteractionsView model =
    [ PluginHelpers.integerField "Number of Points" model.points ChangePoints
    , PluginHelpers.floatField "Sleep time during config" model.configSleep ChangeConfigSleep
    , PluginHelpers.floatField "Sleep time between updates" model.updateSleep ChangeUpdateSleep
    , PluginHelpers.floatField "Sleep time during cleanup" model.cleanupSleep ChangeCleanupSleep
    , PluginHelpers.checkbox "Get plots during execution" model.plot TogglePlot
    ]


encode : Model -> List ( String, E.Value )
encode model =
    [ ( "number_of_points", E.int (PluginHelpers.intDefault "128" model.points) )
    , ( "config_sleep_time", E.float (PluginHelpers.floatDefault default.configSleep model.configSleep) )
    , ( "update_sleep_time", E.float (PluginHelpers.floatDefault default.updateSleep model.updateSleep) )
    , ( "cleanup_sleep_time", E.float (PluginHelpers.floatDefault default.cleanupSleep model.cleanupSleep) )
    , ( "plot", E.bool model.plot )
    ]


decode : D.Decoder Model
decode =
    D.map5
        Model
        (D.field "number_of_points" D.int |> D.andThen (D.succeed << toString))
        (D.field "config_sleep_time" D.float |> D.andThen (D.succeed << toString))
        (D.field "update_sleep_time" D.float |> D.andThen (D.succeed << toString))
        (D.field "cleanup_sleep_time" D.float |> D.andThen (D.succeed << toString))
        (D.field "plot" D.bool)



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
    = ToggleActive
    | ChangePriority String
    | ChangePlugin Msg
    | SendToPlace
    | UpdateProgress E.Value
    | Close


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
                    if plugin.priority == -999999 then
                        newModel defaultModel

                    else
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

        Close ->
            let
                ( clearModel, clearModelCmd ) =
                    newModel defaultModel
            in
            ( clearModel, Cmd.batch [ clearModelCmd, removePlugin model.metadata.elm.moduleName ] )
