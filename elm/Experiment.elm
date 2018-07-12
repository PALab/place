port module Experiment exposing (Model, Msg(..), init, view, update)

import Process
import Task
import Time
import Dict exposing (Dict)
import Http
import Html exposing (Html)
import Html.Attributes
import Html.Events
import Json.Encode
import Json.Decode
import Plugin
import Status exposing (Status, Progress)


port pluginProgress : ( String, Json.Encode.Value ) -> Cmd msg


init : Model
init =
    Model Status.Unknown "1" [] "Unnamed Experiment" "" 0 ""


type alias Model =
    { status : Status
    , updates : String
    , plugins : List Plugin.Model
    , title : String
    , comments : String
    , currentPlotNumber : Int

    --, hinted : Maybe Point
    , rawJson : String
    }


type Msg
    = ChangeUpdates String
    | UpdatePlugins Json.Encode.Value
    | ChangeTitle String
    | ChangeComments String
    | GetStatus
    | GetStatusResponse (Result Http.Error Status)
    | Post
      --| ShowChartValue (Maybe Point)
    | NextPlot
    | PrevPlot


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        ChangeUpdates newValue ->
            ( { model | updates = newValue }, Cmd.none )

        UpdatePlugins jsonValue ->
            case Json.Decode.decodeValue (Json.Decode.list Plugin.decode) jsonValue of
                Ok newData ->
                    let
                        newPlugins =
                            case List.head newData of
                                Nothing ->
                                    model.plugins

                                Just data ->
                                    ((if data.pythonClassName == "None" then
                                        emptyPlugins
                                      else
                                        newData
                                     )
                                        ++ List.filter
                                            (.pythonModuleName >> ((/=) data.pythonModuleName))
                                            model.plugins
                                    )
                    in
                        ( { model | plugins = newPlugins }, Cmd.none )

                Err err ->
                    ( { model | status = Status.Error err }, Cmd.none )

        ChangeTitle newValue ->
            ( { model | title = newValue }, Cmd.none )

        ChangeComments newValue ->
            ( { model | comments = newValue }, Cmd.none )

        GetStatus ->
            ( model, Http.send GetStatusResponse <| Http.get "status/" Status.decode )

        GetStatusResponse (Ok (Status.Running progress)) ->
            let
                updatePlugins =
                    Dict.values <| Dict.map (\a b -> pluginProgress ( a, b )) progress.pluginProgress
            in
                { model | status = Status.Running progress, rawJson = toString progress.pluginProgress }
                    ! (updatePlugins
                        ++ [ Task.perform (always GetStatus) <| Process.sleep <| 500 * Time.millisecond ]
                      )

        GetStatusResponse (Ok status) ->
            ( { model | status = status }, Cmd.none )

        GetStatusResponse (Err err) ->
            ( { model | status = Status.Error (toString err) }, Cmd.none )

        Post ->
            let
                body =
                    Http.jsonBody (encode model)
            in
                ( model, Http.send GetStatusResponse <| Http.post "submit/" body Status.decode )

        {-
           ShowChartValue newValue ->
               ( { model | hinted = newValue }, Cmd.none )
        -}
        PrevPlot ->
            {-
               case model.status of
                   Status.Running progress ->
                       case List.head progress.p pluginProgressluginProgress of
                           Nothing ->
                               ( model, Cmd.none )

                           Just pluginPlot ->
                               ( { model | currentPlotNumber = (model.currentPlotNumber - 1) % (List.length pluginPlot.plots) }, Cmd.none )

                   otherwise ->
            -}
            ( model, Cmd.none )

        NextPlot ->
            {-
               case model.status of
                   Status.Running progress ->
                       case List.head progress.pluginProgress of
                           Nothing ->
                               ( model, Cmd.none )

                           Just pluginPlot ->
                               ( { model | currentPlotNumber = (model.currentPlotNumber + 1) % (List.length pluginPlot.plots) }, Cmd.none )

                   otherwise ->
            -}
            ( model, Cmd.none )


view : Model -> Html Msg
view model =
    Html.div [] <|
        case model.status of
            Status.Ready ->
                [ startExperimentView model, inputsView model ]

            Status.Running percentage ->
                [ liveplot model, statusView model ]

            --    ++ [ Html.p [] [ Html.text model.rawJson ] ]
            otherwise ->
                [ statusView model ]


startExperimentView : Model -> Html Msg
startExperimentView model =
    Html.div [] <|
        [ (case model.status of
            Status.Ready ->
                Html.button
                    [ Html.Attributes.id "start-button"
                    , Html.Events.onClick Post
                    ]
                    [ Html.text "Start" ]

            Status.Running progress ->
                Html.button
                    [ Html.Attributes.id "start-button-inactive" ]
                    [ Html.text <| toString (toFloat progress.currentUpdate / toFloat progress.totalUpdates) ]

            otherwise ->
                Html.button
                    [ Html.Attributes.id "start-button-inactive" ]
                    [ Html.text "Please wait" ]
          )
        , Html.p [ Html.Attributes.id "updates-p" ]
            [ Html.span [ Html.Attributes.id "update-text" ] [ Html.text "Updates: " ]
            , Html.input
                [ Html.Attributes.id "updateNumber"
                , Html.Attributes.value model.updates
                , Html.Events.onInput ChangeUpdates
                ]
                []
            ]
        ]
            ++ (case String.toInt model.updates of
                    Ok _ ->
                        []

                    Err error_msg ->
                        [ Html.br [] [], Html.span [ Html.Attributes.class "error-text" ] [ Html.text error_msg ] ]
               )


statusView : Model -> Html msg
statusView model =
    Html.div [] <|
        case model.status of
            Status.Running progress ->
                let
                    percent =
                        round <| 100 * (toFloat progress.currentUpdate / toFloat progress.totalUpdates)
                in
                    [ Html.p [] [ Html.text <| "Experiment " ++ toString percent ++ "% complete" ]
                    , Html.p [] [ Html.text <| "Phase: " ++ progress.currentPhase ]
                    , Html.p [] [ Html.text <| "Plugin: " ++ progress.currentPlugin ]
                    ]

            otherwise ->
                [ Html.text <| toString model.status ]


inputsView : Model -> Html Msg
inputsView model =
    Html.p []
        [ Html.text "Title: "
        , Html.input [ Html.Attributes.value model.title, Html.Events.onInput ChangeTitle ] []
        , Html.br [] []
        , Html.text "Comments:"
        , Html.br [] []
        , Html.textarea
            [ Html.Attributes.id "commentsBox"
            , Html.Attributes.rows 3
            , Html.Attributes.value model.comments
            , Html.Events.onInput ChangeComments
            ]
            []
        , Html.br [] []
        ]


liveplot : Model -> Html Msg
liveplot model =
    {-
       case model.status of
           Status.Running progress ->
               case List.head progress.pluginProgress of
                   Nothing ->
                       Html.text ""

                   Just pluginPlots ->
                       case List.head (List.drop model.currentPlotNumber pluginPlots.plots) of
                           Nothing ->
                               Html.text ""

                           Just plot ->
                               Html.div
                                   [ Html.Attributes.id "experimentLivePlot"
                                   , Html.Attributes.class "clearfix"
                                   ]
                                   [ Html.button
                                       [ Html.Attributes.id "prevPlotButton"
                                       , Html.Events.onClick PrevPlot
                                       ]
                                       [ Html.text "<" ]
                                   , Html.button
                                       [ Html.Attributes.id "nextPlotButton"
                                       , Html.Events.onClick NextPlot
                                       ]
                                       [ Html.text ">" ]
                                   , drawPlot model plot
                                   ]

           otherwise ->
    -}
    Html.text ""



{-
   drawPlot : Model -> Status.Plot -> Html Msg
   drawPlot model plot =
       case plot of
           Status.DataPlot chart ->
               let
                   colorArray =
                       Array.fromList [ Colors.blue, Colors.green, Colors.red ]
               in
                   case List.length chart.series of
                       0 ->
                           Html.text ""

                       n ->
                           drawChart model chart.title chart.xAxis chart.yAxis colorArray chart.series

           Status.PngPlot img ->
               Html.img
                   [ Html.Attributes.src img.src
                   , Html.Attributes.alt img.alt
                   , Html.Attributes.height 400
                   , Html.Attributes.width 700
                   ]
                   []


   drawChart : Model -> String -> String -> String -> Array Color.Color -> List Status.Series -> Html Msg
   drawChart model title xAxisTitle yAxisTitle colors allSeries =
       let
           allLines =
               List.indexedMap
                   (\index series ->
                       case Array.get (index % 3) colors of
                           Just color ->
                               LineChart.line color Dots.none series.name series.points

                           Nothing ->
                               LineChart.line Color.blue Dots.none series.name series.points
                   )
                   allSeries

           chartConfig =
               { y = Axis.default 400 yAxisTitle .y
               , x = Axis.default 700 xAxisTitle .x
               , container = Container.default title
               , interpolation = Interpolation.default
               , intersection = Intersection.default
               , legends = Legends.default
               , events = Events.hoverOne ShowChartValue
               , junk =
                   Junk.hoverOne model.hinted
                       [ ( xAxisTitle, toString << .x )
                       , ( yAxisTitle, toString << .y )
                       ]
               , grid = Grid.default
               , area = Area.default
               , line = Line.default
               , dots = Dots.default
               }
       in
           Html.div [ Html.Attributes.id "plotDiv" ]
               [ Html.p [ Html.Attributes.class "plotTitle" ] [ Html.text title ]
               , LineChart.viewCustom chartConfig allLines
               ]
-}


errorPlotView : Html Msg
errorPlotView =
    Html.strong [] [ Html.text "There was an error!" ]


experimentShowData : Model -> List (Html Msg)
experimentShowData model =
    let
        makeHeading =
            \num name ->
                Html.th [ Html.Attributes.id ("device" ++ toString num) ] [ Html.text name ]

        makeModuleHeadings =
            \device num -> List.map (makeHeading num) device.dataRegister

        allHeadings =
            List.concat <|
                List.map2 makeModuleHeadings (List.sortBy .priority model.plugins) <|
                    List.map (\x -> x % 3 + 1) <|
                        List.range 1 (List.length model.plugins)

        numHeadings =
            List.length allHeadings

        updates =
            intDefault "1" model.updates
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


encode : Model -> Json.Encode.Value
encode model =
    Json.Encode.object
        [ ( "status", Json.Encode.string <| toString model.status )
        , ( "updates", Json.Encode.int <| intDefault "1" model.updates )
        , ( "plugins", Json.Encode.list <| List.map Plugin.encode model.plugins )
        , ( "title", Json.Encode.string model.comments )
        , ( "comments", Json.Encode.string model.comments )
        ]


decode : Json.Decode.Decoder Model
decode =
    Json.Decode.map7
        Model
        (Json.Decode.field "status" Status.decode)
        (Json.Decode.field "updates" Json.Decode.string)
        (Json.Decode.field "plugins" (Json.Decode.list Plugin.decode))
        (Json.Decode.field "title" Json.Decode.string)
        (Json.Decode.field "comments" Json.Decode.string)
        (Json.Decode.succeed 0)
        (Json.Decode.succeed "")


emptyPlugins : List Plugin.Model
emptyPlugins =
    []


intDefault : String -> String -> Int
intDefault default value =
    case String.toInt value of
        Ok int ->
            int

        Err _ ->
            Result.withDefault 0 (String.toInt default)
