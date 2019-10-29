port module PolytecOFV5000X exposing (main)

import Html exposing (Html)
import Html.Attributes
import Html.Events
import Json.Decode as D
import Json.Decode.Pipeline exposing (optional, required)
import Json.Encode as E
import Metadata exposing (Metadata)
import Plugin exposing (Plugin)
import PluginHelpers exposing (anOption)


common : Metadata
common =
    { title = "Polytec OFV-5000 Xtra"
    , authors = [ "Paul Freeman" ]
    , maintainer = "Jonathan Simpson"
    , email = "jsim921@aucklanduni.ac.nz"
    , url = "https://github.com/palab/place"
    , elm =
        { moduleName = "PolytecOFV5000X"
        }
    , python =
        { moduleName = "polytec"
        , className = "OFV5000X"
        }
    , defaultPriority = "50"
    }


type alias Model =
    { dx300 : Bool
    , dx900 : Bool
    , vx09 : Bool
    , dx300range : String
    , dx900range : String
    , vx09range : String
    , timeout : String
    , autofocus : String
    , areaMin : String
    , areaMax : String
    , autofocusEverytime : Bool
    , plot : Bool
    }


dx300rangeDefault : String
dx300rangeDefault =
    "125nm/V"


dx900rangeDefault : String
dx900rangeDefault =
    "125nm/V"


vx09rangeDefault : String
vx09rangeDefault =
    "12.5mm/s/V"


default : Model
default =
    { dx300 = False
    , dx900 = False
    , vx09 = False
    , dx300range = dx300rangeDefault
    , dx900range = dx900rangeDefault
    , vx09range = vx09rangeDefault
    , timeout = "30.0"
    , autofocus = "none"
    , areaMin = "0"
    , areaMax = "1835"
    , autofocusEverytime = False
    , plot = False
    }


type Msg
    = ToggleDX300
    | ToggleDX900
    | ToggleVX09
    | ChangeDX900Range String
    | ChangeVX09Range String
    | ChangeTimeout String
    | ChangeAutofocus String
    | ChangeAreaMin String
    | ChangeAreaMax String
    | ToggleEverytime
    | ChangePlot


update : Msg -> Model -> ( Model, Cmd Msg )
update msg vib =
    case msg of
        ToggleDX300 ->
            ( { vib | dx300 = not vib.dx300, dx300range = dx300rangeDefault }, Cmd.none )

        ToggleDX900 ->
            ( { vib | dx900 = not vib.dx900, dx900range = dx900rangeDefault }, Cmd.none )

        ToggleVX09 ->
            ( { vib | vx09 = not vib.vx09, vx09range = vx09rangeDefault }, Cmd.none )

        ChangeDX900Range newValue ->
            ( { vib | dx900range = newValue }, Cmd.none )

        ChangeVX09Range newValue ->
            ( { vib | vx09range = newValue }, Cmd.none )

        ChangeTimeout newValue ->
            ( { vib | timeout = newValue }, Cmd.none )

        ChangeAutofocus newValue ->
            if newValue == "none" then
                ( { vib
                    | autofocus = "none"
                    , areaMin = default.areaMin
                    , areaMax = default.areaMax
                    , autofocusEverytime = False
                  }
                , Cmd.none
                )

            else if newValue /= "custom" then
                ( { vib
                    | autofocus = newValue
                    , areaMin = default.areaMin
                    , areaMax = default.areaMax
                  }
                , Cmd.none
                )

            else
                ( { vib | autofocus = newValue }, Cmd.none )

        ChangeAreaMin newValue ->
            ( { vib | areaMin = newValue }, Cmd.none )

        ChangeAreaMax newValue ->
            ( { vib | areaMax = newValue }, Cmd.none )

        ToggleEverytime ->
            ( { vib | autofocusEverytime = not vib.autofocusEverytime }, Cmd.none )

        ChangePlot ->
            ( { vib | plot = not vib.plot }, Cmd.none )



--------------------
-- MAIN HTML VIEW --
--------------------


userInteractionsView : Model -> List (Html Msg)
userInteractionsView vib =
    selectDecoders vib
        :: (if vib.dx300 || vib.dx900 || vib.vx09 then
                inputRange vib
                    ++ selectAutofocus vib
                    ++ [ PluginHelpers.checkbox "Plot" vib.plot ChangePlot ]

            else
                [ Html.text "" ]
           )


selectDecoders : Model -> Html Msg
selectDecoders model =
    Html.p []
        [ Html.text "Decoders: "
        , PluginHelpers.checkbox "DX-300" model.dx300 ToggleDX300
        , PluginHelpers.checkbox "DX-900" model.dx900 ToggleDX900
        , PluginHelpers.checkbox "VX-09" model.vx09 ToggleVX09
        ]


inputRange : Model -> List (Html Msg)
inputRange vib =
    []
        ++ (if vib.dx300 then
                [ Html.p [] [ Html.text "DX-300 range: 125 nm/V" ]
                ]

            else
                [ Html.text "" ]
           )
        ++ (if vib.dx900 then
                [ Html.p []
                    [ Html.text "DX-900 range: "
                    , Html.select [ Html.Events.onInput ChangeDX900Range ]
                        [ anOption vib.dx900range "12.5mm/V" "12.5 mm/V"
                        , anOption vib.dx900range "5mm/V" "5 mm/V"
                        , anOption vib.dx900range "2.5mm/V" "2.5 mm/V"
                        , anOption vib.dx900range "1.25mm/V" "1.25 mm/V"
                        , anOption vib.dx900range "500um/V" "500 um/V"
                        , anOption vib.dx900range "250um/V" "250 um/V"
                        , anOption vib.dx900range "125um/V" "125 um/V"
                        , anOption vib.dx900range "50um/V" "50 um/V"
                        , anOption vib.dx900range "25um/V" "25 um/V"
                        , anOption vib.dx900range "12.5um/V" "12.5 um/V"
                        , anOption vib.dx900range "5um/V" "5 um/V"
                        , anOption vib.dx900range "2.5um/V" "2.5 um/V"
                        , anOption vib.dx900range "1.25um/V" "1.25 um/V"
                        , anOption vib.dx900range "500nm/V" "500 nm/V"
                        , anOption vib.dx900range "250nm/V" "250 nm/V"
                        , anOption vib.dx900range "125nm/V" "125 nm/V"
                        ]
                    ]
                ]

            else
                []
           )
        ++ (if vib.vx09 then
                [ Html.p []
                    [ Html.text "VX-09 range: "
                    , Html.select [ Html.Events.onInput ChangeVX09Range ]
                        [ anOption vib.vx09range "2.5m/s/V" "2.5 m/s/V"
                        , anOption vib.vx09range "2.5m/s/V LP" "2.5 m/s/V LP"
                        , anOption vib.vx09range "1.25m/s/V" "1.25 m/s/V"
                        , anOption vib.vx09range "1.25m/s/V LP" "1.25 m/s/V LP"
                        , anOption vib.vx09range "500mm/s/V" "500 mm/s/V"
                        , anOption vib.vx09range "500mm/s/V LP" "500 mm/s/V LP"
                        , anOption vib.vx09range "250mm/s/V" "250 mm/s/V"
                        , anOption vib.vx09range "250mm/s/V LP" "250 mm/s/V LP"
                        , anOption vib.vx09range "125mm/s/V" "125 mm/s/V"
                        , anOption vib.vx09range "125mm/s/V LP" "125 mm/s/V LP"
                        , anOption vib.vx09range "50mm/s/V" "50 mm/s/V"
                        , anOption vib.vx09range "50mm/s/V LP" "50 mm/s/V LP"
                        , anOption vib.vx09range "25mm/s/V" "25 mm/s/V"
                        , anOption vib.vx09range "12.5mm/s/V" "12.5 mm/s/V"
                        ]
                    ]
                ]

            else
                []
           )


selectAutofocus : Model -> List (Html Msg)
selectAutofocus vib =
    [ PluginHelpers.dropDownBox
        "Autofocus"
        vib.autofocus
        ChangeAutofocus
        [ ( "none", "None" )
        , ( "small", "Small" )
        , ( "medium", "Medium" )
        , ( "full", "Full" )
        , ( "custom", "Custom" )
        ]
    ]
        ++ (if vib.autofocus == "custom" then
                [ PluginHelpers.integerField "Autofocus area minimum" vib.areaMin ChangeAreaMin
                , PluginHelpers.integerField "Autofocus area maximum" vib.areaMax ChangeAreaMax
                ]

            else
                []
           )
        ++ (if vib.autofocus /= "none" then
                [ PluginHelpers.checkbox "Autofocus every update" vib.autofocusEverytime ToggleEverytime
                , PluginHelpers.floatField "Autofocus timeout" vib.timeout ChangeTimeout
                ]

            else
                []
           )


encode : Model -> List ( String, E.Value )
encode vib =
    [ ( "dx_300", E.bool vib.dx300 )
    , ( "dx_900", E.bool vib.dx900 )
    , ( "vx_09", E.bool vib.vx09 )
    , ( "dx_300_range", E.string vib.dx300range )
    , ( "dx_900_range", E.string vib.dx900range )
    , ( "vx_09_range", E.string vib.vx09range )
    , ( "autofocus", E.string vib.autofocus )
    ]
        ++ (if vib.autofocus == "custom" then
                [ ( "area_min"
                  , E.int <| PluginHelpers.intDefault default.areaMin vib.areaMin
                  )
                , ( "area_max"
                  , E.int <| PluginHelpers.intDefault default.areaMax vib.areaMax
                  )
                ]

            else
                []
           )
        ++ (if vib.autofocus /= "none" then
                [ ( "autofocus_everytime", E.bool vib.autofocusEverytime )
                , ( "timeout"
                  , E.float
                        (case String.toFloat vib.timeout of
                            Ok num ->
                                num

                            otherwise ->
                                -1.0
                        )
                  )
                ]

            else
                []
           )
        ++ [ ( "plot", E.bool vib.plot )
           ]


decode : D.Decoder Model
decode =
    D.succeed
        Model
        |> required "dx_300" D.bool
        |> required "dx_900" D.bool
        |> required "vx_09" D.bool
        |> required "dx_300_range" D.string
        |> required "dx_900_range" D.string
        |> required "vx_09_range" D.string
        |> optional "timeout" (D.float |> D.andThen (D.succeed << toString)) default.timeout
        |> required "autofocus" D.string
        |> optional "area_min" (D.int |> D.andThen (D.succeed << toString)) default.areaMin
        |> optional "area_max" (D.int |> D.andThen (D.succeed << toString)) default.areaMax
        |> optional "autofocus_everytime" D.bool default.autofocusEverytime
        |> required "plot" D.bool


{-| Helper function to present an option in a drop-down selection box.
-}
anOption : String -> String -> String -> Html Msg
anOption str val disp =
    Html.option
        [ Html.Attributes.value val, Html.Attributes.selected (str == val) ]
        [ Html.text disp ]



----------------------------------------------
-- THINGS YOU PROBABLY DON"T NEED TO CHANGE --
----------------------------------------------


port config : E.Value -> Cmd msg


port removePlugin : String -> Cmd msg


port processProgress : (E.Value -> msg) -> Sub msg


main : Program Never PluginModel PluginMsg
main =
    Html.program
        { init = ( defaultModel, Cmd.none )
        , view = \model -> Html.div [] (viewModel model)
        , update = updatePlugin
        , subscriptions = always <| processProgress UpdateProgress
        }


type alias PluginModel =
    { active : Bool
    , priority : String
    , metadata : Metadata
    , config : Model
    , progress : E.Value
    }


defaultModel : PluginModel
defaultModel =
    { active = False
    , priority = common.defaultPriority
    , metadata = common
    , config = default
    , progress = E.null
    }


type PluginMsg
    = ToggleActive ------------ turn the plugin on and off on the webpage
    | ChangePriority String --- change the order of execution, relative to other plugins
    | ChangePlugin Msg -------- change one of the custom values in the plugin
    | SendToPlace ------------- sends the values in the model to PLACE
    | UpdateProgress E.Value -- update current progress of a running experiment
    | Close ------------------- close the plugin tab on the webpage


newModel : PluginModel -> ( PluginModel, Cmd PluginMsg )
newModel model =
    updatePlugin SendToPlace model


viewModel : PluginModel -> List (Html PluginMsg)
viewModel model =
    PluginHelpers.titleWithAttributions
        common.title
        model.active
        ToggleActive
        Close
        common.authors
        common.maintainer
        common.email
        ++ (if model.active then
                PluginHelpers.integerField "Priority" model.priority ChangePriority
                    :: List.map (Html.map ChangePlugin) (userInteractionsView model.config)
                    ++ [ PluginHelpers.displayAllProgress model.progress ]

            else
                [ Html.text "" ]
           )


updatePlugin : PluginMsg -> PluginModel -> ( PluginModel, Cmd PluginMsg )
updatePlugin msg model =
    case msg of
        ToggleActive ->
            if model.active then
                newModel { model | active = False }

            else
                newModel { model | active = True }

        ChangePriority newPriority ->
            newModel { model | priority = newPriority }

        ChangePlugin pluginMsg ->
            let
                config =
                    model.config

                ( newConfig, cmd ) =
                    update pluginMsg model.config

                newCmd =
                    Cmd.map ChangePlugin cmd

                ( updatedModel, updatedCmd ) =
                    newModel { model | config = newConfig }
            in
            ( updatedModel, Cmd.batch [ newCmd, updatedCmd ] )

        SendToPlace ->
            ( model
            , config <|
                E.object
                    [ ( model.metadata.elm.moduleName
                      , Plugin.encode
                            { active = model.active
                            , priority = PluginHelpers.intDefault model.metadata.defaultPriority model.priority
                            , metadata = model.metadata
                            , config = E.object (encode model.config)
                            , progress = E.null
                            }
                      )
                    ]
            )

        UpdateProgress value ->
            case D.decodeValue Plugin.decode value of
                Err err ->
                    ( { model | progress = E.string <| "Decode plugin error: " ++ err }, Cmd.none )

                Ok plugin ->
                    if plugin.active then
                        case D.decodeValue decode plugin.config of
                            Err err ->
                                ( { model | progress = E.string <| "Decode value error: " ++ err }, Cmd.none )

                            Ok config ->
                                newModel
                                    { active = plugin.active
                                    , priority = toString plugin.priority
                                    , metadata = plugin.metadata
                                    , config = config
                                    , progress = plugin.progress
                                    }

                    else
                        newModel defaultModel

        Close ->
            let
                ( clearModel, clearModelCmd ) =
                    newModel defaultModel
            in
            ( clearModel, Cmd.batch [ clearModelCmd, removePlugin model.metadata.elm.moduleName ] )
