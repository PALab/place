port module H5Output exposing (main)

import Html exposing (Html)
import Json.Decode as D
import Json.Decode.Pipeline exposing (hardcoded, optional, required)
import Json.Encode as E
import Metadata exposing (Metadata)
import Plugin exposing (Plugin)
import PluginHelpers


common : Metadata
common =
    { title = "PAL H5 output"
    , authors = [ "Paul Freeman" ]
    , maintainer = "Paul Freeman"
    , email = "pfre484@aucklanduni.ac.nz"
    , url = "https://github.com/palab/place"
    , elm =
        { moduleName = "H5Output"
        }
    , python =
        { moduleName = "h5_output"
        , className = "H5Output"
        }
    , defaultPriority = "10"
    }


type alias Model =
    { traceField : String
    , xField : String
    , yField : String
    , thetaField : String
    , extra1Name : String
    , extra1Value : String
    , extra2Name : String
    , extra2Value : String
    , reprocess : String
    }


default : Model
default =
    { traceField = ""
    , xField = ""
    , yField = ""
    , thetaField = ""
    , extra1Name = ""
    , extra1Value = ""
    , extra2Name = ""
    , extra2Value = ""
    , reprocess = ""
    }


type Msg
    = ChangeTraceField String
    | ChangeXField String
    | ChangeYField String
    | ChangeThetaField String
    | ChangeExtra1Name String
    | ChangeExtra1Value String
    | ChangeExtra2Name String
    | ChangeExtra2Value String
    | ChangeReprocess String


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        ChangeTraceField newField ->
            ( { model | traceField = newField }, Cmd.none )

        ChangeXField newField ->
            ( { model | xField = newField }, Cmd.none )

        ChangeYField newField ->
            ( { model | yField = newField }, Cmd.none )

        ChangeThetaField newField ->
            ( { model | thetaField = newField }, Cmd.none )

        ChangeExtra1Name newKey ->
            ( { model | extra1Name = newKey }, Cmd.none )

        ChangeExtra1Value newValue ->
            ( { model | extra1Value = newValue }, Cmd.none )

        ChangeExtra2Name newKey ->
            ( { model | extra2Name = newKey }, Cmd.none )

        ChangeExtra2Value newValue ->
            ( { model | extra2Value = newValue }, Cmd.none )

        ChangeReprocess newValue ->
            ( { model | reprocess = newValue }, Cmd.none )


userInteractionsView : Model -> List (Html Msg)
userInteractionsView model =
    [ PluginHelpers.stringField "trace field" model.traceField ChangeTraceField
    , PluginHelpers.stringField "x-position field" model.xField ChangeXField
    , PluginHelpers.stringField "y-position field" model.yField ChangeYField
    , PluginHelpers.stringField "theta-position field" model.thetaField ChangeThetaField
    , Html.h4 [] [ Html.text "Add arbitrary data to the H5 headers (optional)" ]
    , PluginHelpers.stringField "header key 1" model.extra1Name ChangeExtra1Name
    , PluginHelpers.stringField "header value 1" model.extra1Value ChangeExtra1Value
    , PluginHelpers.stringField "header key 2" model.extra2Name ChangeExtra2Name
    , PluginHelpers.stringField "header value 2" model.extra2Value ChangeExtra2Value
    , Html.h4 [] [ Html.text "Reprocess data in this location (experimental)" ]
    , PluginHelpers.stringField "full path" model.reprocess ChangeReprocess
    ]


encode : Model -> List ( String, E.Value )
encode model =
    [ ( "trace_field", E.string model.traceField )
    , ( "x_position_field", E.string model.xField )
    , ( "y_position_field", E.string model.yField )
    , ( "theta_position_field", E.string model.thetaField )
    , ( "header_extra1_name", E.string model.extra1Name )
    , ( "header_extra1_val", E.string model.extra1Value )
    , ( "header_extra2_name", E.string model.extra2Name )
    , ( "header_extra2_val", E.string model.extra2Value )
    , ( "reprocess", E.string model.reprocess )
    ]


decode : D.Decoder Model
decode =
    D.succeed
        Model
        |> required "trace_field" D.string
        |> required "x_position_field" D.string
        |> required "y_position_field" D.string
        |> required "theta_position_field" D.string
        |> optional "header_extra1_name" D.string ""
        |> optional "header_extra1_val" D.string ""
        |> optional "header_extra2_name" D.string ""
        |> optional "header_extra2_val" D.string ""
        |> optional "reprocess" D.string ""



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
