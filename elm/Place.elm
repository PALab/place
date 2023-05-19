port module Place exposing (main)

{-| This application is used for the PLACE frontend. The primary purpose of this application is
to coordinate the communication between the PLACE plugin frontend applications and the PLACE backend server.

To maintain modularity, plugins are not built _into_ this module, but rather are separate applications.
Communication between the plugin applications and this application is handled through ports into JavaScript.
In JavaScript, we must maintain a list of registered plugins.

-}

import Date exposing (Date)
import Dict exposing (Dict)
import Experiment exposing (Experiment)
import ExperimentResult exposing (ExperimentResult(..))
import Html exposing (Html)
import Html.Attributes
import Html.Events
import Http
import Json.Decode as D
import Json.Encode as E
import Plugin exposing (Plugin)
import Process
import Progress exposing (Progress)
import Svg
import Svg.Attributes
import Svg.Events
import Task
import Time


{-| Plugin applications will submit their configuration plugin to this application vis this port.
-}
port pluginConfig : (E.Value -> msg) -> Sub msg

{-| The web interface will submit this message when the user wants to remove a plugin.
-}
port pluginRemove : (E.Value -> msg) -> Sub msg

{-| Experiment progress is sent back to the plugins applications via this port.
-}
port pluginProgress : E.Value -> Cmd msg

{-| Port command to instruct JavaScript to show the plugin applications on the webpage.
-}
port showPlugins : List String -> Cmd msg

{-| Port command to instruct JavaScript to hide the plugin application on the webpage.
-}
port hidePlugins : () -> Cmd msg

{-| Port command to instruct JavaScript to show the plugin dropdown list on the webpage.
-}
port showPluginsDropdown : () -> Cmd msg

{-| Port command to instruct JavaScript to hide the plugin dropdown list on the webpage.
-}
port hidePluginsDropdown : () -> Cmd msg

{-| Port command to instruct JavaScript to show the window for selecting a config file upload.
-}
port uploadConfigFile : () -> Cmd msg

{-| Port to receive a user uploaded config JSON.
-}
port receiveConfigFile : (E.Value -> msg) -> Sub msg

{-| Port to ping Elm to update when JavaScript has changed something
-}
port commandFromJavaScript : (String -> msg) -> Sub msg

port userChangedPlaceCfg : (Bool) -> Cmd msg

{-| The PLACE application model.
-}
type alias Model =
    { state : State
    , experiment : Experiment
    , history : List ExperimentEntry
    , version : Version
    , showJson : Bool
    , placeConfiguration : String
    , placeCfgChanged : Bool
    }


{-| The state of the PLACE application.
-}
type State
    = Status
    | ConfigureExperiment
    | Started Int
    | LiveProgress Progress
    | Results Bool ExperimentResult
    | History (Maybe String)
    | ConfigurePlace
    | Error String


{-| A version number, based upon the standard _major/minor/revision_ format.
-}
type alias Version =
    { major : Int
    , minor : Int
    , revision : Int
    }


{-| The server status.

If an experiment is running, it will return the progress.
If not, it will return the experiment history.

-}
type ServerStatus
    = Ready (List ExperimentEntry)
    | Running Progress
    | ServerError String
    | Unknown


{-| A completed experiment on the server.
-}
type alias ExperimentEntry =
    { version : String
    , date : Date
    , title : String
    , comments : String
    , location : String
    , filename : String
    }


{-| Data passed to the application when it starts.
-}
type alias Flags =
    { version : String }


{-| This is the entry point to the PLACE application.
-}
main : Program Flags Model Msg
main =
    Html.programWithFlags
        { init = start
        , view = view
        , update = update
        , subscriptions = subscriptions
        }


{-| The starting model and command.

Parses the version from the `Flags` and gets the current server status.

-}
start : Flags -> ( Model, Cmd Msg )
start flags =
    let
        model =
            { state = Status
            , experiment =
                { title = ""
                , directory = ""
                , updates = 1
                , plugins = Dict.empty
                , comments = ""
                }
            , history = []
            , version = parseVersion flags.version
            , showJson = False
            , placeConfiguration = ""
            , placeCfgChanged = False
            }
    in
    update RefreshProgress model


type Msg
    = ChangeExperimentTitle String
    | ChangeExperimentUpdates Int
    | ChangeExperimentComments String
    | ToggleShowJson
    | RemoveExperimentPlugin E.Value
    | UpdateExperimentPlugins E.Value
    | DeleteExperiment String
    | ConfirmDeleteExperiment String
    | GetResults String
    | ConfigureNewExperiment (Maybe Experiment)
    | CloseNewExperiment
    | StartExperimentButton
    | AbortExperimentButton
    | RefreshProgress
    | ShowPluginsDropdown
    | HidePluginsDropdown
    | ServerStatus (Result Http.Error ServerStatus)
    | ExperimentResults (Result Http.Error ExperimentResult)
    | PlaceError String
    | ChooseUploadFile
    | CommandFromJavaScript String
    | FetchPlaceConfiguration (Result Http.Error String)
    | UpdatePlaceConfiguration String
    | SavePlaceConfiguration


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        ChangeExperimentTitle newTitle ->
            let
                oldExperiment =
                    model.experiment
            in
            ( { model | experiment = { oldExperiment | title = newTitle } }, Cmd.none )

        ChangeExperimentComments newComments ->
            let
                oldExperiment =
                    model.experiment
            in
            ( { model | experiment = { oldExperiment | comments = newComments } }, Cmd.none )

        ChangeExperimentUpdates newUpdates ->
            let
                oldExperiment =
                    model.experiment
            in
            ( { model | experiment = { oldExperiment | updates = max 1 <| oldExperiment.updates + newUpdates } }, Cmd.none )

        ToggleShowJson ->
            ( { model | showJson = not model.showJson }, Cmd.none )

        RemoveExperimentPlugin value ->
            case D.decodeValue D.string value of
                Ok elmName ->
                    let
                        oldExperiment =
                            model.experiment

                        newExperiment =
                            { oldExperiment | plugins = Dict.filter (\k v -> k /= elmName) oldExperiment.plugins }
                    in
                    ( { model | experiment = newExperiment }, Cmd.none )

                Err err ->
                    update (PlaceError <| "RemoveExperimentPlugin Err: " ++ toString err) model

        UpdateExperimentPlugins value ->
            case D.decodeValue (D.dict Plugin.decode) value of
                Ok pluginDict ->
                    let
                        oldExperiment =
                            model.experiment

                        newExperiment =
                            { oldExperiment | plugins = Dict.union pluginDict oldExperiment.plugins }
                    in
                    ( { model | experiment = newExperiment }, Cmd.none )

                Err err ->
                    update (PlaceError <| "UpdateExperimentError: " ++ toString err) model

        GetResults location ->
            let
                body =
                    Http.jsonBody (locationEncode location)
            in
            ( model, Http.send ExperimentResults <| Http.post "results/" body ExperimentResult.decode )

        DeleteExperiment location ->
            let
                body =
                    Http.jsonBody (locationEncode location)
            in
            ( model, Http.send ServerStatus <| Http.post "delete/" body serverStatusDecode )

        ConfirmDeleteExperiment location ->
            case model.state of
                History _ ->
                    ( { model | state = History (Just location) }, Cmd.none )

                Results _ progress ->
                    ( { model | state = Results True progress }, Cmd.none )

                otherwise ->
                    ( model, Cmd.none )

        RefreshProgress ->
            ( model, Http.send ServerStatus <| Http.get "status/" serverStatusDecode )

        ShowPluginsDropdown ->
            ( model, showPluginsDropdown () )

        HidePluginsDropdown ->
            ( model, hidePluginsDropdown () )

        ConfigureNewExperiment maybeExperiment ->
            let
                defaultExperiment =
                    { title = ""
                    , directory = ""
                    , updates = 1
                    , comments = ""
                    , plugins =
                        Dict.map
                            (\key plugin ->
                                { plugin
                                    | active = False
                                    , progress = E.null
                                }
                            )
                            model.experiment.plugins
                    }

                newExperiment =
                    Maybe.withDefault defaultExperiment maybeExperiment

                newModel =
                    { model
                        | experiment =
                            { newExperiment
                                | plugins = Dict.map (\key plugin -> { plugin | progress = E.null }) newExperiment.plugins
                            }
                    }
            in
            ( { newModel | state = ConfigureExperiment }
            , Cmd.batch
                [ pluginProgress <| Experiment.encode newModel.experiment
                , showPlugins (Dict.keys newModel.experiment.plugins)
                ]
            )

        CloseNewExperiment ->
            ( { model | state = History Nothing }, hidePlugins () )

        StartExperimentButton ->
            let
                body =
                    Http.jsonBody (Experiment.encode model.experiment)
            in
            ( { model | state = Started model.experiment.updates }, Http.send ServerStatus <| Http.post "submit/" body serverStatusDecode )

        AbortExperimentButton ->
            ( model, Http.send ServerStatus <| Http.get "abort/" serverStatusDecode )

        ServerStatus response ->
            case response of
                Ok status ->
                    case status of
                        Ready history ->
                            ( { model | state = History Nothing, history = history }, hidePlugins () )

                        Running progress ->
                            ( { model | state = LiveProgress progress, experiment = progress.experiment }
                            , Cmd.batch
                                [ pluginProgress <| Experiment.encode progress.experiment
                                , Task.perform (always RefreshProgress) <| Process.sleep <| 500 * Time.millisecond
                                ]
                            )

                        ServerError err ->
                            ( { model | state = Error err }, Cmd.none )

                        Unknown ->
                            ( { model | state = Error "server returned status: Unknown" }, Cmd.none )

                Err err ->
                    ( { model | state = Error (toString err) }, Cmd.none )

        ExperimentResults response ->
            case response of
                Ok results ->
                    case results of
                        Completed progress ->
                            ( { model | state = Results False results, experiment = progress.experiment }
                            , Cmd.batch
                                [ showPlugins (Dict.keys progress.experiment.plugins)
                                , pluginProgress <| Experiment.encode progress.experiment
                                ]
                            )

                        Aborted progress ->
                            ( { model | state = Results False results }, Cmd.none )

                        Empty location ->
                            ( { model | state = Results False results }, Cmd.none )

                Err err ->
                    ( { model | state = Error (toString err) }, Cmd.none )

        PlaceError err ->
            ( { model | state = Error (toString err) }, Cmd.none )

        ChooseUploadFile ->
            ( model, uploadConfigFile () ) 

        CommandFromJavaScript value ->
            case value of
                "progress" ->
                    ( model, pluginProgress <| Experiment.encode model.experiment ) 
                "configuration" ->
                    let
                        body =
                            Http.jsonBody <| encodePlaceConfig False ""
                    in
                    ( { model | state = ConfigurePlace }
                    , Cmd.batch
                        [ Http.send FetchPlaceConfiguration <| Http.post "place_config/" body decodePlaceConfig
                        , userChangedPlaceCfg (False)
                        , hidePlugins () 
                        ]
                    ) 
                _ ->
                    ( model , Cmd.none )

        FetchPlaceConfiguration response ->
            case response of
                Ok configFile ->
                    ( { model | placeConfiguration = configFile, placeCfgChanged = False }, userChangedPlaceCfg (False)) 
                Err err ->
                    ( { model | state = Error (toString err) }, Cmd.none )

        UpdatePlaceConfiguration newCfg ->
            ( { model | placeConfiguration = newCfg, placeCfgChanged = True }, userChangedPlaceCfg (True) )

        SavePlaceConfiguration ->
            let
                body =
                    Http.jsonBody <| encodePlaceConfig True model.placeConfiguration
            in
            ( { model | placeCfgChanged = False }
            , Cmd.batch
                [ Http.send FetchPlaceConfiguration <| Http.post "place_config/" body decodePlaceConfig
                , userChangedPlaceCfg (False)
                ]
            )
            


view : Model -> Html Msg
view model =
    case model.state of
        Status ->
            Html.div [ Html.Attributes.id "statusView" ]
                [ Html.p [ Html.Attributes.class "loaderTitle" ] [ Html.text "Checking status of server..." ]
                , Html.div [ Html.Attributes.class "loader" ] []
                ]

        ConfigureExperiment ->
            Html.div [ Html.Attributes.class "configure-experiment" ]
                [ Html.div [ Html.Attributes.class "configure-experiment__top-row" ]
                    [ Html.div [ Html.Attributes.class "configure-experiment__action-buttons" ]
                        [ Html.button 
                            [ Html.Attributes.class "configure-experiment__history-button"
                            , Html.Events.onClick RefreshProgress
                            ]
                            [ Html.text "Show All Experiments" ]
                        , Html.br [] []    
                        , Html.button 
                            [ Html.Attributes.class "configure-experiment__add-module"
                            , Html.Attributes.id "add-module-button"
                            , Html.Events.onMouseEnter ShowPluginsDropdown 
                            , Html.Events.onMouseLeave HidePluginsDropdown 
                            ]
                            [ Html.text "Add Module" ]
                        ]
                    , Html.div [ Html.Attributes.class "configure-experiment__updates-block" ]
                        [ Html.div [ Html.Attributes.class "configure-experiment__graphic" ]
                            [ placeGraphic "none" model.experiment.updates 0.0 ]
                        , Html.div [ Html.Attributes.class "configure-experiment__change-updates" ]
                            [ Html.button
                                [ Html.Events.onClick <| ChangeExperimentUpdates -100 ]
                                [ Html.text "-100" ]
                            , Html.button
                                [ Html.Events.onClick <| ChangeExperimentUpdates -10 ]
                                [ Html.text "-10" ]
                            , Html.button
                                [ Html.Events.onClick <| ChangeExperimentUpdates -1 ]
                                [ Html.text "-1" ]
                            , Html.button
                                [ Html.Events.onClick <| ChangeExperimentUpdates 1 ]
                                [ Html.text "+1" ]
                            , Html.button
                                [ Html.Events.onClick <| ChangeExperimentUpdates 10 ]
                                [ Html.text "+10" ]
                            , Html.button
                                [ Html.Events.onClick <| ChangeExperimentUpdates 100 ]
                                [ Html.text "+100" ]
                            ]
                        ]
                    , Html.div [ Html.Attributes.class "configure-experiment__upload-area" ]
                        [ Html.button 
                            [ Html.Attributes.class "configure-experiment__upload-config-button"
                            , Html.Attributes.id "upload-config-button"
                            , Html.Events.onMouseEnter ChooseUploadFile
                            ]
                            [ Html.text "Upload config.json" ]
                        ]
                    ]
                

                --, jsonView model -- can be used to debug JSON errors
                , Html.div [ Html.Attributes.class "configure-experiment__input" ]
                    [ Html.input
                        [ Html.Attributes.value model.experiment.title
                        , Html.Attributes.placeholder "Enter Experiment Title"
                        , Html.Events.onInput ChangeExperimentTitle
                        ]
                        []
                    , Html.br [] []
                    , Html.textarea
                        [ Html.Attributes.value model.experiment.comments
                        , Html.Attributes.placeholder "Enter Comments"
                        , Html.Events.onInput ChangeExperimentComments
                        ]
                        []
                    ]
                ]

        Started updates ->
            Html.div []
                [ Html.div [ Html.Attributes.class "configure-experiment__top-row" ]
                    [ Html.div [ Html.Attributes.class "configure-experiment__updates-block" ]
                        [ Html.div [ Html.Attributes.class "configure-experiment__graphic" ]
                            [ placeGraphic "start" updates 0.0 ]
                        ]
                    ]
                , Html.div [ Html.Attributes.id "result-view" ]
                    [ Html.h2 [] [ Html.text model.experiment.title ]
                    , Html.p [] [ Html.em [] [ Html.text model.experiment.comments ] ]
                    , Html.p [] [ Html.text "...starting PLACE" ]
                    ]
                ]

        LiveProgress progress ->
            let
                updatesRemaining =
                    progress.totalUpdates - progress.currentUpdate

                phaseText =
                    case progress.currentPhase of
                        "abort" ->
                            "aborting"

                        "config" ->
                            "configuring"

                        "update" ->
                            "updating"

                        "cleanup" ->
                            "cleaning up after"

                        otherwise ->
                            "working on"
            in
            Html.div []
                
                [ Html.div [ Html.Attributes.class "configure-experiment__top-row" ]
                    [ Html.div [ Html.Attributes.class "configure-experiment__updates-block" ]
                        [ Html.div [ Html.Attributes.class "configure-experiment__graphic" ]
                            [ placeGraphic progress.currentPhase updatesRemaining progress.updateTime ]
                        ]
                    ]
                , Html.div [ Html.Attributes.id "result-view" ]
                    [ Html.h2 [] [ Html.text progress.experiment.title ]
                    , Html.p [] [ Html.em [] [ Html.text progress.experiment.comments ] ]
                    , Html.p [] [ Html.text <| "..." ++ phaseText ++ " " ++ progress.currentPlugin ]
                    ]
                ]

        Results confirmResultDelete results ->
            case results of
                Completed progress ->
                    let
                        location =
                            String.slice -7 -1 progress.directory
                    in
                    Html.div []
                        [ Html.button
                            [ Html.Attributes.class "place-history__show-exp-history-button"
                            , Html.Events.onClick RefreshProgress ]
                            [ Html.text "Show Experiment History" ]
                        , Html.a
                            [ Html.Attributes.href ("download/" ++ location)
                            , Html.Attributes.download True
                            ]
                            [ Html.button [ Html.Attributes.class "place-results__download-button" ] [ Html.text "Download" ] ]
                        , if confirmResultDelete then
                            Html.button
                                [ Html.Attributes.class "place-results__entry-delete-button--confirm"
                                , Html.Events.onClick (DeleteExperiment location)
                                ]
                                [ Html.text "Really?" ]

                          else
                            Html.button
                                [ Html.Attributes.class "place-results__entry-delete-button"
                                , Html.Events.onClick (ConfirmDeleteExperiment location)
                                ]
                                [ Html.text "Delete" ]
                        , Html.button
                            [ Html.Attributes.class "place-results__repeat-experiment-button"
                            , Html.Events.onClick <| ConfigureNewExperiment <| Just progress.experiment ]
                            [ Html.text "Repeat Experiment" ]
                        , Html.div [ Html.Attributes.id "result-view" ]
                            [ Html.h2 [] [ Html.text progress.experiment.title ]
                            , Html.p []
                                [ Html.em [] [ Html.text progress.experiment.comments ]
                                , Html.br [] []
                                , Html.text <|
                                    "("
                                        ++ toString progress.experiment.updates
                                        ++ (if progress.experiment.updates == 1 then
                                                " update)"

                                            else
                                                " updates)"
                                           )
                                ]
                            ]
                        ]

                Aborted experiment ->
                    let
                        location =
                            String.slice -7 -1 (experiment.directory ++ " ")
                    in
                    Html.div []
                        [ Html.button
                            [ Html.Attributes.class "place-history__show-exp-history-button"
                            , Html.Events.onClick RefreshProgress ]
                            [ Html.text "Show Experiment History" ]
                        , Html.a
                            [ Html.Attributes.href ("download/" ++ location)
                            , Html.Attributes.download True
                            ]
                            [ Html.button [ Html.Attributes.class "place-results__download-button" ] [ Html.text "Download" ] ]
                        , if confirmResultDelete then
                            Html.button
                                [ Html.Attributes.class "place-results__entry-delete-button--confirm"
                                , Html.Events.onClick (DeleteExperiment location)
                                ]
                                [ Html.text "Really?" ]

                          else
                            Html.button
                                [ Html.Attributes.class "place-results__entry-delete-button"
                                , Html.Events.onClick (ConfirmDeleteExperiment location)
                                ]
                                [ Html.text "Delete" ]
                        , Html.button
                            [ Html.Attributes.class "place-results__repeat-experiment-button"
                            , Html.Events.onClick <| ConfigureNewExperiment <| Just experiment ]
                            [ Html.text "Repeat Experiment" ]
                        , Html.div [ Html.Attributes.id "result-view" ]
                            [ Html.h2 [] [ Html.text "Experiment Incomplete" ]
                            , Html.p []
                                [ Html.text "This experiment was not completed, possibly due "
                                , Html.text "to being aborted or encountering an error."
                                ]
                            , Html.p []
                                [ Html.text "However, some data was saved, so you may "
                                , Html.text "be able to download the existing data or "
                                , Html.text "repeat the experiment, if desired."
                                ]
                            , Html.h2 [] [ Html.text experiment.title ]
                            , Html.p []
                                [ Html.em [] [ Html.text experiment.comments ]
                                , Html.br [] []
                                , Html.text <|
                                    "("
                                        ++ toString experiment.updates
                                        ++ (if experiment.updates == 1 then
                                                " update)"

                                            else
                                                " updates)"
                                           )
                                ]
                            ]
                        ]

                Empty location ->
                    Html.div []
                        [ Html.button
                            [ Html.Attributes.class "place-history__show-exp-history-button"
                            , Html.Events.onClick RefreshProgress ]
                            [ Html.text "Show Experiment History" ]
                        , if confirmResultDelete then
                            Html.button
                                [ Html.Attributes.class "place-history__entry-delete-button--confirm"
                                , Html.Events.onClick (DeleteExperiment location)
                                ]
                                [ Html.text "Really?" ]

                          else
                            Html.button
                                [ Html.Attributes.class "place-history__entry-delete-button"
                                , Html.Events.onClick (ConfirmDeleteExperiment location)
                                ]
                                [ Html.text "Delete" ]
                        , Html.button
                            [ Html.Attributes.class "place-history__new-experiment-button"
                            , Html.Events.onClick (ConfigureNewExperiment Nothing) ]
                            [ Html.text "New Experiment" ]
                        , Html.div [ Html.Attributes.id "result-view" ]
                            [ Html.h2 [] [ Html.text "No valid data" ]
                            , Html.p []
                                [ Html.text "No valid PLACE data could be found for this "
                                , Html.text "experiment. It is possible that this is due "
                                , Html.text "to some undiscovered PLACE error."
                                ]
                            ]
                        ]

        History maybeLocation ->
            Html.div [ Html.Attributes.id "historyView" ]
                [ Html.h2 [Html.Attributes.class "place-history__title"] [ Html.text "Experiment History" ]
                , Html.button
                    [ Html.Attributes.class "place-history__new-experiment-button"
                    , Html.Events.onClick (ConfigureNewExperiment Nothing) ]
                    [ Html.text "New Experiment" ]
                , Html.table []
                    [ Html.thead []
                        [ Html.tr []
                            [ Html.th
                                [ Html.Attributes.class
                                    "table__heading--version"
                                ]
                                [ Html.text "Version" ]
                            , Html.th
                                [ Html.Attributes.class
                                    "table__heading--timestamp"
                                ]
                                [ Html.text "Timestamp" ]
                            , Html.th
                                [ Html.Attributes.class
                                    "table__heading--title"
                                ]
                                [ Html.text "Title" ]
                            , Html.th
                                [ Html.Attributes.class
                                    "table__heading--comments"
                                ]
                                [ Html.text "Comments" ]
                            , Html.th
                                [ Html.Attributes.class
                                    "table__heading--results"
                                ]
                                [ Html.text "Results" ]
                            , Html.th
                                [ Html.Attributes.class
                                    "table__heading--download"
                                ]
                                [ Html.text "Download" ]
                            , Html.th
                                [ Html.Attributes.class
                                    "table__heading--delete"
                                ]
                                [ Html.text "Delete" ]
                            ]
                        ]
                    , Html.tbody [] <| List.map (historyRow maybeLocation) model.history
                    ]
                {-, Html.button
                    [ Html.Attributes.class "place-history__new-experiment-button"
                    , Html.Events.onClick (ConfigureNewExperiment Nothing) ]
                    [ Html.text "New Experiment" ]-}
                ]

        ConfigurePlace ->
            Html.div [ Html.Attributes.id "placeConfigurationView" ]
                [ Html.h2 [Html.Attributes.class "place-configuration__title"] [ Html.text "PLACE Configuration" ]
                , Html.div [ Html.Attributes.class "place-configuration_buttons" ]
                    [ Html.button
                        [ Html.Attributes.class "place-configuration__show-exp-history-button"
                        , Html.Events.onClick RefreshProgress ]
                        [ Html.text "Show Experiment History" ]
                    , Html.button
                        [ Html.Attributes.class "place-configuration__show-experiment-config"
                        , Html.Events.onClick (ConfigureNewExperiment <| Just model.experiment) ]
                        [ Html.text "Show Experiment View" ]
                    , Html.button
                        [ Html.Attributes.class "place-configuration__save-changes-button"
                        , Html.Attributes.disabled (not model.placeCfgChanged)
                        , Html.Events.onClick SavePlaceConfiguration ]
                        [ Html.text "Save Changes" ]
                    , Html.button
                        [ Html.Attributes.class "place-configuration__revert-button"
                        , Html.Attributes.disabled (not model.placeCfgChanged)
                        , Html.Events.onClick (CommandFromJavaScript "configuration") ]
                        [ Html.text "Revert" ]
                    , Html.button
                        [ Html.Attributes.class "place-configuration__serial-search-button"
                        , Html.Events.onClick RefreshProgress ]
                        [ Html.text "Serial Port Search" ]
                    ]
                , Html.textarea
                    [ Html.Attributes.class "place-configuration__text-area"
                    , Html.Attributes.value model.placeConfiguration
                    , Html.Events.onInput (\newText -> UpdatePlaceConfiguration newText)
                    ]
                    []
                ]      

        Error err ->
            Html.div [ Html.Attributes.id "errorView" ]
                [ Html.button
                    [ Html.Events.onClick RefreshProgress
                    , Html.Attributes.class "error-view__recheck-server-button" ]
                    [ Html.text "Recheck server" ]
                , Html.p [] [ Html.text err ]
                ]


jsonView : Model -> Html Msg
jsonView model =
    Html.div [] <|
        if model.showJson then
            [ Html.button [ Html.Events.onClick <| ToggleShowJson ] [ Html.text "Hide JSON" ]
            , Html.br [] []
            , Html.pre [] [ Html.text <| E.encode 4 <| Experiment.encode model.experiment ]
            ]

        else
            [ Html.button [ Html.Events.onClick <| ToggleShowJson ] [ Html.text "Show JSON" ] ]


subscriptions : Model -> Sub Msg
subscriptions model =
    Sub.batch
        [ pluginConfig (\value -> UpdateExperimentPlugins value)
        , pluginRemove (\value -> RemoveExperimentPlugin value)
        , receiveConfigFile (\value -> experimentFromUserConfig value)
        , commandFromJavaScript  (\value -> CommandFromJavaScript value)
        ]

experimentFromUserConfig : E.Value -> Msg
experimentFromUserConfig config = 
    let
        userConfig = D.decodeValue Experiment.decode config
    in
    case userConfig of
        Ok experiment ->
            ConfigureNewExperiment <| Just experiment 
        Err err ->
            ConfigureNewExperiment <| Nothing

encodePlaceConfig : Bool -> String -> E.Value
encodePlaceConfig updateTrue placeCfg =
    E.object
        [ ( "update", E.bool updateTrue )
        , ( "cfg_string", E.string placeCfg )
        ]

decodePlaceConfig : D.Decoder String
decodePlaceConfig =
    (D.field "cfg_string" D.string)


serverStatusDecode : D.Decoder ServerStatus
serverStatusDecode =
    D.field "status" D.string
        |> D.andThen
            (\status ->
                case status of
                    "Ready" ->
                        D.field "history" experimentEntriesDecode
                            |> D.andThen (D.succeed << Ready)

                    "Running" ->
                        D.field "progress" Progress.decode
                            |> D.andThen (D.succeed << Running)

                    "Error" ->
                        D.field "error_string" D.string
                            |> D.andThen (D.succeed << ServerError)

                    "Unknown" ->
                        D.succeed Unknown

                    otherwise ->
                        D.fail "Invalid status string"
            )


locationEncode : String -> E.Value
locationEncode location =
    E.object
        [ ( "location", E.string location ) ]


emptyPlugins : List Plugin
emptyPlugins =
    []


intDefault : String -> String -> Int
intDefault default value =
    case String.toInt value of
        Ok int ->
            int

        Err _ ->
            Result.withDefault 0 (String.toInt default)


experimentEntriesDecode : D.Decoder (List ExperimentEntry)
experimentEntriesDecode =
    D.field "experiment_entries" (D.list experimentEntryDecode)


experimentEntryDecode : D.Decoder ExperimentEntry
experimentEntryDecode =
    D.map6
        ExperimentEntry
        (D.field "version" D.string)
        (D.field "timestamp" (D.oneOf [ posixEpochDecode, dateDecode ]))
        (D.field "title" D.string)
        (D.field "comments" D.string)
        (D.field "location" D.string)
        (D.field "filename" D.string)


posixEpochDecode : D.Decoder Date
posixEpochDecode =
    D.int
        |> D.andThen
            (toFloat >> ((*) Time.millisecond >> Date.fromTime >> D.succeed))


dateDecode : D.Decoder Date
dateDecode =
    D.string
        |> D.andThen
            (\dateString ->
                case Date.fromString dateString of
                    Ok date ->
                        D.succeed date

                    Err err ->
                        D.fail (toString err)
            )


historyRow : Maybe String -> ExperimentEntry -> Html Msg
historyRow maybeLocation entry =
    let
        minute =
            Date.minute entry.date

        second =
            Date.second entry.date
    in
    Html.tr []
        [ Html.td
            [ Html.Attributes.class "table__data--version" ]
            [ Html.text entry.version ]
        , Html.td
            [ Html.Attributes.class "table__data--timestamp" ]
            [ Html.text <| toString <| Date.hour entry.date
            , Html.text
                (if minute < 10 then
                    ":0"

                 else
                    ":"
                )
            , Html.text <| toString <| Date.minute entry.date
            , Html.text
                (if second < 10 then
                    ":0"

                 else
                    ":"
                )
            , Html.text <| toString <| Date.second entry.date
            , Html.text " "
            , Html.text <| toString <| Date.day entry.date
            , Html.text " "
            , Html.text <| toString <| Date.month entry.date
            , Html.text " "
            , Html.text <| toString <| Date.year entry.date
            ]
        , Html.td
            [ Html.Attributes.class "table__data--title" ]
            [ Html.text <|
                if entry.title == "" then
                    "none"

                else
                    entry.title
            ]
        , Html.td
            [ Html.Attributes.class "table__data--comments" ]
            [ Html.text <|
                if entry.comments == "" then
                    "none"

                else
                    entry.comments
            ]
        , Html.td
            [ Html.Attributes.class "table__data--results" ]
            [ if Date.year entry.date == 1970 then
                Html.text ""

              else
                Html.button
                    [ Html.Attributes.class "place-history__view-results-button"
                    , Html.Events.onClick (GetResults entry.location) ]
                    [ Html.text "View Results" ]
            ]
        , Html.td
            [ Html.Attributes.class "table__data--download" ]
            [ if Date.year entry.date == 1970 then
                Html.text ""

              else
                Html.a
                    [ Html.Attributes.href ("download/" ++ entry.location)
                    , Html.Attributes.download True
                    ]
                    [ Html.button [Html.Attributes.class "place-history__download-button"] [ Html.text "Download" ] ]
            ]
        , Html.td
            [ Html.Attributes.class "table__data--delete" ]
            [ if Maybe.withDefault "" maybeLocation == entry.location then
                Html.button
                    [ Html.Attributes.class "place-history__entry-delete-button--confirm"
                    , Html.Events.onClick (DeleteExperiment entry.location)
                    ]
                    [ Html.text "Really?" ]

              else
                Html.button
                    [ Html.Attributes.class "place-history__entry-delete-button"
                    , Html.Events.onClick (ConfirmDeleteExperiment entry.location)
                    ]
                    [ Html.text "Delete" ]
            ]
        ]


placeGraphic : String -> Int -> Float -> Html Msg
placeGraphic currentPhase updates animate =
    let
        ( size, height ) =
            if updates < 100 then
                ( "40", "73.5" )

            else if updates < 1000 then
                ( "30", "69" )

            else
                ( "20", "66" )

        etaString =
            let
                seconds =
                    toFloat updates * animate
            in
            if seconds > 3.154e7 then
                (toString <| round <| seconds / 3.154e7) ++ " y"

            else if seconds > 86400 then
                (toString <| round <| seconds / 86400) ++ " d"

            else if seconds > 5940 then
                (toString <| round <| seconds / 3600) ++ " h"

            else if seconds > 99 then
                (toString <| round <| seconds / 60) ++ " m"

            else if seconds > 1 then
                (toString <| round <| seconds) ++ " s"

            else
                "0 s"

        ( startClass, configClass, updateClass, cleanupClass, finishedClass ) =
            case currentPhase of
                "start" ->
                    ( "place-progress__start--starting"
                    , "place-progress__config--future-phase"
                    , "place-progress__update--future-phase"
                    , "place-progress__cleanup--future-phase"
                    , "place-progress__finished--running"
                    )

                "config" ->
                    ( "place-progress__start--running"
                    , "place-progress__config--present-phase"
                    , "place-progress__update--future-phase"
                    , "place-progress__cleanup--future-phase"
                    , "place-progress__finished--running"
                    )

                "update" ->
                    ( "place-progress__start--running"
                    , "place-progress__config--past-phase"
                    , "place-progress__update--present-phase"
                    , "place-progress__cleanup--future-phase"
                    , "place-progress__finished--running"
                    )

                "cleanup" ->
                    ( "place-progress__start--running"
                    , "place-progress__config--past-phase"
                    , "place-progress__update--past-phase"
                    , "place-progress__cleanup--present-phase"
                    , "place-progress__finished--running"
                    )

                "abort" ->
                    ( "place-progress__start--aborting"
                    , "place-progress__config--aborting"
                    , "place-progress__update--aborting"
                    , "place-progress__cleanup--aborting"
                    , "place-progress__finished--aborting"
                    )

                otherwise ->
                    ( "place-progress__start--not-running"
                    , "place-progress__config--future-phase"
                    , "place-progress__update--future-phase"
                    , "place-progress__cleanup--future-phase"
                    , "place-progress__finished--not-running"
                    )
    in
    Svg.svg
        [ Svg.Attributes.width "700"
        , Svg.Attributes.height "140"
        , Svg.Attributes.viewBox "0 0 600 120"
        , Svg.Attributes.fill "none"
        ]
        [ Svg.path
            ([ Svg.Attributes.class startClass
             , Svg.Attributes.d <|
                "M 83.959214,59.797863 "
                    ++ "C 84.107399,62.93406 "
                    ++ "61.525366,77.018991 "
                    ++ "58.806293,78.58881 "
                    ++ "55.905923,80.263299 "
                    ++ "31.107693,93.565748 "
                    ++ "28.13154,92.029985 "
                    ++ "25.341421,90.590219 "
                    ++ "24.434529,63.99114 "
                    ++ "24.434562,60.851444 "
                    ++ "c 3.6e-5,-3.349039 "
                    ++ "0.878892,-31.47616 "
                    ++ "3.696978,-33.285703 "
                    ++ "2.641934,-1.696431 "
                    ++ "26.130858,10.817717 "
                    ++ "28.849898,12.387594 "
                    ++ "2.900335,1.67455 "
                    ++ "26.819709,16.499222 "
                    ++ "26.977775,19.844528 "
                    ++ "z"
             ]
                ++ (if startClass == "place-progress__start--not-running" then
                        [ Svg.Events.onClick StartExperimentButton ]

                    else
                        []
                   )
            )
            []
        , Svg.text_
            [ Svg.Attributes.class "place-progress__text"
            , Svg.Attributes.textAnchor "middle"
            , Svg.Attributes.x "48"
            , Svg.Attributes.y "65"
            ]
            [ Svg.text "Start"
            ]
        , Svg.rect
            [ Svg.Attributes.class configClass
            , Svg.Attributes.width "94.997253"
            , Svg.Attributes.height "51.726257"
            , Svg.Attributes.x "117.14876"
            , Svg.Attributes.y "33.917477"
            , Svg.Attributes.rx "3.7218471"
            , Svg.Attributes.ry "3.7218471"
            ]
            []
        , Svg.text_
            [ Svg.Attributes.class "place-progress__text"
            , Svg.Attributes.textAnchor "middle"
            , Svg.Attributes.x "165"
            , Svg.Attributes.y "65"
            ]
            [ Svg.text "Configuration"
            ]
        , Svg.g [ Svg.Attributes.transform "translate(294, 60)" ]
            [ Svg.circle
                [ Svg.Attributes.class updateClass
                , Svg.Attributes.r "42.147732"
                , Svg.Attributes.cx "0"
                , Svg.Attributes.cy "0"
                ]
                []
            , Svg.path
                [ Svg.Attributes.style "fill:#fbfbfb;stroke:#333333;stroke-width:0.47117239"
                , Svg.Attributes.d <|
                    "m 14.732197,39.368652 "
                        ++ "c 0.06981,1.47769 "
                        ++ "-10.5702126,8.114114 "
                        ++ "-11.8513606,8.853776 "
                        ++ "-1.3665697,0.78898 "
                        ++ "-13.0508224,7.056732 "
                        ++ "-14.4530964,6.33311 "
                        ++ "-1.314621,-0.67839 "
                        ++ "-1.741922,-13.21113 "
                        ++ "-1.741914,-14.690468 "
                        ++ "7e-6,-1.577974 "
                        ++ "0.414102,-14.830709 "
                        ++ "1.741914,-15.683303 "
                        ++ "1.244813,-0.7993 "
                        ++ "12.31213445,5.097016 "
                        ++ "13.5932751,5.836691 "
                        ++ "1.3665618,0.788994 "
                        ++ "12.6367199,7.773978 "
                        ++ "12.7111819,9.350194 "
                        ++ "z"
                ]
                (case animate of
                    0.0 ->
                        []

                    seconds ->
                        [ Svg.animateTransform
                            [ Svg.Attributes.attributeName "transform"
                            , Svg.Attributes.type_ "rotate"
                            , Svg.Attributes.from "360 0 0"
                            , Svg.Attributes.to "0 0 0"
                            , Svg.Attributes.dur <| toString seconds ++ "s"
                            , Svg.Attributes.repeatCount "indefinite"
                            ]
                            []
                        ]
                )
            , Svg.path
                [ Svg.Attributes.transform "rotate(180 0 0)"
                , Svg.Attributes.style "fill:#fbfbfb;stroke:#333333;stroke-width:0.47117239"
                , Svg.Attributes.d <|
                    "m 14.732197,39.368652 "
                        ++ "c 0.06981,1.47769 "
                        ++ "-10.5702126,8.114114 "
                        ++ "-11.8513606,8.853776 "
                        ++ "-1.3665697,0.78898 "
                        ++ "-13.0508224,7.056732 "
                        ++ "-14.4530964,6.33311 "
                        ++ "-1.314621,-0.67839 "
                        ++ "-1.741922,-13.21113 "
                        ++ "-1.741914,-14.690468 "
                        ++ "7e-6,-1.577974 "
                        ++ "0.414102,-14.830709 "
                        ++ "1.741914,-15.683303 "
                        ++ "1.244813,-0.7993 "
                        ++ "12.31213445,5.097016 "
                        ++ "13.5932751,5.836691 "
                        ++ "1.3665618,0.788994 "
                        ++ "12.6367199,7.773978 "
                        ++ "12.7111819,9.350194 "
                        ++ "z"
                ]
                (case animate of
                    0.0 ->
                        []

                    seconds ->
                        [ Svg.animateTransform
                            [ Svg.Attributes.attributeName "transform"
                            , Svg.Attributes.type_ "rotate"
                            , Svg.Attributes.from "180 0 0"
                            , Svg.Attributes.to "-180 0 0"
                            , Svg.Attributes.dur <| toString seconds ++ "s"
                            , Svg.Attributes.repeatCount "indefinite"
                            ]
                            []
                        ]
                )
            ]
        , Svg.rect
            [ Svg.Attributes.class cleanupClass
            , Svg.Attributes.width "94.997253"
            , Svg.Attributes.height "51.726257"
            , Svg.Attributes.x "377.39545"
            , Svg.Attributes.y "33.917477"
            , Svg.Attributes.rx "3.7218471"
            , Svg.Attributes.ry "3.7218471"
            ]
            []
        , Svg.text_
            [ Svg.Attributes.class "place-progress__text"
            , Svg.Attributes.textAnchor "middle"
            , Svg.Attributes.x "426"
            , Svg.Attributes.y "65"
            ]
            [ Svg.text "Cleanup"
            ]
        , Svg.path
            [ Svg.Attributes.class finishedClass
            , Svg.Attributes.d <|
                "m 555.38033,93.900713 "
                    ++ "c -1.30688,0.567136 "
                    ++ "-12.79723,0.813896 "
                    ++ "-14.22166,0.83774 "
                    ++ "-1.42443,0.02384 "
                    ++ "-12.9166,0.161806 "
                    ++ "-14.24173,-0.361271 "
                    ++ "-1.32513,-0.523077 "
                    ++ "-9.62451,-8.473495 "
                    ++ "-10.6486,-9.463859 "
                    ++ "-1.02409,-0.990364 "
                    ++ "-9.24783,-9.019002 "
                    ++ "-9.81497,-10.32588 "
                    ++ "-0.56713,-1.306878 "
                    ++ "-0.81389,-12.797226 "
                    ++ "-0.83774,-14.221658 "
                    ++ "-0.0238,-1.424431 "
                    ++ "-0.1618,-12.9166 "
                    ++ "0.36128,-14.241728 "
                    ++ "0.52307,-1.325128 "
                    ++ "8.47349,-9.624517 "
                    ++ "9.46385,-10.648602 "
                    ++ "0.99037,-1.024086 "
                    ++ "9.01901,-9.247829 "
                    ++ "10.32588,-9.814965 "
                    ++ "1.30688,-0.567136 "
                    ++ "12.79723,-0.813896 "
                    ++ "14.22166,-0.83774 "
                    ++ "1.42443,-0.02384 "
                    ++ "12.9166,-0.161806 "
                    ++ "14.24173,0.361271 "
                    ++ "1.32513,0.523077 "
                    ++ "9.62452,8.473495 "
                    ++ "10.6486,9.463859 "
                    ++ "1.02409,0.990364 "
                    ++ "9.24783,9.019002 "
                    ++ "9.81497,10.32588 "
                    ++ "0.56713,1.306878 "
                    ++ "0.81389,12.797226 "
                    ++ "0.83774,14.221658 "
                    ++ "0.0238,1.424431 "
                    ++ "0.1618,12.9166 "
                    ++ "-0.36127,14.241728 "
                    ++ "-0.52308,1.325128 "
                    ++ "-8.4735,9.624517 "
                    ++ "-9.46386,10.648602 "
                    ++ "-0.99037,1.024086 "
                    ++ "-9.019,9.247829 "
                    ++ "-10.32588,9.814965 "
                    ++ "z"
            , Svg.Events.onClick AbortExperimentButton
            ]
            []
        , Svg.text_
            [ Svg.Attributes.class "place-progress__text"
            , Svg.Attributes.textAnchor "middle"
            , Svg.Attributes.x "540"
            , Svg.Attributes.y "65"
            ]
            [ Svg.text
                (case currentPhase of
                    "update" ->
                        etaString

                    "abort" ->
                        "Aborting"

                    otherwise ->
                        "Finish"
                )
            ]
        , Svg.text_
            [ Svg.Attributes.class "place-progress__text"
            , Svg.Attributes.style <| "font-size:" ++ size ++ "px"
            , Svg.Attributes.textAnchor "middle"
            , Svg.Attributes.x "295"
            , Svg.Attributes.y height
            ]
            [ Svg.text
                (case currentPhase of
                    "cleanup" ->
                        "0"

                    "abort" ->
                        "0"

                    otherwise ->
                        toString updates
                )
            ]
        ]


parseVersion : String -> Version
parseVersion versionStr =
    case String.split "." versionStr of
        [ major, minor, revision ] ->
            case Result.map3 Version (String.toInt major) (String.toInt minor) (String.toInt revision) of
                Ok version ->
                    version

                Err _ ->
                    Version 0 0 0

        otherwise ->
            Version 0 0 0


stringToFilename : String -> String
stringToFilename title =
    let
        shortTitle =
            String.left 25 title

        valid =
            \c -> List.member c (String.toList "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_.- ")

        space =
            \c -> List.member c [ '_', '.', '-', ' ' ]

        sub =
            \c ->
                if space c then
                    Just '_'

                else if valid c then
                    Just c

                else
                    Nothing

        filename =
            String.fromList <| List.filterMap sub <| String.toList shortTitle
    in
    case filename of
        "" ->
            "data.zip"

        otherwise ->
            filename ++ ".zip"
