port module Place exposing (main)

import Date exposing (Date)
import Dict exposing (Dict)
import Html exposing (Html)
import Html.Attributes
import Html.Events
import Http
import Json.Decode
import Json.Encode


port pluginConfig : (Json.Encode.Value -> msg) -> Sub msg


port pluginProgress : ( String, Json.Encode.Value ) -> Cmd msg


port showPlugins : () -> Cmd msg


port hidePlugins : () -> Cmd msg


type State
    = Status
    | ConfigureExperiment
    | LiveProgress Progress
    | Refresh
    | Result
    | History
    | Error String


type alias Experiment =
    { title : String
    , updates : String
    , plugins : List Plugin
    , comments : String
    }


type alias ExperimentEntry =
    { version : String
    , date : Date
    , title : String
    , comments : String
    , location : String
    }


type alias Progress =
    { directory : String
    , currentPhase : String
    , currentPlugin : String
    , currentUpdate : Int
    , totalUpdates : Int
    , pluginProgress : Dict String Json.Decode.Value
    }


type ServerStatus
    = Ready
    | Running Progress
    | ServerError String
    | Unknown


type alias Plugin =
    { pythonModuleName : String
    , pythonClassName : String
    , elmModuleName : String
    , priority : Int
    , dataRegister : List String
    , config : Json.Encode.Value
    }


type alias Model =
    { state : State
    , experiment : Experiment
    , history : List ExperimentEntry
    , version : Version
    , error : String
    }


init : Model
init =
    { state = Status
    , experiment =
        { title = ""
        , updates = "1"
        , plugins = []
        , comments = ""
        }
    , history = []
    , version = Version 0 0 0
    , error = "none"
    }


type Msg
    = ReceiveServerStatus (Result Http.Error ServerStatus)
      -- experiment messages
    | ChangeExperimentTitle String
    | ChangeExperimentUpdates String
    | ChangeExperimentComments String
    | UpdateExperimentPlugins Json.Encode.Value
      -- history messages
    | DeleteExperiment String
      -- state machine messages
    | ConfigureNewExperiment
    | CloseNewExperiment
    | StartExperimentButton
    | StartExperimentResponse (Result Http.Error ServerStatus)
    | RefreshProgressButton
    | RefreshProgressResponse (Result Http.Error ServerStatus)
    | RetrieveHistory
    | RetrieveHistoryResponse (Result Http.Error (List ExperimentEntry))
    | PlaceError String


main : Program Flags Model Msg
main =
    Html.programWithFlags
        { init = \flags -> update RetrieveHistory init
        , view = view
        , update = update
        , subscriptions = subscriptions
        }


type alias Version =
    { major : Int
    , minor : Int
    , revision : Int
    }


type alias Flags =
    { version : String }


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        ReceiveServerStatus response ->
            case response of
                Ok status ->
                    case status of
                        Ready ->
                            ( { model | state = History }, hidePlugins () )

                        Running progress ->
                            ( { model | state = LiveProgress progress }, showPlugins () )

                        ServerError err ->
                            ( { model | state = Error ("PLACE error: " ++ err) }, Cmd.none )

                        Unknown ->
                            ( { model | state = Error "PLACE unknown status" }, Cmd.none )

                Err err ->
                    ( { model | state = Error ("Error: " ++ toString err) }, Cmd.none )

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
                ( { model | experiment = { oldExperiment | updates = newUpdates } }, Cmd.none )

        UpdateExperimentPlugins jsonValue ->
            case Json.Decode.decodeValue (Json.Decode.list pluginDecode) jsonValue of
                Ok newData ->
                    let
                        oldExperiment =
                            model.experiment

                        newPlugins =
                            case List.head newData of
                                Nothing ->
                                    model.experiment.plugins

                                Just data ->
                                    ((if data.pythonClassName == "None" then
                                        emptyPlugins
                                      else
                                        newData
                                     )
                                        ++ List.filter
                                            (.pythonModuleName >> ((/=) data.pythonModuleName))
                                            model.experiment.plugins
                                    )
                    in
                        ( { model | experiment = { oldExperiment | plugins = newPlugins } }, Cmd.none )

                Err err ->
                    update (PlaceError (toString err)) model

        DeleteExperiment location ->
            let
                body =
                    Http.jsonBody (locationEncode location)
            in
                ( model, Http.send RetrieveHistoryResponse <| Http.post "delete/" body experimentEntriesDecode )

        RefreshProgressButton ->
            ( model, statusCmd RefreshProgressResponse )

        RefreshProgressResponse response ->
            case response of
                Ok status ->
                    case status of
                        Ready ->
                            ( { model | state = Result }, Cmd.none )

                        Running progress ->
                            let
                                updatePlugins =
                                    Dict.values <| Dict.map (\a b -> pluginProgress ( a, b )) progress.pluginProgress
                            in
                                { model | state = LiveProgress progress } ! updatePlugins

                        ServerError err ->
                            ( { model | state = Error err }, Cmd.none )

                        Unknown ->
                            ( { model | state = Error "server returned status: Unknown" }, Cmd.none )

                Err err ->
                    ( { model | state = Error (toString err) }, Cmd.none )

        ConfigureNewExperiment ->
            ( { model | state = ConfigureExperiment }, showPlugins () )

        CloseNewExperiment ->
            ( { model | state = History }, hidePlugins () )

        StartExperimentButton ->
            let
                body =
                    Http.jsonBody (experimentEncode model.experiment)
            in
                ( model, Http.send StartExperimentResponse <| Http.post "submit/" body serverStatusDecode )

        StartExperimentResponse response ->
            case response of
                Ok serverStatus ->
                    case serverStatus of
                        Ready ->
                            ( model, statusCmd StartExperimentResponse )

                        Running progress ->
                            ( { model | state = LiveProgress progress }, showPlugins () )

                        ServerError err ->
                            ( { model | state = Error ("PLACE error: " ++ err) }, Cmd.none )

                        Unknown ->
                            ( { model | state = Error "PLACE unknown status" }, Cmd.none )

                Err err ->
                    ( { model | state = Error (toString err) }, Cmd.none )

        RetrieveHistory ->
            ( model, Http.send RetrieveHistoryResponse <| Http.get "history/" experimentEntriesDecode )

        RetrieveHistoryResponse response ->
            case response of
                Ok experimentEntries ->
                    ( { model | state = History, history = experimentEntries }, hidePlugins () )

                Err err ->
                    ( { model | state = Error (toString err) }, Cmd.none )

        PlaceError err ->
            ( { model | state = Error (toString err) }, Cmd.none )


view : Model -> Html Msg
view model =
    case model.state of
        Status ->
            Html.div [ Html.Attributes.id "statusView" ]
                [ Html.p [ Html.Attributes.class "loaderTitle" ] [ Html.text "Checking status of server..." ]
                , Html.div [ Html.Attributes.class "loader" ] []
                ]

        ConfigureExperiment ->
            experimentView model

        LiveProgress progress ->
            progressView model progress

        Refresh ->
            Html.div [ Html.Attributes.id "refreshingView" ]
                [ Html.p [] [ Html.text "Refreshing..." ]
                ]

        Result ->
            Html.div [ Html.Attributes.id "resultView" ]
                [ Html.p [] [ Html.text "You have reached the incomplete Result view" ]
                , Html.button
                    [ Html.Events.onClick RetrieveHistory ]
                    [ Html.text "Show all experiments" ]
                ]

        History ->
            Html.div [ Html.Attributes.id "historyView" ]
                [ Html.table []
                    [ Html.thead []
                        [ Html.tr []
                            [ Html.th [] [ Html.text "PLACE version" ]
                            , Html.th [] [ Html.text "Timestamp" ]
                            , Html.th [] [ Html.text "Title" ]
                            , Html.th [] [ Html.text "Comments" ]
                            , Html.th [] [ Html.text "Download" ]
                            , Html.th [] [ Html.text "Delete" ]
                            ]
                        ]
                    , Html.tbody [] <| List.map historyRow model.history
                    ]
                , Html.button
                    [ Html.Events.onClick ConfigureNewExperiment ]
                    [ Html.text "New experiment" ]
                ]

        Error err ->
            Html.div [ Html.Attributes.id "errorView" ]
                [ Html.p [] [ Html.text (model.error) ] ]


progressView : Model -> Progress -> Html Msg
progressView model progress =
    let
        percent =
            round <| 100 * (toFloat progress.currentUpdate / toFloat progress.totalUpdates)
    in
        Html.div []
            [ Html.p [] [ Html.text <| "Experiment " ++ toString percent ++ "% complete" ]
            , Html.p [] [ Html.text <| "Phase: " ++ progress.currentPhase ]
            , Html.p [] [ Html.text <| "Plugin: " ++ progress.currentPlugin ]
            , Html.button
                [ Html.Events.onClick RefreshProgressButton ]
                [ Html.text "Refresh progress" ]
            ]


experimentView : Model -> Html Msg
experimentView model =
    Html.div [] [ startExperimentView model, inputsView model ]


startExperimentView : Model -> Html Msg
startExperimentView model =
    Html.div [] <|
        [ Html.button
            [ Html.Attributes.id "start-button"
            , Html.Events.onClick StartExperimentButton
            ]
            [ Html.text "Start" ]
        , Html.p [ Html.Attributes.id "updates-p" ]
            [ Html.span [ Html.Attributes.id "update-text" ] [ Html.text "Updates: " ]
            , Html.input
                [ Html.Attributes.id "updateNumber"
                , Html.Attributes.value model.experiment.updates
                , Html.Events.onInput ChangeExperimentUpdates
                ]
                []
            ]
        ]
            ++ (case String.toInt model.experiment.updates of
                    Ok _ ->
                        []

                    Err error_msg ->
                        [ Html.br [] [], Html.span [ Html.Attributes.class "error-text" ] [ Html.text error_msg ] ]
               )


inputsView : Model -> Html Msg
inputsView model =
    Html.p []
        [ Html.text "Title: "
        , Html.input [ Html.Attributes.value model.experiment.title, Html.Events.onInput ChangeExperimentTitle ] []
        , Html.br [] []
        , Html.text "Comments:"
        , Html.br [] []
        , Html.textarea
            [ Html.Attributes.id "commentsBox"
            , Html.Attributes.rows 3
            , Html.Attributes.value model.experiment.comments
            , Html.Events.onInput ChangeExperimentComments
            ]
            []
        , Html.br [] []
        ]


subscriptions : Model -> Sub Msg
subscriptions model =
    Sub.batch [ pluginConfig (\value -> UpdateExperimentPlugins value) ]


statusCmd : (Result Http.Error ServerStatus -> Msg) -> Cmd Msg
statusCmd callback =
    Http.send callback <| Http.get "status/" serverStatusDecode


serverStatusDecode : Json.Decode.Decoder ServerStatus
serverStatusDecode =
    Json.Decode.field "status" Json.Decode.string
        |> Json.Decode.andThen
            (\status ->
                case status of
                    "Ready" ->
                        Json.Decode.succeed Ready

                    "Running" ->
                        Json.Decode.field "progress" progressDecode
                            |> Json.Decode.andThen (Json.Decode.succeed << Running)

                    "Error" ->
                        Json.Decode.field "error_string" Json.Decode.string
                            |> Json.Decode.andThen (Json.Decode.succeed << ServerError)

                    "Unknown" ->
                        Json.Decode.succeed Unknown

                    otherwise ->
                        Json.Decode.fail "Invalid status string"
            )


progressDecode : Json.Decode.Decoder Progress
progressDecode =
    Json.Decode.map6
        Progress
        (Json.Decode.field "directory" Json.Decode.string)
        (Json.Decode.field "current_phase" Json.Decode.string)
        (Json.Decode.field "current_plugin" Json.Decode.string)
        (Json.Decode.field "current_update" Json.Decode.int)
        (Json.Decode.field "total_updates" Json.Decode.int)
        (Json.Decode.field "plugin" <| Json.Decode.dict Json.Decode.value)


pluginEncode : Plugin -> Json.Encode.Value
pluginEncode plugin =
    Json.Encode.object
        [ ( "python_module_name", Json.Encode.string plugin.pythonModuleName )
        , ( "python_class_name", Json.Encode.string plugin.pythonClassName )
        , ( "elm_module_name", Json.Encode.string plugin.elmModuleName )
        , ( "priority", Json.Encode.int plugin.priority )
        , ( "data_register", Json.Encode.list <| List.map Json.Encode.string plugin.dataRegister )
        , ( "config", plugin.config )
        ]


pluginDecode : Json.Decode.Decoder Plugin
pluginDecode =
    Json.Decode.map6
        Plugin
        (Json.Decode.field "python_module_name" Json.Decode.string)
        (Json.Decode.field "python_class_name" Json.Decode.string)
        (Json.Decode.field "elm_module_name" Json.Decode.string)
        (Json.Decode.field "priority" Json.Decode.int)
        (Json.Decode.field "data_register" (Json.Decode.list Json.Decode.string))
        (Json.Decode.field "config" Json.Decode.value)


experimentEncode : Experiment -> Json.Encode.Value
experimentEncode experiment =
    Json.Encode.object
        [ ( "updates", Json.Encode.int <| intDefault "1" experiment.updates )
        , ( "plugins", Json.Encode.list <| List.map pluginEncode experiment.plugins )
        , ( "title", Json.Encode.string experiment.title )
        , ( "comments", Json.Encode.string experiment.comments )
        ]


locationEncode : String -> Json.Encode.Value
locationEncode location =
    Json.Encode.object
        [ ( "location", Json.Encode.string location ) ]


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


experimentShowData : Experiment -> List (Html Msg)
experimentShowData experiment =
    let
        makeHeading =
            \num name ->
                Html.th [ Html.Attributes.id ("device" ++ toString num) ] [ Html.text name ]

        makeModuleHeadings =
            \device num -> List.map (makeHeading num) device.dataRegister

        allHeadings =
            List.concat <|
                List.map2 makeModuleHeadings (List.sortBy .priority experiment.plugins) <|
                    List.map (\x -> x % 3 + 1) <|
                        List.range 1 (List.length experiment.plugins)

        numHeadings =
            List.length allHeadings

        updates =
            intDefault "1" experiment.updates
    in
        [ Html.h2 [] [ Html.text "NumPy data array layout" ]
        , Html.table [ Html.Attributes.id "data-table" ] <|
            [ Html.tr []
                (Html.th [] []
                    :: Html.th [ Html.Attributes.id "device0" ] [ Html.text "time" ]
                    :: allHeadings
                )
            ]
                ++ (case updates of
                        1 ->
                            [ Html.tr []
                                (Html.td [] [ Html.text "0" ]
                                    :: List.repeat (numHeadings + 1) (Html.td [] [])
                                )
                            ]

                        2 ->
                            [ Html.tr []
                                (Html.td [] [ Html.text "0" ]
                                    :: List.repeat (numHeadings + 1) (Html.td [] [])
                                )
                            , Html.tr []
                                (Html.td [] [ Html.text "1" ]
                                    :: List.repeat (numHeadings + 1) (Html.td [] [])
                                )
                            ]

                        3 ->
                            [ Html.tr []
                                (Html.td [] [ Html.text "0" ]
                                    :: List.repeat (numHeadings + 1) (Html.td [] [])
                                )
                            , Html.tr []
                                (Html.td [] [ Html.text "1" ]
                                    :: List.repeat (numHeadings + 1) (Html.td [] [])
                                )
                            , Html.tr []
                                (Html.td [] [ Html.text "2" ]
                                    :: List.repeat (numHeadings + 1) (Html.td [] [])
                                )
                            ]

                        4 ->
                            [ Html.tr []
                                (Html.td [] [ Html.text "0" ]
                                    :: List.repeat (numHeadings + 1) (Html.td [] [])
                                )
                            , Html.tr []
                                (Html.td [] [ Html.text "1" ]
                                    :: List.repeat (numHeadings + 1) (Html.td [] [])
                                )
                            , Html.tr []
                                (Html.td [] [ Html.text "2" ]
                                    :: List.repeat (numHeadings + 1) (Html.td [] [])
                                )
                            , Html.tr []
                                (Html.td [] [ Html.text "3" ]
                                    :: List.repeat (numHeadings + 1) (Html.td [] [])
                                )
                            ]

                        5 ->
                            [ Html.tr []
                                (Html.td [] [ Html.text "0" ]
                                    :: List.repeat (numHeadings + 1) (Html.td [] [])
                                )
                            , Html.tr []
                                (Html.td [] [ Html.text "1" ]
                                    :: List.repeat (numHeadings + 1) (Html.td [] [])
                                )
                            , Html.tr []
                                (Html.td [] [ Html.text "2" ]
                                    :: List.repeat (numHeadings + 1) (Html.td [] [])
                                )
                            , Html.tr []
                                (Html.td [] [ Html.text "3" ]
                                    :: List.repeat (numHeadings + 1) (Html.td [] [])
                                )
                            , Html.tr []
                                (Html.td [] [ Html.text "4" ]
                                    :: List.repeat (numHeadings + 1) (Html.td [] [])
                                )
                            ]

                        otherwise ->
                            [ Html.tr []
                                (Html.td [] [ Html.text "0" ]
                                    :: List.repeat (numHeadings + 1) (Html.td [] [])
                                )
                            , Html.tr []
                                (Html.td [] [ Html.text "1" ]
                                    :: List.repeat (numHeadings + 1) (Html.td [] [])
                                )
                            , Html.tr [ Html.Attributes.class "skip-row" ]
                                (Html.td [] [ Html.text "..." ]
                                    :: List.repeat (numHeadings + 1)
                                        (Html.td []
                                            [ Html.text "..." ]
                                        )
                                )
                            , Html.tr []
                                (Html.td [] [ Html.text (toString (updates - 2)) ]
                                    :: List.repeat (numHeadings + 1) (Html.td [] [])
                                )
                            , Html.tr []
                                (Html.td [] [ Html.text (toString (updates - 1)) ]
                                    :: List.repeat (numHeadings + 1) (Html.td [] [])
                                )
                            ]
                   )
        ]


experimentDecode : Json.Decode.Decoder Experiment
experimentDecode =
    Json.Decode.map4
        Experiment
        (Json.Decode.field "title" Json.Decode.string)
        (Json.Decode.field "updates" Json.Decode.string)
        (Json.Decode.field "plugins" (Json.Decode.list pluginDecode))
        (Json.Decode.field "comments" Json.Decode.string)


experimentEntriesDecode : Json.Decode.Decoder (List ExperimentEntry)
experimentEntriesDecode =
    Json.Decode.field "experiment_entries" (Json.Decode.list experimentEntryDecode)


experimentEntryDecode : Json.Decode.Decoder ExperimentEntry
experimentEntryDecode =
    Json.Decode.map5
        ExperimentEntry
        (Json.Decode.field "version" Json.Decode.string)
        (Json.Decode.field "timestamp" dateDecode)
        (Json.Decode.field "title" Json.Decode.string)
        (Json.Decode.field "comments" Json.Decode.string)
        (Json.Decode.field "location" Json.Decode.string)


dateDecode : Json.Decode.Decoder Date
dateDecode =
    Json.Decode.string
        |> Json.Decode.andThen
            (\dateString ->
                case Date.fromString dateString of
                    Ok date ->
                        Json.Decode.succeed date

                    Err err ->
                        Json.Decode.fail (toString err)
            )


historyRow : ExperimentEntry -> Html Msg
historyRow entry =
    let
        minute =
            Date.minute entry.date

        second =
            Date.second entry.date
    in
        Html.tr []
            [ Html.td [] [ Html.text entry.version ]
            , Html.td []
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
            , Html.td []
                [ Html.text <|
                    if entry.title == "" then
                        "none"
                    else
                        entry.title
                ]
            , Html.td []
                [ Html.text <|
                    if entry.comments == "" then
                        "none"
                    else
                        entry.comments
                ]
            , Html.td []
                [ Html.button []
                    [ Html.a [ Html.Attributes.href ("download/" ++ entry.location) ] [ Html.text "Download" ] ]
                ]
            , Html.td []
                [ Html.button
                    [ Html.Events.onClick (DeleteExperiment entry.location) ]
                    [ Html.text "Delete" ]
                ]
            ]
