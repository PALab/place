module Status exposing (Status(..), Progress, PluginPlots, Plot(..), Series, Point, decode)

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
    , pluginPlots : List PluginPlots
    }


type alias PluginPlots =
    { name : String
    , plots : List Plot
    }


type Plot
    = DataPlot Chart
    | PngPlot Img


type alias Chart =
    { title : String
    , xAxis : String
    , yAxis : String
    , series : List Series
    }


type alias Img =
    { src : String
    , alt : String
    }


type alias Series =
    { name : String
    , points : List Point
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
        (Json.Decode.field "plugin_plots" <| Json.Decode.list pluginPlotsDecode)


pluginPlotsDecode : Json.Decode.Decoder PluginPlots
pluginPlotsDecode =
    Json.Decode.map2
        PluginPlots
        (Json.Decode.field "name" Json.Decode.string)
        (Json.Decode.field "plots" <| Json.Decode.list plotDecode)


plotDecode : Json.Decode.Decoder Plot
plotDecode =
    Json.Decode.oneOf [ chartDecode, imgDecode ]


chartDecode : Json.Decode.Decoder Plot
chartDecode =
    Json.Decode.map4
        Chart
        (Json.Decode.field "title" Json.Decode.string)
        (Json.Decode.field "xaxis" Json.Decode.string)
        (Json.Decode.field "yaxis" Json.Decode.string)
        (Json.Decode.field "series" <| Json.Decode.list seriesDecode)
        |> Json.Decode.andThen (\chart -> Json.Decode.succeed (DataPlot chart))


imgDecode : Json.Decode.Decoder Plot
imgDecode =
    Json.Decode.map2
        Img
        (Json.Decode.field "src" Json.Decode.string)
        (Json.Decode.field "alt" Json.Decode.string)
        |> Json.Decode.andThen (\img -> Json.Decode.succeed (PngPlot img))


seriesDecode : Json.Decode.Decoder Series
seriesDecode =
    Json.Decode.map2
        Series
        (Json.Decode.field "name" Json.Decode.string)
        pointsDecode


pointsDecode : Json.Decode.Decoder (List Point)
pointsDecode =
    (Json.Decode.field "xdata" <| Json.Decode.list Json.Decode.float)
        |> Json.Decode.andThen
            (\xlist ->
                (Json.Decode.field "ydata" <| Json.Decode.list Json.Decode.float)
                    |> Json.Decode.andThen
                        (\ylist ->
                            Json.Decode.succeed <| List.map2 Point xlist ylist
                        )
            )
