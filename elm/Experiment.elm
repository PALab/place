module Experiment exposing (Model, Msg(..), default, view, update)

import Process
import Task
import Time
import Http
import Html exposing (Html)
import Html.Attributes
import Html.Events
import Dict exposing (Dict)
import Json.Encode
import Json.Decode
import Plugin


type alias Model =
    { status : Status
    , plugins : List Plugin.Model
    , updates : Int
    , comments : String
    , ready : String
    }


default : Model
default =
    { status = New
    , plugins = []
    , updates = 1
    , comments = ""
    , ready = "Loading"
    }


type Status
    = New
    | Started
    | Running
    | Complete
    | Error


type Msg
    = ChangeUpdates String
    | ChangeComments String
    | PostResponse (Result Http.Error (Dict String String))
    | UpdatePlugins Json.Encode.Value
    | StartExperiment
    | GetStatus ()
    | GetStatusResponse (Result Http.Error (Dict String String))


update : Msg -> Model -> ( Model, Cmd Msg )
update msg experiment =
    case msg of
        ChangeUpdates newValue ->
            ( { experiment | updates = Result.withDefault 1 <| String.toInt newValue }, Cmd.none )

        ChangeComments newValue ->
            ( { experiment | comments = newValue }, Cmd.none )

        UpdatePlugins jsonValue ->
            case Json.Decode.decodeValue (Json.Decode.list Plugin.decode) jsonValue of
                Ok newData ->
                    let
                        newState =
                            case List.head newData of
                                Nothing ->
                                    experiment

                                Just data ->
                                    { experiment
                                        | plugins =
                                            ((if data.className == "None" then
                                                emptyPlugins
                                              else
                                                newData
                                             )
                                                ++ List.filter
                                                    (.module_name >> ((/=) data.module_name))
                                                    experiment.plugins
                                            )
                                    }
                    in
                        ( newState, Cmd.none )

                Err err ->
                    ( { experiment | status = Error }, Cmd.none )

        PostResponse (Ok dict) ->
            case Dict.get "status" dict of
                Just string ->
                    update (GetStatus ()) { experiment | comments = string }

                Nothing ->
                    ( { experiment | comments = "no \"status\" key in dictionary" }, Cmd.none )

        PostResponse (Err err) ->
            ( { experiment | comments = toString err }, Cmd.none )

        StartExperiment ->
            let
                body =
                    Http.jsonBody (encode experiment)
            in
                ( experiment
                , Http.send PostResponse <|
                    Http.post "submit/" body <|
                        Json.Decode.dict Json.Decode.string
                )

        GetStatus () ->
            ( experiment
            , Http.send GetStatusResponse <|
                Http.get "status/" <|
                    Json.Decode.dict Json.Decode.string
            )

        GetStatusResponse (Ok dict) ->
            case Dict.get "status" dict of
                Just string ->
                    let
                        new_experiment =
                            { experiment | ready = string }
                    in
                        if new_experiment.ready == "Ready" then
                            ( new_experiment, Cmd.none )
                        else
                            ( new_experiment, Task.perform GetStatus (Process.sleep (500 * Time.millisecond)) )

                Nothing ->
                    ( { experiment | comments = "no \"status\" key in dictionary" }, Cmd.none )

        GetStatusResponse (Err err) ->
            ( { experiment | ready = toString err }, Cmd.none )


view : Model -> Html Msg
view model =
    if model.ready == "Ready" then
        readyView model
    else
        loaderView model


readyView : Model -> Html Msg
readyView model =
    Html.div []
        [ startExperimentView model
        , readyBox model
        , commentBox model
        ]


loaderView : Model -> Html Msg
loaderView model =
    Html.div []
        [ Html.p [ Html.Attributes.class "loaderTitle" ] [ Html.text "PLACE is busy" ]
        , Html.div [ Html.Attributes.class "loader" ] []
        , Html.p [ Html.Attributes.class "progresstext" ] [ Html.text model.ready ]
        , readyBox model
        , commentBox model
        ]


startExperimentView : Model -> Html Msg
startExperimentView model =
    if model.ready == "Ready" then
        Html.p []
            [ Html.button
                [ Html.Attributes.id "start-button"
                , Html.Events.onClick StartExperiment
                ]
                [ Html.text "Start" ]
            , Html.input
                [ Html.Attributes.id "update-number"
                , Html.Attributes.value <| toString model.updates
                , Html.Attributes.type_ "number"
                , Html.Attributes.min "1"
                , Html.Events.onInput ChangeUpdates
                ]
                []
            , Html.span [ Html.Attributes.id "update-text" ]
                [ if model.updates == 1 then
                    Html.text "update"
                  else
                    Html.text "updates"
                ]
            ]
    else
        Html.text ""


readyBox : Model -> Html Msg
readyBox experiment =
    Html.p []
        [ Html.text ("PLACE status: " ++ experiment.ready) ]


commentBox : Model -> Html Msg
commentBox experiment =
    Html.p []
        [ Html.text "Comments:"
        , Html.br [] []
        , Html.textarea
            [ Html.Attributes.rows 3
            , Html.Attributes.cols 60
            , Html.Attributes.value experiment.comments
            , Html.Events.onInput ChangeComments
            ]
            []
        , Html.br [] []
        ]


errorPlotView : Html Msg
errorPlotView =
    Html.strong [] [ Html.text "There was an error!" ]


experimentShowData : Model -> List (Html Msg)
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


encode : Model -> Json.Encode.Value
encode experiment =
    Json.Encode.object
        [ ( "status", Json.Encode.string <| toString experiment.status )
        , ( "plugins", Json.Encode.list <| List.map Plugin.encode experiment.plugins )
        , ( "updates", Json.Encode.int experiment.updates )
        , ( "comments", Json.Encode.string experiment.comments )
        , ( "ready", Json.Encode.string experiment.ready )
        ]


decode : Json.Decode.Decoder Model
decode =
    Json.Decode.map5
        Model
        (Json.Decode.field "status" decodeStatus)
        (Json.Decode.field "plugins" (Json.Decode.list Plugin.decode))
        (Json.Decode.field "updates" Json.Decode.int)
        (Json.Decode.field "comments" Json.Decode.string)
        (Json.Decode.field "ready" Json.Decode.string)


decodeStatus : Json.Decode.Decoder Status
decodeStatus =
    Json.Decode.string |> Json.Decode.andThen fromStringStatus


fromStringStatus : String -> Json.Decode.Decoder Status
fromStringStatus status =
    case status of
        "New" ->
            Json.Decode.succeed New

        "Started" ->
            Json.Decode.succeed Started

        "Running" ->
            Json.Decode.succeed Running

        "Complete" ->
            Json.Decode.succeed Complete

        "Error" ->
            Json.Decode.succeed Error

        otherwise ->
            Json.Decode.fail "Invalid status string"


emptyPlugins : List Plugin.Model
emptyPlugins =
    []
