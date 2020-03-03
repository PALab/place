port module EquilibarEPR3000 exposing (main)

import Html exposing (Html)
import Json.Decode as D
import Json.Decode.Pipeline exposing (hardcoded, optional, required)
import Json.Encode as E
import Metadata exposing (Metadata)
import Plugin exposing (Plugin)
import PluginHelpers


common : Metadata
common =
    { title = "Equilibar EPR-3000"
    , authors = [ "Jonathan Simpson" ]
    , maintainer = "Jonathan Simpson"
    , email = "jsim921@aucklanduni.ac.nz"
    , url = "https://github.com/palab/place"
    , elm =
        { moduleName = "EquilibarEPR3000"
        }
    , python =
        { moduleName = "equilibar"
        , className = "EquilibarEPR3000"
        }
    , defaultPriority = "0"
    }


type alias Model =
    { start_pressure : String
    , end_pressure : String
    , units : String
    , end_true : Bool
    }


default : Model
default =
    { start_pressure = "0.0"
    , end_pressure = "0.0"
    , units = "MPa"
    , end_true = False
    }


type Msg
    = ChangeStart String
    | ChangeEnd String
    | ChangeUnits String
    | ToggleEnd


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        ChangeStart newStart ->
            ( { model | start_pressure = newStart }, Cmd.none )

        ChangeEnd newEnd ->
            ( { model | end_pressure = newEnd }, Cmd.none )

        ChangeUnits newUnits ->
            ( { model | units = newUnits }, Cmd.none )

        ToggleEnd ->
            ( { model | end_true = not model.end_true, end_pressure = model.start_pressure }, Cmd.none )


userInteractionsView : Model -> List (Html Msg)
userInteractionsView model =
    [ PluginHelpers.floatField "Start pressure" model.start_pressure ChangeStart
    , PluginHelpers.checkbox "Go to pressure at end" model.end_true ToggleEnd
    ]
        ++ (if model.end_true then
                [ PluginHelpers.floatField "End pressure" model.end_pressure ChangeEnd ]

            else
                []
           )
        ++ [ PluginHelpers.dropDownBox "Units" model.units ChangeUnits [ ( "MPa", "MPa" ), ( "psi", "psi" ) ]
           ]


encode : Model -> List ( String, E.Value )
encode model =
    [ ( "start_pressure", E.float (PluginHelpers.floatDefault default.start_pressure model.start_pressure) )
    , ( "end_pressure", E.float (PluginHelpers.floatDefault default.end_pressure model.end_pressure) )
    , ( "units", E.string model.units )
    , ( "end_true", E.bool model.end_true )
    ]


decode : D.Decoder Model
decode =
    D.succeed
        Model
        |> required "start_pressure" (D.float |> D.andThen (D.succeed << toString))
        |> required "end_pressure" (D.float |> D.andThen (D.succeed << toString))
        |> required "units" D.string
        |> required "end_true" D.bool



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
