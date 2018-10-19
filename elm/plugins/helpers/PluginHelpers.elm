module PluginHelpers exposing
    ( Common
    , Img
    , Plugin
    , Point
    , anOption
    , checkbox
    , colorDecoder
    , dashDecoder
    , decode
    , displayAllProgress
    , displayItem
    , dropDownBox
    , encode
    , floatDefault
    , floatField
    , floatRangeCheck
    , floatStringField
    , imgDecoder
    , intDefault
    , integerField
    , itemDecoder
    , lineDecoder
    , makeAuthor
    , makeAuthors
    , makeMaintainer
    , pngDecoder
    , pointsDecoder
    , rangeCheck
    , seriesDecoder
    , shapeDecoder
    , stringField
    , title
    , titleWithAttributions
    , view1Decoder
    , view2Decoder
    , view3Decoder
    , viewDecoder
    )

import Color exposing (Color)
import Dict exposing (Dict)
import Html exposing (Html)
import Html.Attributes
import Html.Events
import Json.Decode
import Json.Encode
import LineChart exposing (Series)
import LineChart.Colors
import LineChart.Dots
import Svg exposing (Svg)


type alias Plugin =
    { pythonModuleName : String
    , pythonClassName : String
    , elmModuleName : String
    , priority : Int
    , dataRegister : List String
    , config : Json.Encode.Value
    , progress : Json.Encode.Value
    }


type alias Common =
    { title : String
    , authors : List String
    , maintainer : String
    , email : String
    , url : String
    , elmModuleName : String
    , pythonClassName : String
    , pythonModuleName : String
    }


type alias Point =
    { x : Float
    , y : Float
    }


type alias Img =
    { src : String
    , alt : String
    }


title : String -> Bool -> msg -> msg -> List (Html msg)
title title value activeMsg closeMsg =
    titleWithAttributions title value activeMsg closeMsg [] "" ""


titleWithAttributions : String -> Bool -> msg -> msg -> List String -> String -> String -> List (Html msg)
titleWithAttributions title value activeMsg closeMsg authors maintainer email =
    [ Html.button
        [ Html.Attributes.class "close-x"
        , Html.Events.onClick closeMsg
        ]
        [ Html.text "x" ]
    , Html.button
        [ Html.Attributes.class "close-x"
        , Html.Attributes.class "tooltip"
        ]
        [ Html.text "?"
        , Html.span [ Html.Attributes.class "tooltiptext" ]
            [ Html.p [] <|
                (if authors == [] then
                    [ Html.text "No author provided" ]

                 else
                    makeAuthors authors
                )
                    ++ (if maintainer == "" then
                            []

                        else
                            makeMaintainer maintainer email
                       )
            ]
        ]
    , Html.input
        [ Html.Attributes.type_ "checkbox"
        , Html.Attributes.checked value
        , Html.Events.onClick activeMsg
        ]
        []
    , Html.h2 [] [ Html.text title ]
    ]


makeAuthors : List String -> List (Html msg)
makeAuthors authors =
    let
        firstAuthor =
            Maybe.withDefault "" (List.head authors)

        lastAuthors =
            Maybe.withDefault [] (List.tail authors)
    in
    if List.length authors == 1 then
        [ Html.text ("Author: " ++ firstAuthor) ]

    else
        [ Html.text ("Authors: " ++ firstAuthor) ]
            ++ List.map makeAuthor lastAuthors


makeAuthor : String -> Html msg
makeAuthor author =
    Html.text (", " ++ author)


makeMaintainer : String -> String -> List (Html msg)
makeMaintainer maintainer email =
    if email == "" then
        [ Html.br [] []
        , Html.text ("Maintainer: " ++ maintainer)
        ]

    else
        [ Html.br [] []
        , Html.text "Maintainer: "
        , Html.a
            [ Html.Attributes.href ("mailto:" ++ email) ]
            [ Html.text maintainer ]
        ]


checkbox : String -> Bool -> msg -> Html msg
checkbox description value msg =
    Html.p []
        [ Html.text (description ++ ": ")
        , Html.input
            [ Html.Attributes.type_ "checkbox"
            , Html.Attributes.checked value
            , Html.Events.onClick msg
            ]
            []
        ]


stringField : String -> String -> (String -> msg) -> Html msg
stringField description value msg =
    Html.p []
        [ Html.text (description ++ ": ")
        , Html.input
            [ Html.Attributes.value value
            , Html.Events.onInput msg
            ]
            []
        ]


integerField : String -> String -> (String -> msg) -> Html msg
integerField description value msg =
    Html.p [] <|
        [ Html.text (description ++ ": ")
        , Html.input
            [ Html.Attributes.value value
            , Html.Events.onInput msg
            ]
            []
        ]
            ++ (case String.toInt value of
                    Ok _ ->
                        []

                    Err error_msg ->
                        [ Html.br [] [], Html.span [ Html.Attributes.class "error-text" ] [ Html.text error_msg ] ]
               )


floatField : String -> String -> (String -> msg) -> Html msg
floatField description value msg =
    Html.p [] <|
        [ Html.text (description ++ ": ")
        , Html.input
            [ Html.Attributes.value value
            , Html.Events.onInput msg
            ]
            []
        ]
            ++ (case String.toFloat value of
                    Ok _ ->
                        []

                    Err error_msg ->
                        [ Html.br [] [], Html.span [ Html.Attributes.class "error-text" ] [ Html.text error_msg ] ]
               )


floatStringField : String -> String -> String -> (String -> msg) -> Html msg
floatStringField description value alt_string msg =
    Html.p []
        [ Html.text (description ++ ": ")
        , Html.input
            [ Html.Attributes.value value
            , Html.Events.onInput msg
            ]
            []
        , case String.toFloat value of
            Ok _ ->
                Html.text ""

            Err error ->
                if value == alt_string then
                    Html.text ""

                else
                    Html.span [ Html.Attributes.class "error-text" ]
                        [ Html.br [] []
                        , Html.text (" Error: " ++ error)
                        ]
        ]


dropDownBox : String -> String -> (String -> msg) -> List ( String, String ) -> Html msg
dropDownBox description value msg options =
    Html.p [] <|
        [ Html.text (description ++ ": ")
        , Html.select
            [ Html.Events.onInput msg
            ]
            (List.map (anOption value) options)
        ]


rangeCheck : String -> Float -> Float -> String -> Html msg
rangeCheck string low high error_msg =
    let
        result =
            String.toFloat string
    in
    case result of
        Err err ->
            Html.p [] [ Html.span [ Html.Attributes.class "error-text" ] [ Html.text err ] ]

        Ok value ->
            if low <= value && high >= value then
                Html.text ""

            else
                Html.p [] [ Html.span [ Html.Attributes.class "error-text" ] [ Html.text error_msg ] ]


intDefault : String -> String -> Int
intDefault default value =
    case String.toInt value of
        Ok int ->
            int

        Err _ ->
            Result.withDefault 0 (String.toInt default)


floatDefault : String -> String -> Float
floatDefault default value =
    case String.toFloat value of
        Ok float ->
            float

        Err _ ->
            Result.withDefault 0.0 (String.toFloat default)


floatRangeCheck : Float -> Float -> Float -> String -> Html msg
floatRangeCheck value low high error_msg =
    if low <= value && high >= value then
        Html.text ""

    else
        Html.p [] [ Html.span [ Html.Attributes.class "error-text" ] [ Html.text error_msg ] ]


anOption : String -> ( String, String ) -> Html msg
anOption str ( val, disp ) =
    Html.option
        [ Html.Attributes.value val, Html.Attributes.selected (str == val) ]
        [ Html.text disp ]


displayAllProgress : Maybe Json.Decode.Value -> Html msg
displayAllProgress progress =
    case progress of
        Nothing ->
            Html.text ""

        Just plots ->
            case Json.Decode.decodeValue (Json.Decode.dict Json.Decode.value) plots of
                Ok dict ->
                    Dict.toList dict
                        |> List.map displayItem
                        |> Html.div []

                Err err ->
                    Html.text err


displayItem : ( String, Json.Decode.Value ) -> Html msg
displayItem ( label, value ) =
    Html.figure []
        [ Html.h3 [] [ Html.text label ]
        , Html.div []
            [ case Json.Decode.decodeValue itemDecoder value of
                Ok html ->
                    html

                Err err ->
                    Html.text err
            ]
        ]


decode : Json.Decode.Decoder Plugin
decode =
    Json.Decode.map7
        Plugin
        (Json.Decode.field "python_module_name" Json.Decode.string)
        (Json.Decode.field "python_class_name" Json.Decode.string)
        (Json.Decode.field "elm_module_name" Json.Decode.string)
        (Json.Decode.field "priority" Json.Decode.int)
        (Json.Decode.field "data_register" (Json.Decode.list Json.Decode.string))
        (Json.Decode.field "config" Json.Decode.value)
        (Json.Decode.field "progress" Json.Decode.value)


encode : Plugin -> Json.Encode.Value
encode plugin =
    Json.Encode.object
        [ ( "python_module_name", Json.Encode.string plugin.pythonModuleName )
        , ( "python_class_name", Json.Encode.string plugin.pythonClassName )
        , ( "elm_module_name", Json.Encode.string plugin.elmModuleName )
        , ( "priority", Json.Encode.int plugin.priority )
        , ( "data_register", Json.Encode.list <| List.map Json.Encode.string plugin.dataRegister )
        , ( "config", plugin.config )
        , ( "progress", plugin.config )
        ]


itemDecoder : Json.Decode.Decoder (Html msg)
itemDecoder =
    Json.Decode.field "f" Json.Decode.string
        |> Json.Decode.andThen
            (\itemCategory ->
                case itemCategory of
                    "view1" ->
                        view1Decoder

                    "view2" ->
                        view2Decoder

                    "view3" ->
                        view3Decoder

                    "view" ->
                        viewDecoder

                    "png" ->
                        pngDecoder

                    otherwise ->
                        Json.Decode.fail "item not recognized"
            )


view1Decoder : Json.Decode.Decoder (Svg msg)
view1Decoder =
    Json.Decode.map
        (LineChart.view1 .x .y)
        (Json.Decode.field "data1" pointsDecoder)


view2Decoder : Json.Decode.Decoder (Svg msg)
view2Decoder =
    Json.Decode.map2
        (LineChart.view2 .x .y)
        (Json.Decode.field "data1" pointsDecoder)
        (Json.Decode.field "data2" pointsDecoder)


view3Decoder : Json.Decode.Decoder (Svg msg)
view3Decoder =
    Json.Decode.map3
        (LineChart.view3 .x .y)
        (Json.Decode.field "data1" pointsDecoder)
        (Json.Decode.field "data2" pointsDecoder)
        (Json.Decode.field "data3" pointsDecoder)


viewDecoder : Json.Decode.Decoder (Svg msg)
viewDecoder =
    Json.Decode.map
        (LineChart.view .x .y)
        (Json.Decode.field "series" (Json.Decode.list seriesDecoder))



{-
   viewCustomDecoder : LineChart.Events.Config Point msg -> Json.Decode.Decoder (Svg msg)
   viewCustomDecoder eventMsg =
       Json.Decode.map2
           LineChart.viewCustom
           (Json.Decode.field "config" <| chartConfigDecoder eventMsg)
           (Json.Decode.field "series" <| Json.Decode.list seriesDecoder)
-}


pngDecoder : Json.Decode.Decoder (Html msg)
pngDecoder =
    Json.Decode.field "image" imgDecoder


imgDecoder : Json.Decode.Decoder (Html msg)
imgDecoder =
    Json.Decode.field "src" Json.Decode.string
        |> Json.Decode.andThen
            (\src ->
                Json.Decode.field "alt" Json.Decode.string
                    |> Json.Decode.andThen
                        (\alt ->
                            Json.Decode.succeed <|
                                Html.img
                                    [ Html.Attributes.src src
                                    , Html.Attributes.alt alt
                                    ]
                                    []
                        )
            )


seriesDecoder : Json.Decode.Decoder (Series Point)
seriesDecoder =
    Json.Decode.field "f" Json.Decode.string
        |> Json.Decode.andThen
            (\seriesCategory ->
                case seriesCategory of
                    "line" ->
                        lineDecoder

                    "dash" ->
                        dashDecoder

                    otherwise ->
                        Json.Decode.fail "series not recognized"
            )


lineDecoder : Json.Decode.Decoder (Series Point)
lineDecoder =
    Json.Decode.map4
        LineChart.line
        (Json.Decode.field "color" colorDecoder)
        (Json.Decode.field "shape" shapeDecoder)
        (Json.Decode.field "label" Json.Decode.string)
        (Json.Decode.field "data" pointsDecoder)


dashDecoder : Json.Decode.Decoder (Series Point)
dashDecoder =
    Json.Decode.map5
        LineChart.dash
        (Json.Decode.field "color" colorDecoder)
        (Json.Decode.field "shape" shapeDecoder)
        (Json.Decode.field "label" Json.Decode.string)
        (Json.Decode.field "stroke_dasharray" <| Json.Decode.list Json.Decode.float)
        (Json.Decode.field "data" pointsDecoder)


pointsDecoder : Json.Decode.Decoder (List Point)
pointsDecoder =
    (Json.Decode.field "x" <| Json.Decode.list Json.Decode.float)
        |> Json.Decode.andThen
            (\xlist ->
                (Json.Decode.field "y" <| Json.Decode.list Json.Decode.float)
                    |> Json.Decode.andThen
                        (\ylist ->
                            Json.Decode.succeed <| List.map2 Point xlist ylist
                        )
            )


colorDecoder : Json.Decode.Decoder Color
colorDecoder =
    Json.Decode.string
        |> Json.Decode.andThen
            (\color ->
                case color of
                    "pink" ->
                        Json.Decode.succeed LineChart.Colors.pink

                    "blue" ->
                        Json.Decode.succeed LineChart.Colors.blue

                    "gold" ->
                        Json.Decode.succeed LineChart.Colors.gold

                    "red" ->
                        Json.Decode.succeed LineChart.Colors.red

                    "green" ->
                        Json.Decode.succeed LineChart.Colors.green

                    "cyan" ->
                        Json.Decode.succeed LineChart.Colors.cyan

                    "teal" ->
                        Json.Decode.succeed LineChart.Colors.teal

                    "purple" ->
                        Json.Decode.succeed LineChart.Colors.purple

                    "rust" ->
                        Json.Decode.succeed LineChart.Colors.rust

                    "strongBlue" ->
                        Json.Decode.succeed LineChart.Colors.strongBlue

                    "pinkLight" ->
                        Json.Decode.succeed LineChart.Colors.pinkLight

                    "blueLight" ->
                        Json.Decode.succeed LineChart.Colors.blueLight

                    "goldLight" ->
                        Json.Decode.succeed LineChart.Colors.goldLight

                    "redLight" ->
                        Json.Decode.succeed LineChart.Colors.redLight

                    "greenLight" ->
                        Json.Decode.succeed LineChart.Colors.greenLight

                    "cyanLight" ->
                        Json.Decode.succeed LineChart.Colors.cyanLight

                    "tealLight" ->
                        Json.Decode.succeed LineChart.Colors.tealLight

                    "purpleLight" ->
                        Json.Decode.succeed LineChart.Colors.purpleLight

                    "black" ->
                        Json.Decode.succeed LineChart.Colors.black

                    "gray" ->
                        Json.Decode.succeed LineChart.Colors.gray

                    "grayLight" ->
                        Json.Decode.succeed LineChart.Colors.grayLight

                    "grayLightest" ->
                        Json.Decode.succeed LineChart.Colors.grayLightest

                    "transparent" ->
                        Json.Decode.succeed LineChart.Colors.transparent

                    otherwise ->
                        Json.Decode.fail <| color ++ " not recognized as a color"
            )


shapeDecoder : Json.Decode.Decoder LineChart.Dots.Shape
shapeDecoder =
    Json.Decode.string
        |> Json.Decode.andThen
            (\shape ->
                case shape of
                    "none" ->
                        Json.Decode.succeed LineChart.Dots.none

                    "circle" ->
                        Json.Decode.succeed LineChart.Dots.circle

                    "triangle" ->
                        Json.Decode.succeed LineChart.Dots.triangle

                    "square" ->
                        Json.Decode.succeed LineChart.Dots.square

                    "diamond" ->
                        Json.Decode.succeed LineChart.Dots.diamond

                    "plus" ->
                        Json.Decode.succeed LineChart.Dots.plus

                    "cross" ->
                        Json.Decode.succeed LineChart.Dots.cross

                    otherwise ->
                        Json.Decode.fail <| shape ++ " not recognized as a shape"
            )



{-
   chartConfigDecoder : LineChart.Events.Config Point msg -> Json.Decode.Decoder (LineChart.Config Point msg)
   chartConfigDecoder eventMsg =
       Json.Decode.field "ylabel" Json.Decode.string
           |> Json.Decode.andThen
               (\ylabel ->
                   Json.Decode.field "xlabel" Json.Decode.string
                       |> Json.Decode.andThen
                           (\xlabel ->
                               Json.Decode.succeed <|
                                   LineChart.Config
                                       (LineChart.Axis.default 700 xlabel .x)
                                       (LineChart.Axis.default 400 ylabel .y)
                                       (LineChart.Container.default "line-chart-1")
                                       (LineChart.Axis.Intersection.default)
                                       (LineChart.Interpolation.default)
                                       (LineChart.Legends.default)
                                       eventMsg
                                       (LineChart.Area.default)
                                       (LineChart.Grid.default)
                                       (LineChart.Line.default)
                                       (LineChart.Dots.default)
                                       (LineChart.Junk.default)
                           )
               )
-}
