port module PlaceTimer exposing (main)

import Html exposing (Html)
import Json.Decode as D
import Json.Encode as E
import Json.Decode.Pipeline exposing (optional, required)
import Metadata exposing (Metadata)
import Plugin exposing (Plugin)
import PluginHelpers


common : Metadata
common =
    { title = "PLACE Timer"
    , authors = [ "Jonathan Simpson" ]
    , maintainer = "Jonathan Simpson"
    , email = "jsim921@aucklanduni.ac.nz"
    , url = "https://github.com/palab/place"
    , elm =
        { moduleName = "PlaceTimer"
        }
    , python =
        { moduleName = "place_timer"
        , className = "PlaceTimer"
        }
    , defaultPriority = "110"
    }


type alias Model =
    { intervalType : String
    , constWaitTime : String
    , waitLastUpdate : Bool
    }


default : Model
default =
    { intervalType = "constant"
    , constWaitTime = "1.0"
    , waitLastUpdate = True
    }


type Msg
    = ChangeIntervalType String
    | ChangeConstWaitTime String
    | ToggleWaitLastUpdate
    


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        ChangeIntervalType newValue ->
            ( { model | intervalType = newValue }, Cmd.none )

        ChangeConstWaitTime newValue ->
            ( { model | constWaitTime = newValue }, Cmd.none )

        ToggleWaitLastUpdate ->
            ( { model | waitLastUpdate = not model.waitLastUpdate }, Cmd.none )


userInteractionsView : Model -> List (Html Msg)
userInteractionsView model =
    selectType model
        ++
        [ PluginHelpers.checkbox "Wait on last update" model.waitLastUpdate ToggleWaitLastUpdate
        ]

selectType : Model -> List (Html Msg)
selectType model =
    [ PluginHelpers.dropDownBox
        "Timer Type"
        model.intervalType
        ChangeIntervalType
        [ ( "constant", "Constant Interval" )
        ]
    ]
        ++ (if model.intervalType == "constant" then
                [ PluginHelpers.floatField "Time between updates (s)" model.constWaitTime ChangeConstWaitTime
                ]

            else
                []
           )

encode : Model -> List ( String, E.Value )
encode model =
    [ ( "interval_type", E.string model.intervalType )
    , ( "constant_wait_time", E.float (PluginHelpers.floatDefault default.constWaitTime model.constWaitTime) )
    , ( "wait_on_last_update", E.bool model.waitLastUpdate )
    ]


decode : D.Decoder Model
decode =
    D.succeed
        Model
        |> required "interval_type" D.string
        |> optional "constant_wait_time" (D.float |> D.andThen (D.succeed << toString)) default.constWaitTime
        |> required "wait_on_last_update" D.bool


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
