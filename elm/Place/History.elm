module Place.History exposing (Model, Msg(..), init, view, update)

import Html exposing (Html)
import Html.Events


type alias Model =
    { experiments : List String
    }


type Msg
    = NewExperiment


init : Model
init =
    { experiments = []
    }


view : Model -> Html Msg
view model =
    Html.div [] <|
        [ Html.p [] [ Html.text "You have reached the incomplete History view" ]
        , Html.button
            [ Html.Events.onClick NewExperiment ]
            [ Html.text "Go back" ]
        ]


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    ( model, Cmd.none )
