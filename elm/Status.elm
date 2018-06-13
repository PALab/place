module Status exposing (Status(..), Progress, decode)

import Json.Decode


type Status
    = Ready
    | Running Progress
    | Error String
    | Unknown


type alias Progress =
    { currentStage : String
    , currentPlugin : String
    , percentage : Float
    , percentageString : String
    , livePlots : List LivePlot
    }


type alias LivePlot =
    { title : String
    , series : List (List Point)
    }


type alias Point =
    { x : Float
    , y : Float
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
    Json.Decode.map5
        Progress
        (Json.Decode.field "current_stage" Json.Decode.string)
        (Json.Decode.field "current_plugin" Json.Decode.string)
        (Json.Decode.field "percentage" Json.Decode.float)
        (Json.Decode.field "percentage_string" Json.Decode.string)
        (Json.Decode.field "live_plots" <| Json.Decode.list liveplotDecode)


liveplotDecode : Json.Decode.Decoder LivePlot
liveplotDecode =
    Json.Decode.map2
        LivePlot
        (Json.Decode.field "title" Json.Decode.string)
        (Json.Decode.field "series" <| Json.Decode.list seriesDecode)


seriesDecode : Json.Decode.Decoder (List Point)
seriesDecode =
    (Json.Decode.field "xdata" <| Json.Decode.list Json.Decode.float)
        |> Json.Decode.andThen
            (\xlist ->
                (Json.Decode.field "ydata" <| Json.Decode.list Json.Decode.float)
                    |> Json.Decode.andThen
                        (\ylist ->
                            Json.Decode.succeed <| List.map2 Point xlist ylist
                        )
            )
