port module Place exposing (main)

import Http
import Html exposing (Html)
import Json.Encode
import Json.Decode
import Experiment


port jsonData : (Json.Encode.Value -> msg) -> Sub msg


type alias Model =
    { experiment : Experiment.Model
    , currentView : View
    , version : Version
    , status : Status
    }


type View
    = Main
    | New
    | Experiment Int
    | Database
    | Settings


type Status
    = Ready
    | Busy
    | Unknown
    | Error String


type Msg
    = ExperimentMsg Experiment.Msg
    | GetStatus
    | GetStatusResponse (Result Http.Error Status)


main : Program Flags Model Msg
main =
    Html.programWithFlags
        { init =
            \flags ->
                update GetStatus <|
                    Model Experiment.init New (Version 0 0 0) Unknown
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
        ExperimentMsg experimentMsg ->
            let
                ( experimentModel, experimentCmd ) =
                    Experiment.update experimentMsg model.experiment
            in
                ( { model | experiment = experimentModel }, Cmd.map ExperimentMsg experimentCmd )

        GetStatus ->
            ( model
            , Http.send GetStatusResponse <|
                Http.get "status/" statusDecode
            )

        GetStatusResponse (Ok status) ->
            ( { model | status = status }, Cmd.none )

        GetStatusResponse (Err err) ->
            ( { model | status = Error (toString err) }, Cmd.none )


view : Model -> Html Msg
view model =
    case model.currentView of
        Main ->
            Html.text "PLACE Main View"

        New ->
            case model.status of
                Ready ->
                    Html.div []
                        [ Html.p [] [ Html.text "PLACE server is ready" ]
                        , Html.map ExperimentMsg <| Experiment.view model.experiment
                        ]

                Busy ->
                    Html.text "PLACE is running another experiment"

                otherwise ->
                    Html.text <| "PLACE server status: " ++ (toString model.status)

        Experiment number ->
            Html.text <| "PLACE Experiment " ++ toString number ++ " View"

        Database ->
            Html.text "PLACE Database View"

        Settings ->
            Html.text "PLACE Settings View"



--loaderView : Model -> Html Msg
--loaderView model =
--    Html.div []
--        [ Html.p [ Html.Attributes.class "loaderTitle" ] [ Html.text "PLACE is busy" ]
--        , Html.div [ Html.Attributes.class "loader" ] []
--        , Html.p [ Html.Attributes.class "progresstext" ] [ Html.text (toString model.status) ]
--        ]


subscriptions : Model -> Sub Msg
subscriptions model =
    Sub.batch [ jsonData (\value -> ExperimentMsg (Experiment.UpdatePlugins value)) ]


statusDecode : Json.Decode.Decoder Status
statusDecode =
    Json.Decode.field "status" Json.Decode.string
        |> Json.Decode.andThen fromStringStatus


fromStringStatus : String -> Json.Decode.Decoder Status
fromStringStatus status =
    case status of
        "Ready" ->
            Json.Decode.succeed Ready

        "Running" ->
            Json.Decode.succeed Busy

        "Busy" ->
            Json.Decode.succeed Busy

        "Unknown" ->
            Json.Decode.succeed Unknown

        "Error" ->
            Json.Decode.field "error_string" Json.Decode.string
                |> Json.Decode.andThen (Json.Decode.succeed << Error)

        otherwise ->
            Json.Decode.fail "Invalid status string"
