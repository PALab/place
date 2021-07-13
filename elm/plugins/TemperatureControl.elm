port module TemperatureControl exposing (main)

import Html exposing (Html)
import Json.Decode as D
import Json.Decode.Pipeline exposing (hardcoded, optional, required)
import Json.Encode as E
import Metadata exposing (Metadata)
import Plugin exposing (Plugin)
import PluginHelpers

common : Metadata
common =
    { title = "Temperature Control"
    , authors = [ "Jonathan Simpson" ]
    , maintainer = "Jonathan Simpson" 
    , email = "jsim921@aucklanduni.ac.nz" 
    , url = "https://github.com/palab/place" 
    , elm =
        { moduleName = "TemperatureControl"
        }
    , python =
        { moduleName = "temperature_control" 
        , className = "TemperatureControl" 
        }
    , defaultPriority = "11" 
    }

type alias Model =
    { seconds_between_reads : String
    , read_ramptrol : Bool
    , read_omega : Bool
    , plot : Bool
    }

default : Model
default =
    { seconds_between_reads = "10"
    , read_ramptrol = False
    , read_omega = False
    , plot = False
    }

type Msg
    = ChangeSecondsBetweenReads String
    | ToggleReadRamptrol
    | ToggleReadOmega
    | TogglePlot

update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        ChangeSecondsBetweenReads newVal ->
           ( { model | seconds_between_reads = newVal }, Cmd.none )
        ToggleReadRamptrol ->
           ( { model | read_ramptrol = not model.read_ramptrol }, Cmd.none )
        ToggleReadOmega ->
           ( { model | read_omega = not model.read_omega }, Cmd.none )
        TogglePlot ->
           ( { model | plot = not model.plot }, Cmd.none )


userInteractionsView : Model -> List (Html Msg)
userInteractionsView model =
    [ Html.h4 [] [ Html.text "RampTrol Controller" ]
    , PluginHelpers.checkbox "Read temperatures" model.read_ramptrol ToggleReadRamptrol
    , Html.br [] []
    , Html.h4 [] [ Html.text "Omega Infrared Thermometer" ]
    , PluginHelpers.checkbox "Read temperatures" model.read_omega ToggleReadOmega
    , Html.br [] []
    , PluginHelpers.floatField "Time between readings (s)" model.seconds_between_reads ChangeSecondsBetweenReads
    , PluginHelpers.checkbox "Plot" model.plot TogglePlot
    ]


encode : Model -> List ( String, E.Value )
encode model =
    [ ( "seconds_between_reads", E.float (PluginHelpers.floatDefault default.seconds_between_reads model.seconds_between_reads) )  
    , ( "read_ramptrol", E.bool model.read_ramptrol )  
    , ( "read_omega", E.bool model.read_omega ) 
    , ( "plot", E.bool model.plot ) 
    ]

decode : D.Decoder Model
decode =
    D.succeed
        Model
        |> required "seconds_between_reads" (D.float |> D.andThen (D.succeed << toString))
        |> required "read_ramptrol" D.bool
        |> required "read_omega" D.bool
        |> required "plot" D.bool

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
