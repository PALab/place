port module Place exposing (main)

import Html exposing (Html)
import Html.Events
import Html.Attributes
import Json.Decode
import Json.Encode
import WebSocket
import Helpers exposing (..)


type alias Experiment =
    { modules : List Module
    , directory : String
    , updates : Int
    , comments : String
    , plotData : Html Msg
    , showJson : Bool
    }


port jsonData : (Json.Encode.Value -> msg) -> Sub msg


view : Experiment -> Html Msg
view experiment =
    Html.div [] <|
        Html.h1 [] [ Html.text "PLACE interface" ]
            :: startExperimentView
            :: inputUpdates experiment
            :: directoryBox experiment
            :: commentBox experiment
            :: plotBox experiment
            ++ jsonView experiment


startExperimentView : Html Msg
startExperimentView =
    Html.p []
        [ Html.button
            [ Html.Events.onClick StartExperiment
            ]
            [ Html.text "Start experiment" ]
        ]


inputUpdates : Experiment -> Html Msg
inputUpdates experiment =
    Html.p []
        [ Html.text "Number of updates (steps): "
        , Html.input
            [ Html.Attributes.value <| toString experiment.updates
            , Html.Attributes.type_ "number"
            , Html.Events.onInput ChangeUpdates
            ]
            []
        , Html.br [] []
        ]


directoryBox : Experiment -> Html Msg
directoryBox experiment =
    Html.p []
        [ Html.text "Save directory: "
        , Html.input
            [ Html.Attributes.value experiment.directory
            , Html.Events.onInput ChangeDirectory
            ]
            []
        ]


commentBox : Experiment -> Html Msg
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


plotBox : Experiment -> List (Html Msg)
plotBox experiment =
    [ experiment.plotData
    , Html.br [] []
    ]


jsonView : Experiment -> List (Html Msg)
jsonView experiment =
    if experiment.showJson then
        [ Html.button [ Html.Events.onClick <| ChangeShowJson False ] [ Html.text "Hide JSON" ]
        , Html.br [] []
        , Html.pre [] [ Html.text <| encodeScan 4 experiment ]
        ]
    else
        [ Html.button [ Html.Events.onClick <| ChangeShowJson True ] [ Html.text "Show JSON" ] ]


type Msg
    = ChangeDirectory String
    | ChangeUpdates String
    | ChangeShowJson Bool
    | ChangeComments String
    | UpdateModules Json.Encode.Value
    | StartExperiment
    | Plot String


update : Msg -> Experiment -> ( Experiment, Cmd Msg )
update msg experiment =
    case msg of
        ChangeDirectory newValue ->
            ( { experiment | directory = newValue }, Cmd.none )

        ChangeUpdates newValue ->
            ( { experiment | updates = Result.withDefault 1 <| String.toInt newValue }, Cmd.none )

        ChangeShowJson newValue ->
            ( { experiment | showJson = newValue }, Cmd.none )

        ChangeComments newValue ->
            ( { experiment | comments = newValue }, Cmd.none )

        UpdateModules jsonValue ->
            case decoder jsonValue of
                Err err ->
                    ( experimentErrorState err, Cmd.none )

                Ok new ->
                    ( updateModules new experiment
                    , Cmd.none
                    )

        StartExperiment ->
            ( experiment, WebSocket.send socket <| encodeScan 0 experiment )

        Plot data ->
            ( { experiment
                | plotData =
                    Html.iframe
                        [ Html.Attributes.srcdoc data
                        , Html.Attributes.property "scrolling" (Json.Encode.string "no")
                        ]
                        []
              }
            , Cmd.none
            )


subscriptions : Experiment -> Sub Msg
subscriptions experiment =
    Sub.batch [ jsonData UpdateModules, WebSocket.listen socket Plot ]


socket =
    "ws://localhost:9130"


type alias Module =
    { module_name : String
    , class_name : String
    , priority : Int
    , config : Json.Encode.Value
    }


decoder : Json.Encode.Value -> Result String (List Module)
decoder =
    Json.Decode.decodeValue <|
        Json.Decode.list <|
            Json.Decode.map4
                Module
                (Json.Decode.field "module_name" Json.Decode.string)
                (Json.Decode.field "class_name" Json.Decode.string)
                (Json.Decode.field "priority" Json.Decode.int)
                (Json.Decode.field "config" Json.Decode.value)


encoder : List Module -> Json.Encode.Value
encoder modules =
    Json.Encode.list <| List.map singleEncoder modules


singleEncoder : Module -> Json.Encode.Value
singleEncoder module_ =
    Json.Encode.object
        [ ( "module_name", Json.Encode.string module_.module_name )
        , ( "class_name", Json.Encode.string module_.class_name )
        , ( "priority", Json.Encode.int module_.priority )
        , ( "config", module_.config )
        ]


encodeScan : Int -> Experiment -> String
encodeScan indent experiment =
    Json.Encode.encode indent <|
        Json.Encode.object
            [ ( "updates", Json.Encode.int experiment.updates )
            , ( "directory", Json.Encode.string experiment.directory )
            , ( "comments", Json.Encode.string experiment.comments )
            , ( "modules", encoder experiment.modules )
            ]


updateModules : List Module -> Experiment -> Experiment
updateModules newData experiment =
    case List.head newData of
        Nothing ->
            experiment

        Just data ->
            if data.class_name == "None" then
                { experiment
                    | modules =
                        List.filter
                            (notModule data.module_name)
                            experiment.modules
                }
            else
                { experiment
                    | modules =
                        (newData
                            ++ List.filter
                                (notModule data.module_name)
                                experiment.modules
                        )
                }


notModule : String -> Module -> Bool
notModule moduleName module_ =
    moduleName /= module_.module_name


main : Program Never Experiment Msg
main =
    Html.program
        { init = ( experimentDefaultState, Cmd.none )
        , view = view
        , update = update
        , subscriptions = subscriptions
        }


experimentDefaultState : Experiment
experimentDefaultState =
    { modules = []
    , directory = "/tmp/place_tmp"
    , updates = 1
    , comments = ""
    , plotData = Html.text ""
    , showJson = False
    }


experimentErrorState : String -> Experiment
experimentErrorState err =
    { modules = []
    , directory = ""
    , updates = 0
    , comments = err
    , plotData = Html.strong [] [ Html.text "There was an error!" ]
    , showJson = True
    }
