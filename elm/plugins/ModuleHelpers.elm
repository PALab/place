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


dropDownBox : String -> String -> (String -> msg) -> List ( String, String ) -> Html msg
dropDownBox description value msg options =
    Html.p [] <|
        [ Html.text (description ++ ": ")
        , Html.select [ Html.Events.onInput msg ] (List.map (anOption value) options)
        ]


rangeCheck : Int -> Int -> Int -> String -> Html msg
rangeCheck value low high error_msg =
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
