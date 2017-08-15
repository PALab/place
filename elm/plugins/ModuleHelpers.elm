module ModuleHelpers exposing (..)

import Html exposing (Html)
import Html.Attributes
import Html.Events


title : String -> Bool -> msg -> List (Html msg)
title title value msg =
    [ Html.input
        [ Html.Attributes.type_ "checkbox"
        , Html.Attributes.checked value
        , Html.Events.onClick msg
        ]
        []
    , Html.h2 [] [ Html.text title ]
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


integerField : String -> Int -> (String -> msg) -> Html msg
integerField description value msg =
    Html.p []
        [ Html.text (description ++ ": ")
        , Html.input
            [ Html.Attributes.value (toString value)
            , Html.Attributes.type_ "number"
            , Html.Events.onInput msg
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


floatField : String -> String -> (String -> msg) -> Html msg
floatField description value msg =
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
                Html.span [ Html.Attributes.class "error-text" ]
                    [ Html.br [] []
                    , Html.text (" Error: " ++ error)
                    ]
        ]


empty : Html msg
empty =
    Html.text ""
