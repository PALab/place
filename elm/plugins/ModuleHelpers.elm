module ModuleHelpers exposing (..)

import Html exposing (Html)
import Html.Attributes
import Html.Events


type alias Attributions =
    { authors : List String
    , maintainer : String
    , maintainerEmail : String
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
            Html.p [] <|
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
