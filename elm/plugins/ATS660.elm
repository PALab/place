port module ATS660 exposing (main)

import ATS660Config
import AlazarConfig
import Html exposing (Html)
import Json.Decode as D
import Json.Decode.Pipeline exposing (hardcoded, required)
import Json.Encode as E
import Metadata exposing (Metadata)
import Plugin exposing (Plugin)
import PluginHelpers exposing (..)


common : Metadata
common =
    { title = "AlazarTech ATS 660"
    , authors = [ "Paul Freeman" ]
    , maintainer = "Paul Freeman"
    , email = "paul.freeman.cs@gmail.com"
    , url = "https://github.com/palab/place"
    , elm =
        { moduleName = "ATS660"
        }
    , python =
        { moduleName = "alazartech"
        , className = "ATS660"
        }
    , defaultPriority = "100"
    }


type Msg
    = ToggleActive
    | ChangeName String
    | ChangePriority String
    | ChangeConfig AlazarConfig.Msg
    | SendJson
    | UpdateProgress E.Value
    | Close


main : Program Never AlazarConfig.Instrument Msg
main =
    let
        model =
            ATS660Config.default common
    in
    Html.program
        { init = ( model, Cmd.none )
        , view = \instrument -> Html.div [] (view ATS660Config.options instrument)
        , update = update model
        , subscriptions = always <| processProgress UpdateProgress
        }


view : AlazarConfig.Options -> AlazarConfig.Instrument -> List (Html Msg)
view options instrument =
    PluginHelpers.titleWithAttributions
        instrument.metadata.title
        instrument.active
        ToggleActive
        Close
        instrument.metadata.authors
        instrument.metadata.maintainer
        instrument.metadata.email
        ++ (if instrument.active then
                nameView instrument
                    :: Html.map ChangeConfig (AlazarConfig.view options instrument.config)
                    :: [ displayAllProgress instrument.progress ]

            else
                [ Html.text "" ]
           )


update : AlazarConfig.Instrument -> Msg -> AlazarConfig.Instrument -> ( AlazarConfig.Instrument, Cmd Msg )
update default msg instrument =
    case msg of
        ToggleActive ->
            if instrument.active then
                update default SendJson default

            else
                update default SendJson { instrument | active = True }

        ChangeName newInstrument ->
            update default SendJson default

        ChangePriority newValue ->
            update default SendJson { instrument | priority = newValue }

        ChangeConfig configMsg ->
            update default SendJson <|
                { instrument
                    | config = AlazarConfig.update default.config configMsg instrument.config
                }

        SendJson ->
            ( instrument, config <| toJson default instrument )

        UpdateProgress value ->
            case D.decodeValue Plugin.decode value of
                Err err ->
                    ( { instrument | progress = E.string <| "Decode plugin error: " ++ err }, Cmd.none )

                Ok plugin ->
                    if plugin.active then
                        case D.decodeValue AlazarConfig.fromJson plugin.config of
                            Err err ->
                                ( { instrument | progress = E.string <| "Decode value error: " ++ err }, Cmd.none )

                            Ok config ->
                                update default
                                    SendJson
                                    { active = plugin.active
                                    , priority = toString plugin.priority
                                    , metadata = default.metadata
                                    , config = config
                                    , progress = plugin.progress
                                    }

                    else
                        update default SendJson default

        Close ->
            let
                ( model, sendJsonCmd ) =
                    update default SendJson default
            in
            model ! [ sendJsonCmd, removePlugin instrument.metadata.elm.moduleName ]


nameView : AlazarConfig.Instrument -> Html Msg
nameView instrument =
    Html.div []
        [ floatField "Priority" instrument.priority ChangePriority
        , dropDownBox "Plot"
            instrument.config.plot
            (ChangeConfig << AlazarConfig.ChangePlot)
            [ ( "yes", "yes" ), ( "no", "no" ) ]
        ]


toJson : AlazarConfig.Instrument -> AlazarConfig.Instrument -> E.Value
toJson default instrument =
    E.object
        [ ( instrument.metadata.elm.moduleName
          , Plugin.encode
                { active = instrument.active
                , priority = PluginHelpers.intDefault instrument.metadata.defaultPriority instrument.priority
                , metadata = default.metadata
                , config = AlazarConfig.toJson default.config instrument.config
                , progress = E.null
                }
          )
        ]


port config : E.Value -> Cmd msg


port removePlugin : String -> Cmd msg


port processProgress : (E.Value -> msg) -> Sub msg
