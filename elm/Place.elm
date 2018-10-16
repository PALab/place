port module Place exposing (main)

import Date exposing (Date)
import Dict exposing (Dict)
import Html exposing (Html)
import Html.Attributes
import Html.Events
import Http
import Json.Decode
import Json.Encode
import Process
import Svg
import Svg.Attributes
import Svg.Events
import Task
import Time


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
    , updates : Int
    , plugins : List Plugin
    , comments : String
    }


type alias ExperimentEntry =
    { version : String
    , date : Date
    , title : String
    , comments : String
    , location : String
    , filename : String
    }


type alias Progress =
    { directory : String
    , currentPhase : String
    , currentPlugin : String
    , currentUpdate : Int
    , totalUpdates : Int
    , updateTime : Float
    , pluginProgress : Dict String Json.Decode.Value
    }


type ServerStatus
    = Ready (List ExperimentEntry)
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
    }


start : Flags -> ( Model, Cmd Msg )
start flags =
    let
        model =
            { state = Status
            , experiment =
                { title = ""
                , updates = 1
                , plugins = []
                , comments = ""
                }
            , history = []
            , version = parseVersion flags.version
            }
    in
    update RefreshProgress model


type Msg
    = ChangeExperimentTitle String
    | ChangeExperimentUpdates Int
    | ChangeExperimentComments String
    | UpdateExperimentPlugins Json.Encode.Value
      -- history messages
    | DeleteExperiment String
      -- state machine messages
    | ConfigureNewExperiment
    | CloseNewExperiment
    | StartExperimentButton
    | StartExperimentResponse (Result Http.Error ServerStatus)
    | RefreshProgress
    | RefreshProgressResponse (Result Http.Error ServerStatus)
    | PlaceError String


main : Program Flags Model Msg
main =
    Html.programWithFlags
        { init = start
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
                                    (if data.pythonClassName == "None" then
                                        emptyPlugins

                                     else
                                        newData
                                    )
                                        ++ List.filter
                                            (.pythonModuleName >> (/=) data.pythonModuleName)
                                            model.experiment.plugins
                    in
                    ( { model | experiment = { oldExperiment | plugins = newPlugins } }, Cmd.none )

                Err err ->
                    update (PlaceError (toString err)) model

        DeleteExperiment location ->
            let
                body =
                    Http.jsonBody (locationEncode location)
            in
            ( model, Http.send RefreshProgressResponse <| Http.post "delete/" body serverStatusDecode )

        RefreshProgress ->
            ( model, Http.send RefreshProgressResponse <| Http.get "status/" serverStatusDecode )

        RefreshProgressResponse response ->
            case response of
                Ok status ->
                    case status of
                        Ready history ->
                            ( { model | state = History, history = history }, hidePlugins () )

                        Running progress ->
                            let
                                updatePlugins =
                                    Dict.values <| Dict.map (\a b -> pluginProgress ( a, b )) progress.pluginProgress
                            in
                            { model | state = LiveProgress progress }
                                ! (updatePlugins ++ [ Task.perform (always RefreshProgress) <| Process.sleep <| 500 * Time.millisecond ])

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
                        Ready history ->
                            ( model, Http.send StartExperimentResponse <| Http.get "status/" serverStatusDecode )

                        Running progress ->
                            let
                                updatePlugins =
                                    Dict.values <| Dict.map (\a b -> pluginProgress ( a, b )) progress.pluginProgress
                            in
                            { model | state = LiveProgress progress }
                                ! (updatePlugins ++ [ Task.perform (always RefreshProgress) <| Process.sleep <| 500 * Time.millisecond ])

                        ServerError err ->
                            ( { model | state = Error ("PLACE error: " ++ err) }, Cmd.none )

                        Unknown ->
                            ( { model | state = Error "PLACE unknown status" }, Cmd.none )

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
            Html.div [ Html.Attributes.class "configure-experiment" ]
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
                , Html.button
                    [ Html.Attributes.class "configure-experiment__history-button"
                    , Html.Events.onClick RefreshProgress
                    ]
                    [ Html.text "Show all experiments" ]
                , Html.div [ Html.Attributes.class "configure-experiment__input" ]
                    [ Html.input
                        [ Html.Attributes.value model.experiment.title
                        , Html.Attributes.placeholder "Experiment Title"
                        , Html.Events.onInput ChangeExperimentTitle
                        ]
                        []
                    , Html.br [] []
                    , Html.textarea
                        [ Html.Attributes.value model.experiment.comments
                        , Html.Attributes.placeholder "Comments"
                        , Html.Events.onInput ChangeExperimentComments
                        ]
                        []
                    ]
                ]

        LiveProgress progress ->
            let
                updatesRemaining =
                    progress.totalUpdates - progress.currentUpdate
            in
            Html.div [ Html.Attributes.class "configure-experiment__graphic" ]
                [ placeGraphic progress.currentPhase updatesRemaining progress.updateTime ]

        Refresh ->
            Html.div [ Html.Attributes.id "refreshingView" ]
                [ Html.p [] [ Html.text "Refreshing..." ]
                ]

        Result ->
            Html.div [ Html.Attributes.id "resultView" ]
                [ Html.p [] [ Html.text "You have reached the incomplete Result view" ]
                , Html.button
                    [ Html.Events.onClick RefreshProgress ]
                    [ Html.text "Show all experiments" ]
                ]

        History ->
            Html.div [ Html.Attributes.id "historyView" ]
                [ Html.h2 [] [ Html.text "Experiment History" ]
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
                    , Html.tbody [] <| List.map historyRow model.history
                    ]
                , Html.button
                    [ Html.Events.onClick ConfigureNewExperiment ]
                    [ Html.text "New experiment" ]
                ]

        Error err ->
            Html.div [ Html.Attributes.id "errorView" ]
                [ Html.button
                    [ Html.Events.onClick RefreshProgress ]
                    [ Html.text "Recheck server" ]
                , Html.p [] [ Html.text err ]
                ]


subscriptions : Model -> Sub Msg
subscriptions model =
    Sub.batch [ pluginConfig (\value -> UpdateExperimentPlugins value) ]


serverStatusDecode : Json.Decode.Decoder ServerStatus
serverStatusDecode =
    Json.Decode.field "status" Json.Decode.string
        |> Json.Decode.andThen
            (\status ->
                case status of
                    "Ready" ->
                        Json.Decode.field "history" experimentEntriesDecode
                            |> Json.Decode.andThen (Json.Decode.succeed << Ready)

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
    Json.Decode.map7
        Progress
        (Json.Decode.field "directory" Json.Decode.string)
        (Json.Decode.field "current_phase" Json.Decode.string)
        (Json.Decode.field "current_plugin" Json.Decode.string)
        (Json.Decode.field "current_update" Json.Decode.int)
        (Json.Decode.field "total_updates" Json.Decode.int)
        (Json.Decode.field "update_time" Json.Decode.float)
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
        [ ( "updates", Json.Encode.int experiment.updates )
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
    in
    [ Html.h2 [] [ Html.text "NumPy data array layout" ]
    , Html.table [ Html.Attributes.id "data-table" ] <|
        [ Html.tr []
            (Html.th [] []
                :: Html.th [ Html.Attributes.id "device0" ] [ Html.text "time" ]
                :: allHeadings
            )
        ]
            ++ (case experiment.updates of
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
                            (Html.td [] [ Html.text (toString (experiment.updates - 2)) ]
                                :: List.repeat (numHeadings + 1) (Html.td [] [])
                            )
                        , Html.tr []
                            (Html.td [] [ Html.text (toString (experiment.updates - 1)) ]
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
        (Json.Decode.field "updates" Json.Decode.int)
        (Json.Decode.field "plugins" (Json.Decode.list pluginDecode))
        (Json.Decode.field "comments" Json.Decode.string)


experimentEntriesDecode : Json.Decode.Decoder (List ExperimentEntry)
experimentEntriesDecode =
    Json.Decode.field "experiment_entries" (Json.Decode.list experimentEntryDecode)


experimentEntryDecode : Json.Decode.Decoder ExperimentEntry
experimentEntryDecode =
    Json.Decode.map6
        ExperimentEntry
        (Json.Decode.field "version" Json.Decode.string)
        (Json.Decode.field "timestamp" (Json.Decode.oneOf [ posixEpochDecode, dateDecode ]))
        (Json.Decode.field "title" Json.Decode.string)
        (Json.Decode.field "comments" Json.Decode.string)
        (Json.Decode.field "location" Json.Decode.string)
        (Json.Decode.field "filename" Json.Decode.string)


posixEpochDecode : Json.Decode.Decoder Date
posixEpochDecode =
    Json.Decode.int
        |> Json.Decode.andThen
            (toFloat >> ((*) Time.millisecond >> Date.fromTime >> Json.Decode.succeed))


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
            [ Html.Attributes.class "table__data--download" ]
            [ Html.button []
                [ Html.a [ Html.Attributes.href ("download/" ++ entry.location) ] [ Html.text entry.filename ]
                ]
            ]
        , Html.td
            [ Html.Attributes.class "table__data--delete" ]
            [ Html.button
                [ Html.Events.onClick (DeleteExperiment entry.location) ]
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
            [ Svg.Attributes.class startClass
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
            , Svg.Events.onClick StartExperimentButton
            ]
            []
        , Svg.text_
            [ Svg.Attributes.class "place-progress__text"
            , Svg.Attributes.textAnchor "middle"
            , Svg.Attributes.x "48"
            , Svg.Attributes.y "65"
            , Svg.Events.onClick StartExperimentButton
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
