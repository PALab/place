module Experiment.Model exposing (Experiment, Status(..), Version, encode, decode)

import Json.Encode
import Json.Decode
import Experiment.Plugin exposing (Plugin)


type Status
    = New
    | Started
    | Running
    | Complete
    | Error


type alias Experiment =
    { status : Status
    , plugins : List Plugin
    , updates : Int
    , comments : String
    , version : Version
    , ready : String
    }


type alias Version =
    { major : Int
    , minor : Int
    , revision : Int
    }


encode : Experiment -> Json.Encode.Value
encode experiment =
    Json.Encode.object
        [ ( "status", Json.Encode.string <| toString experiment.status )
        , ( "plugins", Json.Encode.list <| List.map Experiment.Plugin.encode experiment.plugins )
        , ( "updates", Json.Encode.int experiment.updates )
        , ( "comments", Json.Encode.string experiment.comments )
        , ( "version"
          , Json.Encode.object
                [ ( "major", Json.Encode.int experiment.version.major )
                , ( "minor", Json.Encode.int experiment.version.minor )
                , ( "revision", Json.Encode.int experiment.version.revision )
                ]
          )
        , ( "ready", Json.Encode.string experiment.ready )
        ]


decode : Json.Decode.Decoder Experiment
decode =
    Json.Decode.map6
        Experiment
        (Json.Decode.field "status" decodeStatus)
        (Json.Decode.field "plugins" (Json.Decode.list Experiment.Plugin.decode))
        (Json.Decode.field "updates" Json.Decode.int)
        (Json.Decode.field "comments" Json.Decode.string)
        (Json.Decode.field "version" <|
            Json.Decode.map3
                Version
                (Json.Decode.field "major" Json.Decode.int)
                (Json.Decode.field "minor" Json.Decode.int)
                (Json.Decode.field "revision" Json.Decode.int)
        )
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
