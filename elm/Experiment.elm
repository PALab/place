module Experiment exposing (Experiment, decode, encode, showLayout)

import Html exposing (Html)
import Html.Attributes
import Json.Decode
import Json.Encode
import PluginHelpers exposing (Plugin)


{-| Configuration data for a PLACE experiment.

This is very similar to the data saved into the `config.json` file.

-}
type alias Experiment =
    { title : String
    , updates : Int
    , plugins : List Plugin
    , comments : String
    }


decode : Json.Decode.Decoder Experiment
decode =
    Json.Decode.map4
        Experiment
        (Json.Decode.field "title" Json.Decode.string)
        (Json.Decode.field "updates" Json.Decode.int)
        (Json.Decode.field "plugins" (Json.Decode.list PluginHelpers.decode))
        (Json.Decode.field "comments" Json.Decode.string)


encode : Experiment -> Json.Encode.Value
encode experiment =
    Json.Encode.object
        [ ( "updates", Json.Encode.int experiment.updates )
        , ( "plugins", Json.Encode.list <| List.map PluginHelpers.encode experiment.plugins )
        , ( "title", Json.Encode.string experiment.title )
        , ( "comments", Json.Encode.string experiment.comments )
        ]


showLayout : Experiment -> Html a
showLayout experiment =
    let
        makeHeading =
            \num name ->
                Html.th [ Html.Attributes.id ("device" ++ toString num) ] [ Html.text name ]

        makeModuleHeadings =
            \device num -> List.map (makeHeading num) device.dataRegister

        allHeadings =
            List.concat <|
                List.map2 makeModuleHeadings (List.sortBy .priority experiment.plugins) <|
                    List.map (\x -> x % 3 + 1) <|
                        List.range 1 (List.length experiment.plugins)

        width =
            List.length allHeadings + 1

        row =
            \label ->
                Html.tr []
                    (Html.td [] [ Html.text (toString label) ]
                        :: List.repeat width (Html.td [] [])
                    )

        headRow =
            Html.tr []
                (Html.th [] []
                    :: Html.th [ Html.Attributes.id "device0" ] [ Html.text "time" ]
                    :: allHeadings
                )

        skipRow =
            Html.tr [ Html.Attributes.class "skip-row" ]
                (Html.td [] [ Html.text "..." ]
                    :: List.repeat width (Html.td [] [ Html.text "..." ])
                )
    in
    Html.div []
        [ Html.h2 [] [ Html.text "NumPy data array layout" ]
        , Html.table [ Html.Attributes.id "data-table" ] <|
            headRow
                :: (if experiment.updates <= 5 then
                        List.map row <| List.range 0 experiment.updates

                    else
                        [ row 0
                        , row 1
                        , skipRow
                        , row (experiment.updates - 2)
                        , row (experiment.updates - 1)
                        ]
                   )
        ]
