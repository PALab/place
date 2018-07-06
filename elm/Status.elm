module Status exposing (Status(..), Progress, decode)

import Dict exposing (Dict)
import Json.Decode


type Status
    = Ready
    | Running Progress
    | Error String
    | Unknown


type alias Progress =
    { directory : String
    , currentPhase : String
    , currentPlugin : String
    , currentUpdate : Int
    , totalUpdates : Int
    , pluginProgress : Dict String Json.Decode.Value
    }


decode : Json.Decode.Decoder Status
decode =
    Json.Decode.field "status" Json.Decode.string
        |> Json.Decode.andThen fromStringStatus


fromStringStatus : String -> Json.Decode.Decoder Status
fromStringStatus status =
    case status of
        "Ready" ->
            Json.Decode.succeed Ready

        "Running" ->
            Json.Decode.field "progress" progressDecode
                |> Json.Decode.andThen (Json.Decode.succeed << Running)

        "Error" ->
            Json.Decode.field "error_string" Json.Decode.string
                |> Json.Decode.andThen (Json.Decode.succeed << Error)

        "Unknown" ->
            Json.Decode.succeed Unknown

        otherwise ->
            Json.Decode.fail "Invalid status string"


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
