port module Scan exposing (view)

{-|
@docs view
-}

import Html
import Html.Events
import Html.Attributes
import Json.Encode


{-| -}
main : Program Never Scan Msg
main =
    Html.program
        { init = ( placeDefaults, Cmd.none )
        , view = view 4
        , update = update
        , subscriptions = subscriptions
        }


type alias Scan =
    { scan_type : String
    , instruments : List Json.Encode.Value
    }


placeDefaults : Scan
placeDefaults =
    { scan_type = "scan_point_test"
    , instruments = []
    }


{-| -}
view : Int -> Scan -> Html.Html Msg
view indent scan =
    Html.div []
        [ Html.h1 [] [ Html.text "PLACE interface" ]
        , Html.button [ Html.Events.onClick RequestJson ] [ Html.text "Scan" ]
        , Html.br [] []
        , Html.div [ Html.Attributes.id "instruments" ] []
        ]


type Msg
    = ChangeScanType String
    | UpdateJson Json.Encode.Value
    | RequestJson


update : Msg -> Scan -> ( Scan, Cmd Msg )
update msg scan =
    case msg of
        ChangeScanType newValue ->
            ( { scan | scan_type = newValue }, Cmd.none )

        UpdateJson newJson ->
            ( { scan | instruments = newJson :: [] }, Cmd.none )

        RequestJson ->
            ( scan, requestJson "scan" )


port requestJson : String -> Cmd msg


port jsonData : (Json.Encode.Value -> msg) -> Sub msg


subscriptions : Scan -> Sub Msg
subscriptions scan =
    jsonData UpdateJson
