module PluginHelpers exposing
    ( Img
    , Point
    , anOption
    , checkbox
    , colorDecoder
    , dashDecoder
    , displayAllProgress
    , displayItem
    , dropDownBox
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
import Json.Decode as D
import LineChart exposing (Series)
import LineChart.Colors
import LineChart.Dots
import Svg exposing (Svg)


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


displayAllProgress : D.Value -> Html msg
displayAllProgress progress =
    case D.decodeValue (D.oneOf [ D.dict D.value, D.null Dict.empty ]) progress of
        Ok dict ->
            if Dict.isEmpty dict then
                Html.text ""

            else
                Dict.toList dict
                    |> List.map displayItem
                    |> Html.div []

        Err err ->
            Html.text err


displayItem : ( String, D.Value ) -> Html msg
displayItem ( label, value ) =
    Html.figure []
        [ Html.h3 [] [ Html.text label ]
        , Html.div []
            [ case D.decodeValue itemDecoder value of
                Ok html ->
                    html

                Err err ->
                    Html.text err
            ]
        ]


itemDecoder : D.Decoder (Html msg)
itemDecoder =
    D.field "f" D.string
        |> D.andThen
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
                        D.fail "item not recognized"
            )


view1Decoder : D.Decoder (Svg msg)
view1Decoder =
    D.map
        (LineChart.view1 .x .y)
        (D.field "data1" pointsDecoder)


view2Decoder : D.Decoder (Svg msg)
view2Decoder =
    D.map2
        (LineChart.view2 .x .y)
        (D.field "data1" pointsDecoder)
        (D.field "data2" pointsDecoder)


view3Decoder : D.Decoder (Svg msg)
view3Decoder =
    D.map3
        (LineChart.view3 .x .y)
        (D.field "data1" pointsDecoder)
        (D.field "data2" pointsDecoder)
        (D.field "data3" pointsDecoder)


viewDecoder : D.Decoder (Svg msg)
viewDecoder =
    D.map
        (LineChart.view .x .y)
        (D.field "series" (D.list seriesDecoder))



{-
   viewCustomDecoder : LineChart.Events.Config Point msg -> D.Decoder (Svg msg)
   viewCustomDecoder eventMsg =
       D.map2
           LineChart.viewCustom
           (D.field "config" <| chartConfigDecoder eventMsg)
           (D.field "series" <| D.list seriesDecoder)
-}


pngDecoder : D.Decoder (Html msg)
pngDecoder =
    D.field "image" imgDecoder


imgDecoder : D.Decoder (Html msg)
imgDecoder =
    D.field "src" D.string
        |> D.andThen
            (\src ->
                D.field "alt" D.string
                    |> D.andThen
                        (\alt ->
                            D.succeed <|
                                Html.img
                                    [ Html.Attributes.src src
                                    , Html.Attributes.alt alt
                                    ]
                                    []
                        )
            )


seriesDecoder : D.Decoder (Series Point)
seriesDecoder =
    D.field "f" D.string
        |> D.andThen
            (\seriesCategory ->
                case seriesCategory of
                    "line" ->
                        lineDecoder

                    "dash" ->
                        dashDecoder

                    otherwise ->
                        D.fail "series not recognized"
            )


lineDecoder : D.Decoder (Series Point)
lineDecoder =
    D.map4
        LineChart.line
        (D.field "color" colorDecoder)
        (D.field "shape" shapeDecoder)
        (D.field "label" D.string)
        (D.field "data" pointsDecoder)


dashDecoder : D.Decoder (Series Point)
dashDecoder =
    D.map5
        LineChart.dash
        (D.field "color" colorDecoder)
        (D.field "shape" shapeDecoder)
        (D.field "label" D.string)
        (D.field "stroke_dasharray" <| D.list D.float)
        (D.field "data" pointsDecoder)


pointsDecoder : D.Decoder (List Point)
pointsDecoder =
    (D.field "x" <| D.list D.float)
        |> D.andThen
            (\xlist ->
                (D.field "y" <| D.list D.float)
                    |> D.andThen
                        (\ylist ->
                            D.succeed <| List.map2 Point xlist ylist
                        )
            )


colorDecoder : D.Decoder Color
colorDecoder =
    D.string
        |> D.andThen
            (\color ->
                case color of
                    "pink" ->
                        D.succeed LineChart.Colors.pink

                    "blue" ->
                        D.succeed LineChart.Colors.blue

                    "gold" ->
                        D.succeed LineChart.Colors.gold

                    "red" ->
                        D.succeed LineChart.Colors.red

                    "green" ->
                        D.succeed LineChart.Colors.green

                    "cyan" ->
                        D.succeed LineChart.Colors.cyan

                    "teal" ->
                        D.succeed LineChart.Colors.teal

                    "purple" ->
                        D.succeed LineChart.Colors.purple

                    "rust" ->
                        D.succeed LineChart.Colors.rust

                    "strongBlue" ->
                        D.succeed LineChart.Colors.strongBlue

                    "pinkLight" ->
                        D.succeed LineChart.Colors.pinkLight

                    "blueLight" ->
                        D.succeed LineChart.Colors.blueLight

                    "goldLight" ->
                        D.succeed LineChart.Colors.goldLight

                    "redLight" ->
                        D.succeed LineChart.Colors.redLight

                    "greenLight" ->
                        D.succeed LineChart.Colors.greenLight

                    "cyanLight" ->
                        D.succeed LineChart.Colors.cyanLight

                    "tealLight" ->
                        D.succeed LineChart.Colors.tealLight

                    "purpleLight" ->
                        D.succeed LineChart.Colors.purpleLight

                    "black" ->
                        D.succeed LineChart.Colors.black

                    "gray" ->
                        D.succeed LineChart.Colors.gray

                    "grayLight" ->
                        D.succeed LineChart.Colors.grayLight

                    "grayLightest" ->
                        D.succeed LineChart.Colors.grayLightest

                    "transparent" ->
                        D.succeed LineChart.Colors.transparent

                    otherwise ->
                        D.fail <| color ++ " not recognized as a color"
            )


shapeDecoder : D.Decoder LineChart.Dots.Shape
shapeDecoder =
    D.string
        |> D.andThen
            (\shape ->
                case shape of
                    "none" ->
                        D.succeed LineChart.Dots.none

                    "circle" ->
                        D.succeed LineChart.Dots.circle

                    "triangle" ->
                        D.succeed LineChart.Dots.triangle

                    "square" ->
                        D.succeed LineChart.Dots.square

                    "diamond" ->
                        D.succeed LineChart.Dots.diamond

                    "plus" ->
                        D.succeed LineChart.Dots.plus

                    "cross" ->
                        D.succeed LineChart.Dots.cross

                    otherwise ->
                        D.fail <| shape ++ " not recognized as a shape"
            )



{-
   chartConfigDecoder : LineChart.Events.Config Point msg -> D.Decoder (LineChart.Config Point msg)
   chartConfigDecoder eventMsg =
       D.field "ylabel" D.string
           |> D.andThen
               (\ylabel ->
                   D.field "xlabel" D.string
                       |> D.andThen
                           (\xlabel ->
                               D.succeed <|
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
