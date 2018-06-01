port module Place exposing (main)

import String exposing (left, dropLeft)
import Time
import Task
import Process
import Html exposing (Html)
import Html.Attributes
import Http exposing (jsonBody)
import Json.Decode
import Json.Encode
import Place.Model exposing (Model, Msg(..), PlacePlugin)
import Place.View exposing (view)
import Place.Encode


port jsonData : (Json.Encode.Value -> msg) -> Sub msg


update : Msg -> Model -> ( Model, Cmd Msg )
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
            update (GetStatus ()) { experiment | comments = string }

        PostResponse (Err err) ->
            ( { experiment | comments = toString err }, Cmd.none )

        StartExperiment ->
            ( experiment, sendExperiment PostResponse (postExperiment experiment) )

        GetStatus () ->
            ( experiment, Http.send StatusResponse (Http.getString "status/") )

        StatusResponse (Ok string) ->
            let
                new_experiment =
                    { experiment | ready = string }
            in
                if string == "Ready" then
                    ( new_experiment, Cmd.none )
                else
                    ( new_experiment, Task.perform GetStatus (Process.sleep (500 * Time.millisecond)) )

        StatusResponse (Err err) ->
            ( { experiment | comments = toString err }, Cmd.none )

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


postExperiment : Model -> Http.Request String
postExperiment experiment =
    Http.post "start/" (jsonBody (Place.Encode.toJson experiment)) Json.Decode.string


subscriptions : Model -> Sub Msg
subscriptions experiment =
    Sub.batch [ jsonData UpdateModules ]


decoder : Json.Encode.Value -> Result String (List PlacePlugin)
decoder =
    Json.Decode.decodeValue <|
        Json.Decode.list <|
            Json.Decode.map5
                PlacePlugin
                (Json.Decode.field "module_name" Json.Decode.string)
                (Json.Decode.field "class_name" Json.Decode.string)
                (Json.Decode.field "priority" Json.Decode.int)
                (Json.Decode.field "data_register" (Json.Decode.list Json.Decode.string))
                (Json.Decode.field "config" Json.Decode.value)


updateModules : List PlacePlugin -> Model -> Model
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


notModule : String -> PlacePlugin -> Bool
notModule moduleName module_ =
    moduleName /= module_.module_name


main : Program Flags Model Msg
main =
    Html.programWithFlags
        { init = \flags -> update (GetStatus ()) { experimentDefaultState | version = flags.version }
        , view = view
        , update = update
        , subscriptions = subscriptions
        }


type alias Flags =
    { version : String }


experimentDefaultState : Model
experimentDefaultState =
    { modules = []
    , directory = "/tmp/place_tmp"
    , updates = 1
    , comments = ""
    , plotData = Html.text ""
    , showJson = False
    , showData = False
    , version = "0.0.0"
    , ready = "PLACE loading"
    }


experimentErrorState : String -> Model
experimentErrorState err =
    { modules = []
    , directory = ""
    , updates = 0
    , comments = err
    , plotData = Html.strong [] [ Html.text "There was an error!" ]
    , showJson = False
    , showData = False
    , version = "0.0.0"
    , ready = "Error"
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
