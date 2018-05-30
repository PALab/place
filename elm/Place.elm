port module Place exposing (main)

import String exposing (left, dropLeft)
import Html exposing (Html)
import Html.Events
import Html.Attributes
import Http exposing (jsonBody)
import Json.Decode
import Json.Encode
import Helpers exposing (..)


type alias Experiment =
    { modules : List Module
    , directory : String
    , updates : Int
    , comments : String
    , plotData : Html Msg
    , showJson : Bool
    , showData : Bool
    , version : String
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
        [ Html.button
            [ Html.Attributes.id "start-button"
            , Html.Events.onClick StartExperiment
            ]
            [ Html.text "Start experiment" ]
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
    | PostResponse (Result Http.Error String)
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
                    let
                        newState =
                            experimentErrorState err
                    in
                        ( { newState | version = experiment.version }, Cmd.none )

                Ok new ->
                    ( updateModules new experiment
                    , Cmd.none
                    )

        PostResponse (Ok string) ->
            ( { experiment | comments = string }, Cmd.none )

        PostResponse (Err err) ->
            ( { experiment | comments = toString err }, Cmd.none )

        StartExperiment ->
            ( experiment, sendExperiment PostResponse (postExperiment experiment) )

        ServerData data ->
            let
                tag =
                    left 6 data

                msg =
                    dropLeft 6 data
            in
                case tag of
                    "<VERS>" ->
                        if
                            (major experiment.version == major msg)
                                && (minor experiment.version == minor msg)
                                && (patch experiment.version == patch msg)
                        then
                            ( experiment, Cmd.none )
                        else
                            let
                                url =
                                    "../" ++ msg ++ "/index.html"

                                oldLinkButton =
                                    Html.a
                                        [ Html.Attributes.href url
                                        , Html.Attributes.id "start-button-disconnected"
                                        ]
                                        [ Html.text ("Goto " ++ msg) ]

                                oldLinkText =
                                    "Your version of the PLACE server is "
                                        ++ "older than this web app. Please update "
                                        ++ "your server or use the 'Goto "
                                        ++ msg
                                        ++ "' button to switch to the older version "
                                        ++ "of the web app."
                            in
                                ( { experiment
                                    | comments = oldLinkText
                                    , plotData = oldLinkButton
                                  }
                                , Cmd.none
                                )

                    "<CLOS>" ->
                        ( experiment, Cmd.none )

                    "<PLOT>" ->
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

                    otherwise ->
                        let
                            newState =
                                experimentErrorState ("unknown server command: " ++ data)
                        in
                            ( { newState | version = experiment.version }, Cmd.none )


sendExperiment : (Result Http.Error String -> Msg) -> Http.Request String -> Cmd Msg
sendExperiment msg req =
    Http.send msg req


postExperiment : Experiment -> Http.Request String
postExperiment experiment =
    Http.post "start/" (jsonBody (makeJsonExperiment experiment)) Json.Decode.string


subscriptions : Experiment -> Sub Msg
subscriptions experiment =
    Sub.batch [ jsonData UpdateModules ]


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
        makeJsonExperiment experiment


makeJsonExperiment : Experiment -> Json.Encode.Value
makeJsonExperiment experiment =
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


main : Program Flags Experiment Msg
main =
    Html.programWithFlags
        { init = \flags -> ( { experimentDefaultState | version = flags.version }, Cmd.none )
        , view = \model -> Html.div [] (view model)
        , update = update
        , subscriptions = subscriptions
        }


type alias Flags =
    { version : String }


experimentDefaultState : Experiment
experimentDefaultState =
    { modules = []
    , directory = "/tmp/place_tmp"
    , updates = 1
    , comments = ""
    , plotData = Html.text ""
    , showJson = False
    , showData = False
    , version = "0.0.0"
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
    , version = "0.0.0"
    }


headToInt : Maybe (List String) -> Int
headToInt ls =
    Maybe.withDefault 0
        (ls |> Maybe.andThen List.head |> Maybe.andThen (Result.toMaybe << String.toInt))


major : String -> Int
major str =
    Just (String.split "." str) |> headToInt


minor : String -> Int
minor str =
    List.tail (String.split "." str) |> headToInt


patch : String -> Int
patch str =
    List.tail (String.split "." str) |> Maybe.andThen List.tail |> headToInt
