module Helpers exposing (..)

{-| Elm helper functions for PLACE.

# Helper Functions

@docs anOption, onload

-}

import Html exposing (Html)
import Html.Attributes
import Json.Encode


{-| Helper function to present an option in a drop-down selection box.
-}
anOption : String -> String -> String -> Html msg
anOption currentValue optionValue displayValue =
    Html.option
        [ Html.Attributes.value optionValue
        , Html.Attributes.selected (currentValue == optionValue)
        ]
        [ Html.text displayValue ]


{-| Support for the HTML onload attribute
-}
onload : String -> Html.Attribute msg
onload script =
    Html.Attributes.property "onload" <| Json.Encode.string script
