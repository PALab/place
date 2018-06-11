module Experiment.View exposing (view, errorPlotView)

import Html exposing (Html)
import Html.Attributes
import Html.Events
import Experiment exposing (ExperimentMsg(..))
import Experiment.Model exposing (Experiment)


view : Experiment -> Html ExperimentMsg
view model =
    if model.ready == "Ready" then
        readyView model
    else
        loaderView model


readyView : Experiment -> Html ExperimentMsg
readyView model =
    Html.div []
        [ startExperimentView model
        , readyBox model
        , commentBox model
        ]


loaderView : Experiment -> Html ExperimentMsg
loaderView model =
    Html.div []
        [ Html.p [ Html.Attributes.class "loaderTitle" ] [ Html.text "PLACE is busy" ]
        , Html.div [ Html.Attributes.class "loader" ] []
        , Html.p [ Html.Attributes.class "progresstext" ] [ Html.text model.ready ]
        ]


startExperimentView : Experiment -> Html ExperimentMsg
startExperimentView model =
    if model.ready == "Ready" then
        Html.p []
            [ Html.button
                [ Html.Attributes.id "start-button"
                , Html.Events.onClick StartExperiment
                ]
                [ Html.text "Start" ]
            , Html.input
                [ Html.Attributes.id "update-number"
                , Html.Attributes.value <| toString model.updates
                , Html.Attributes.type_ "number"
                , Html.Attributes.min "1"
                , Html.Events.onInput ChangeUpdates
                ]
                []
            , Html.span [ Html.Attributes.id "update-text" ]
                [ if model.updates == 1 then
                    Html.text "update"
                  else
                    Html.text "updates"
                ]
            ]
    else
        Html.text ""


readyBox : Experiment -> Html ExperimentMsg
readyBox experiment =
    Html.p []
        [ Html.text ("PLACE status: " ++ experiment.ready) ]


commentBox : Experiment -> Html ExperimentMsg
commentBox experiment =
    Html.p []
        [ Html.text "Comments:"
        , Html.br [] []
        , Html.textarea
            [ Html.Attributes.rows 3
            , Html.Attributes.cols 60
            , Html.Attributes.value experiment.comments
            , Html.Events.onInput ChangeComments
            ]
            []
        , Html.br [] []
        ]


errorPlotView : Html ExperimentMsg
errorPlotView =
    Html.strong [] [ Html.text "There was an error!" ]


experimentShowData : Experiment -> List (Html ExperimentMsg)
experimentShowData experiment =
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

        numHeadings =
            List.length allHeadings
    in
        [ Html.h2 [] [ Html.text "NumPy data array layout" ]
        , Html.table [ Html.Attributes.id "data-table" ] <|
            [ Html.tr []
                (Html.th [] []
                    :: Html.th [ Html.Attributes.id "device0" ] [ Html.text "time" ]
                    :: allHeadings
                )
            ]
                ++ (case experiment.updates of
                        1 ->
                            [ Html.tr []
                                (Html.td [] [ Html.text "0" ]
                                    :: List.repeat (numHeadings + 1) (Html.td [] [])
                                )
                            ]

                        2 ->
                            [ Html.tr []
                                (Html.td [] [ Html.text "0" ]
                                    :: List.repeat (numHeadings + 1) (Html.td [] [])
                                )
                            , Html.tr []
                                (Html.td [] [ Html.text "1" ]
                                    :: List.repeat (numHeadings + 1) (Html.td [] [])
                                )
                            ]

                        3 ->
                            [ Html.tr []
                                (Html.td [] [ Html.text "0" ]
                                    :: List.repeat (numHeadings + 1) (Html.td [] [])
                                )
                            , Html.tr []
                                (Html.td [] [ Html.text "1" ]
                                    :: List.repeat (numHeadings + 1) (Html.td [] [])
                                )
                            , Html.tr []
                                (Html.td [] [ Html.text "2" ]
                                    :: List.repeat (numHeadings + 1) (Html.td [] [])
                                )
                            ]

                        4 ->
                            [ Html.tr []
                                (Html.td [] [ Html.text "0" ]
                                    :: List.repeat (numHeadings + 1) (Html.td [] [])
                                )
                            , Html.tr []
                                (Html.td [] [ Html.text "1" ]
                                    :: List.repeat (numHeadings + 1) (Html.td [] [])
                                )
                            , Html.tr []
                                (Html.td [] [ Html.text "2" ]
                                    :: List.repeat (numHeadings + 1) (Html.td [] [])
                                )
                            , Html.tr []
                                (Html.td [] [ Html.text "3" ]
                                    :: List.repeat (numHeadings + 1) (Html.td [] [])
                                )
                            ]

                        5 ->
                            [ Html.tr []
                                (Html.td [] [ Html.text "0" ]
                                    :: List.repeat (numHeadings + 1) (Html.td [] [])
                                )
                            , Html.tr []
                                (Html.td [] [ Html.text "1" ]
                                    :: List.repeat (numHeadings + 1) (Html.td [] [])
                                )
                            , Html.tr []
                                (Html.td [] [ Html.text "2" ]
                                    :: List.repeat (numHeadings + 1) (Html.td [] [])
                                )
                            , Html.tr []
                                (Html.td [] [ Html.text "3" ]
                                    :: List.repeat (numHeadings + 1) (Html.td [] [])
                                )
                            , Html.tr []
                                (Html.td [] [ Html.text "4" ]
                                    :: List.repeat (numHeadings + 1) (Html.td [] [])
                                )
                            ]

                        otherwise ->
                            [ Html.tr []
                                (Html.td [] [ Html.text "0" ]
                                    :: List.repeat (numHeadings + 1) (Html.td [] [])
                                )
                            , Html.tr []
                                (Html.td [] [ Html.text "1" ]
                                    :: List.repeat (numHeadings + 1) (Html.td [] [])
                                )
                            , Html.tr [ Html.Attributes.class "skip-row" ]
                                (Html.td [] [ Html.text "..." ]
                                    :: List.repeat (numHeadings + 1)
                                        (Html.td []
                                            [ Html.text "..." ]
                                        )
                                )
                            , Html.tr []
                                (Html.td [] [ Html.text (toString (experiment.updates - 2)) ]
                                    :: List.repeat (numHeadings + 1) (Html.td [] [])
                                )
                            , Html.tr []
                                (Html.td [] [ Html.text (toString (experiment.updates - 1)) ]
                                    :: List.repeat (numHeadings + 1) (Html.td [] [])
                                )
                            ]
                   )
        ]
