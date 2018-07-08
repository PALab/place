module ModuleHelpers exposing (..)

import Color exposing (Color)
import Dict exposing (Dict)
import Html exposing (Html)
import Html.Attributes
import Html.Events
import Json.Decode
import LineChart exposing (Series)
import LineChart.Colors
import LineChart.Dots
import Svg exposing (Svg)


type alias Attributions =
    { authors : List String
    , maintainer : String
    , maintainerEmail : String
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
    titleWithAttributions
        title
        value
        activeMsg
        closeMsg
        { authors = [], maintainer = "", maintainerEmail = "" }


titleWithAttributions : String -> Bool -> msg -> msg -> Attributions -> List (Html msg)
titleWithAttributions title value activeMsg closeMsg attributions =
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
                (if attributions.authors == [] then
                    [ Html.text "No author provided" ]
                 else
                    makeAuthors attributions
                )
                    ++ (if attributions.maintainer == "" then
                            []
                        else
                            makeMaintainer attributions
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


makeAuthors : Attributions -> List (Html msg)
makeAuthors attr =
    let
        firstAuthor =
            Maybe.withDefault "" (List.head attr.authors)

        lastAuthors =
            Maybe.withDefault [] (List.tail attr.authors)
    in
        if List.length attr.authors == 1 then
            [ Html.text ("Author: " ++ firstAuthor) ]
        else
            [ Html.text ("Authors: " ++ firstAuthor) ]
                ++ List.map makeAuthor lastAuthors


makeAuthor : String -> Html msg
makeAuthor author =
    Html.text (", " ++ author)


makeMaintainer : Attributions -> List (Html msg)
makeMaintainer attr =
    if attr.maintainerEmail == "" then
        [ Html.br [] []
        , Html.text ("Maintainer: " ++ attr.maintainer)
        ]
    else
        [ Html.br [] []
        , Html.text "Maintainer: "
        , Html.a
            [ Html.Attributes.href ("mailto:" ++ attr.maintainerEmail) ]
            [ Html.text attr.maintainer ]
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
        , Html.select [ Html.Events.onInput msg ] (List.map (anOption value) options)
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


empty : Html msg
empty =
    Html.text ""


anOption : String -> ( String, String ) -> Html msg
anOption str ( val, disp ) =
    Html.option
        [ Html.Attributes.value val, Html.Attributes.selected (str == val) ]
        [ Html.text disp ]


displayAllProgress : Json.Decode.Value -> Html msg
displayAllProgress progress =
    case Json.Decode.decodeValue (Json.Decode.dict Json.Decode.value) progress of
        Ok dict ->
            Dict.toList dict
                |> List.map displayItem
                |> Html.div []

        Err err ->
            Html.text err


displayItem : ( String, Json.Decode.Value ) -> Html msg
displayItem ( label, value ) =
    Html.div []
        [ Html.h3 [] [ Html.text label ]
        , Html.div []
            [ case Json.Decode.decodeValue itemDecoder value of
                Ok html ->
                    html

                Err err ->
                    Html.text err
            ]
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

                    otherwise ->
                        Json.Decode.fail "item not recognized"
            )


view1Decoder : Json.Decode.Decoder (Svg msg)
view1Decoder =
    Json.Decode.field "data1" pointsDecoder
        |> Json.Decode.andThen
            (\data1 ->
                Json.Decode.succeed <| LineChart.view1 .x .y data1
            )


view2Decoder : Json.Decode.Decoder (Svg msg)
view2Decoder =
    Json.Decode.field "data1" pointsDecoder
        |> Json.Decode.andThen
            (\data1 ->
                Json.Decode.field "data2" pointsDecoder
                    |> Json.Decode.andThen
                        (\data2 ->
                            Json.Decode.succeed <| LineChart.view2 .x .y data1 data2
                        )
            )


view3Decoder : Json.Decode.Decoder (Svg msg)
view3Decoder =
    Json.Decode.field "data1" pointsDecoder
        |> Json.Decode.andThen
            (\data1 ->
                Json.Decode.field "data2" pointsDecoder
                    |> Json.Decode.andThen
                        (\data2 ->
                            Json.Decode.field "data3" pointsDecoder
                                |> Json.Decode.andThen
                                    (\data3 ->
                                        Json.Decode.succeed <| LineChart.view3 .x .y data1 data2 data3
                                    )
                        )
            )


viewDecoder : Json.Decode.Decoder (Svg msg)
viewDecoder =
    Json.Decode.field "series" (Json.Decode.list seriesDecoder)
        |> Json.Decode.andThen
            (\seriesList ->
                Json.Decode.succeed <| LineChart.view .x .y seriesList
            )



{-
   imgDecoder : Json.Decode.Decoder (Html msg)
   imgDecoder =
       Json.Decode.map2
           Img
           (Json.Decode.field "src" Json.Decode.string)
           (Json.Decode.field "alt" Json.Decode.string)
           |> Json.Decode.andThen (\img -> Json.Decode.succeed (PngPlot img))
-}


seriesDecoder : Json.Decode.Decoder (Series Point)
seriesDecoder =
    Json.Decode.field "f" Json.Decode.string
        |> Json.Decode.andThen
            (\seriesCategory ->
                case seriesCategory of
                    "line" ->
                        lineDecoder

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
