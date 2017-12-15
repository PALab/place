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
    , showData : Bool
    , connected : Bool
    }


port jsonData : (Json.Encode.Value -> msg) -> Sub msg


view : Experiment -> List (Html Msg)
view experiment =
    Html.h1 [] [ Html.text "PLACE interface" ]
        :: startExperimentView experiment
        :: directoryBox experiment
        :: commentBox experiment
        :: buttonsView experiment
        :: jsonView experiment
        ++ dataTable experiment


startExperimentView : Experiment -> Html Msg
startExperimentView experiment =
    Html.p []
        [ (if experiment.connected then
            Html.button
                [ Html.Attributes.id "start-button"
                , Html.Events.onClick StartExperiment
                ]
                [ Html.text "Start experiment" ]
           else
            Html.button
                [ Html.Attributes.id "start-button-disconnected" ]
                [ Html.text "Not connected" ]
          )
        , Html.input
            [ Html.Attributes.id "update-number"
            , Html.Attributes.value <| toString experiment.updates
            , Html.Attributes.type_ "number"
            , Html.Attributes.min "1"
            , Html.Events.onInput ChangeUpdates
            ]
            []
        , Html.span [ Html.Attributes.id "update-text" ]
            [ if experiment.updates == 1 then
                Html.text "update"
              else
                Html.text "updates"
            ]
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


buttonsView : Experiment -> Html Msg
buttonsView experiment =
    Html.p []
        [ (if experiment.showJson then
            Html.button [ Html.Events.onClick <| ChangeShowJson False ] [ Html.text "Hide JSON" ]
           else
            Html.button [ Html.Events.onClick <| ChangeShowJson True ] [ Html.text "Show JSON" ]
          )
        , (if experiment.showData then
            Html.button [ Html.Events.onClick <| ChangeShowData False ] [ Html.text "Hide Data Layout" ]
           else
            Html.button [ Html.Events.onClick <| ChangeShowData True ] [ Html.text "Show Data Layout" ]
          )
        ]


dataTable : Experiment -> List (Html Msg)
dataTable experiment =
    let
        makeHeading =
            \num name ->
                Html.th [ Html.Attributes.id ("device" ++ toString num) ] [ Html.text name ]

        makeModuleHeadings =
            \device num -> List.map (makeHeading num) device.dataRegister

        allHeadings =
            List.concat <|
                List.map2 makeModuleHeadings (List.sortBy .priority experiment.modules) <|
                    List.map (\x -> x % 3 + 1) <|
                        List.range 1 (List.length experiment.modules)

        numHeadings =
            List.length allHeadings
    in
        if experiment.showData then
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
        else
            [ Html.text "" ]


jsonView : Experiment -> List (Html Msg)
jsonView experiment =
    if experiment.showJson then
        [ Html.h2 [] [ Html.text "JSON data to be sent to PLACE" ]
        , Html.pre [] [ Html.text <| encodeExperiment 4 experiment ]
        ]
    else
        [ Html.text "" ]


type Msg
    = ChangeDirectory String
    | ChangeUpdates String
    | ChangeShowJson Bool
    | ChangeShowData Bool
    | ChangeComments String
    | UpdateModules Json.Encode.Value
    | StartExperiment
    | ServerData String


update : Msg -> Experiment -> ( Experiment, Cmd Msg )
update msg experiment =
    case msg of
        ChangeDirectory newValue ->
            ( { experiment | directory = newValue }, Cmd.none )

        ChangeUpdates newValue ->
            ( { experiment | updates = Result.withDefault 1 <| String.toInt newValue }, Cmd.none )

        ChangeShowJson newValue ->
            ( { experiment | showJson = newValue }, Cmd.none )

        ChangeShowData newValue ->
            ( { experiment | showData = newValue }, Cmd.none )

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
            ( experiment, WebSocket.send socket <| encodeExperiment 0 experiment )

        ServerData "server_connected" ->
            ( { experiment | connected = True }, Cmd.none )

        ServerData "server_closed" ->
            ( { experiment | connected = False }, Cmd.none )

        ServerData data ->
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
    Sub.batch [ jsonData UpdateModules, WebSocket.listen socket ServerData ]


socket =
    "ws://localhost:9130"


type alias Module =
    { module_name : String
    , className : String
    , priority : Int
    , dataRegister : List String
    , config : Json.Encode.Value
    }


decoder : Json.Encode.Value -> Result String (List Module)
decoder =
    Json.Decode.decodeValue <|
        Json.Decode.list <|
            Json.Decode.map5
                Module
                (Json.Decode.field "module_name" Json.Decode.string)
                (Json.Decode.field "class_name" Json.Decode.string)
                (Json.Decode.field "priority" Json.Decode.int)
                (Json.Decode.field "data_register" (Json.Decode.list Json.Decode.string))
                (Json.Decode.field "config" Json.Decode.value)


encoder : List Module -> Json.Encode.Value
encoder modules =
    Json.Encode.list <| List.map singleEncoder modules


singleEncoder : Module -> Json.Encode.Value
singleEncoder module_ =
    Json.Encode.object
        [ ( "module_name", Json.Encode.string module_.module_name )
        , ( "class_name", Json.Encode.string module_.className )
        , ( "priority", Json.Encode.int module_.priority )
        , ( "config", module_.config )
        ]


encodeExperiment : Int -> Experiment -> String
encodeExperiment indent experiment =
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
            if data.className == "None" then
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
        , view = \model -> Html.div [] (view model)
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
    , showData = False
    , connected = False
    }


experimentErrorState : String -> Experiment
experimentErrorState err =
    { modules = []
    , directory = ""
    , updates = 0
    , comments = err
    , plotData = Html.strong [] [ Html.text "There was an error!" ]
    , showJson = False
    , showData = False
    , connected = False
    }
