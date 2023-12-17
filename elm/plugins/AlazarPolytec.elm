-- STEP 1:
-- The first line of code should set the name of your Elm module. The name of
-- the file will need to match the name of the Elm module, but will have a .elm
-- extension.
--
-- Change the name in `port module PLACETemplate exposing (main)` to whatever
-- name you want for your plugin. Rename the file appropriately.


port module AlazarPolytec exposing (main)

import ATS660
import ATS9440
import ATS9462
import AlazarTech
import Html exposing (Html)
import Json.Decode as D
import Json.Decode.Pipeline exposing (hardcoded, optional, required)
import Json.Encode as E
import Metadata exposing (Metadata)
import Plugin exposing (Plugin)
import PluginHelpers
import Polytec



-- STEP 2:
-- Fill in information for who wrote this module, who maintains it currently, a
-- contact email address, and a project URL. Note that `authors` is a list, but
-- you can only list one person as the `maintainer`. Also, fill in the names of
-- the Elm/Python modules associated with this plugin so PLACE can make sure
-- everything gets sent to the correct location. Finally, choose a default PLACE
-- priority for your plugin. (Lower numbers represent higher priority.)


common : Metadata
common =
    { title = "Alazar/Polytec combo" ---------- the title to display in the PLACE web application
    , authors = [ "Dr. A. Place" ] ------------ list of all authors/contributors
    , maintainer = "Mo Places" ---------------- who is currently maintaining the plugin
    , email = "moplaces@everywhere.com" ------- email address for the maintainer
    , url = "https://github.com/palab/place" -- a web URL for the plugin
    , elm =
        { moduleName = "AlazarPolytec" -------- the name of this Elm module
        }
    , python =
        { moduleName = "alazar_polytec" ------- the name of the Python module used by the server
        , className = "AlazarPolytec" --------- the name of the Python class within the Python module
        }
    , defaultPriority = "10" ------------------ the default priority of this plugin
    }



-- STEP 3:
-- In this step you will create the model for your plugin. The model is the list
-- of values that you need the user to be able to modify in the web interface
-- for PLACE. Generally, you want to use Bool (Boolean) or String values,
-- however, you will often need Int (Integer) and Float (Decimal) values, too.
-- These values are usually best kept as Strings within the Elm code and
-- converted to number formats just before sending the data to PLACE.


type alias Model =
    { --   plot : Bool
      -- , note : String
      -- , samples : String
      -- , start : String
      --
      alazarTechBoard : String
    , alazarTechConfig : AlazarTech.Config
    , polytecModel : Polytec.Model
    }



-- STEP 4:
-- For each variable in your model, assign it a default value. Remember that
-- it's generally easier to store Int and Float values as String values, so we
-- will put quotes around our numeric values to indicate that Elm should treat
-- them as String values.


default : Model
default =
    { --   plot = True ---------- Bool
      -- , note = "no comment" -- String
      -- , samples = "10000" ---- Int (as String)
      -- , start = "2.5" -------- Float (as String)
      --
      alazarTechBoard = "ATS660"
    , alazarTechConfig = ATS660.defaultConfig
    , polytecModel = Polytec.default
    }



-- STEP 5:
-- Elm uses messages to communicate user interactions to the code. Add a message
-- to change each variable in your model. If you aren't sure what to name them,
-- general PLACE convention is to prefix "Toggle" to the variable name if it is a
-- Boolean value or "Change" if it is a String value.
--
-- Like all Elm things, each message is a function. Some of them take string
-- arguments, and some of them take no arguments. The type Msg is just a "thing"
-- that will be one of these functions.


type Msg
    = -- TogglePlot -------------- Bool message
      -- | ChangeNote String ----- String message
      -- | ChangeSamples String -- Int (as String) message
      -- | ChangeStart String ---- Float (as String) message
      --
      ChangeAlazarTechBoard String
    | AlazarTechConfigMsg AlazarTech.ConfigMsg
    | PolytecMsg Polytec.Msg



-- STEP 6:
-- In this step, we will write what happens when the UI sends us a message. This
-- message is sent whenever the user changes something on the UI. So, each time
-- the user types a digit into an integer box, we want to make sure we update
-- the value in our model. This means that generally, we will handle messages by
-- simply updating the appropriate variable, depending on the message received.
-- Examples have been provided to get you started.


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        -- TogglePlot ->
        --     ( { model | plot = not model.plot }, Cmd.none ) -- update Bool
        -- ChangeNote newNote ->
        --     ( { model | note = newNote }, Cmd.none ) ---------------- update String
        -- ChangeSamples newSamples ->
        --     ( { model | samples = newSamples }, Cmd.none ) ---------- update Int (as String)
        -- ChangeStart newStart ->
        --     ( { model | start = newStart }, Cmd.none ) -------------- update Float (as String)
        --
        ChangeAlazarTechBoard newAlazarTechBoard ->
            ( { model
                | alazarTechBoard = newAlazarTechBoard
                , alazarTechConfig =
                    case newAlazarTechBoard of
                        "ATS660" ->
                            ATS660.defaultConfig

                        "ATS9440" ->
                            ATS9440.defaultConfig

                        "ATS9462" ->
                            ATS9462.defaultConfig

                        _ ->
                            ATS660.defaultConfig
              }
            , Cmd.none
            )

        AlazarTechConfigMsg alazarTechConfigMsg ->
            ( { model
                | alazarTechConfig =
                    case model.alazarTechBoard of
                        "ATS660" ->
                            AlazarTech.updateConfig ATS660.defaultConfig alazarTechConfigMsg model.alazarTechConfig

                        "ATS9440" ->
                            AlazarTech.updateConfig ATS9440.defaultConfig alazarTechConfigMsg model.alazarTechConfig

                        "ATS9462" ->
                            AlazarTech.updateConfig ATS9462.defaultConfig alazarTechConfigMsg model.alazarTechConfig

                        _ ->
                            AlazarTech.updateConfig ATS660.defaultConfig alazarTechConfigMsg model.alazarTechConfig
              }
            , Cmd.none
            )

        PolytecMsg polytecMsg ->
            let
                ( polytecModel, polytecCmd ) =
                    Polytec.update polytecMsg model.polytecModel
            in
            ( { model | polytecModel = polytecModel }, Cmd.map PolytecMsg polytecCmd )



-- STEP 7:
-- Add interactive elements for each variable you added into the model.
--
-- You can add checkboxes to manipulate boolean values, integer input fields,
-- float input fields, and string input fields.  Additionally, there is a
-- dropdown menu element, to allow selection from a limited number of strings.
-- Put all these elements between the square brackets and separated by commas.
--
-- For most of these functions, you pass the text description of the element,
-- the variable to hold the result, and the message to manipulate the variable.
-- So if, for example, I needed the user to manipulate a float value to describe
-- the velocity, my interactive element might be described with this code:
--
--     PluginHelpers.floatField "Velocity" model.velocity ChangeVelocity
--
-- You can find these functions in the PluginHelpers.elm file, or you can look
-- at other modules for examples.


userInteractionsView : Model -> List (Html Msg)
userInteractionsView model =
    [ -- PluginHelpers.checkbox "Plot" model.plot TogglePlot --------------------------- Bool
      -- , PluginHelpers.stringField "Note" model.note ChangeNote ---------------------- String
      -- , PluginHelpers.integerField "Number of samples" model.samples ChangeSamples -- Int (as String)
      -- , PluginHelpers.floatField "Start time" model.start ChangeStart --------------- Float (as String)
      --
      -- Dropdown Box (for Strings with limited choices)
      -- , PluginHelpers.dropDownBox "Shape" model.shape ChangeShape [("circle", "Circle"), ("zigzag", "Zig Zag")]
      --
      -- Note that in the dropdown box, you must also pass the choices. The first
      -- string in each tuple is the value saved into the variable and the second
      -- is the more descriptive string shown to the user on the web interface.
      PluginHelpers.dropDownBox "AlazarTech Card"
        model.alazarTechBoard
        ChangeAlazarTechBoard
        [ ( "ATS660", "ATS660" )
        , ( "ATS9440", "ATS9440" )
        , ( "ATS9462", "ATS9462" )
        ]
    , Html.map AlazarTechConfigMsg <|
        case model.alazarTechBoard of
            "ATS660" ->
                AlazarTech.configView ATS660.options model.alazarTechConfig

            "ATS9440" ->
                AlazarTech.configView ATS9440.options model.alazarTechConfig

            "ATS9462" ->
                AlazarTech.configView ATS9462.options model.alazarTechConfig

            _ ->
                AlazarTech.configView ATS660.options model.alazarTechConfig
    ]
        ++ (List.map (Html.map PolytecMsg) <| Polytec.userInteractionsView model.polytecModel)



-- STEP 8:
-- Each time a user interaction is made, PLACE updates the JSON text that will
-- be sent to the PLACE backend when the experiment is started. In this step,
-- we will update the JSON. As with other steps, there is a different way to
-- handle each type of variable, so examples are provided.
--
-- As mentioned previously, it is during this step that our Int and Float
-- values will be converted from the String values used in the web interface.
-- In the event that the user tries to start an experiment with illegal values
-- in the number fields, the default value is used.
--
-- This step is important because this is where you will actually define how
-- your Python module will access the values selected by the user in the web
-- interface. So, for example, if you have a variable named "linearDistance" in
-- the Elm Model and you associate it with the String "linear_distance" in this
-- step, then in your Python code, you would be able to access the linear
-- distance selected by the user by accessing self._config['linear_distance'].
--
-- Note that you can ignore values such as `active` and `priority`, as these are
-- automatically handelled by PLACE. This section is just to deal with values
-- that you need to pass to your Python code.


encode : Model -> List ( String, E.Value )
encode model =
    [ -- ( "plot", E.bool model.plot ) --------------------------------------------------------- Bool
      -- , ( "note", E.string model.note ) ----------------------------------------------------- String
      -- , ( "samples", E.int (PluginHelpers.intDefault default.samples model.samples) ) -- Int (as String)
      -- , ( "start", E.float (PluginHelpers.floatDefault default.start model.start) ) ---- Float (as String)
      --
      ( "alazarTechBoard", E.string model.alazarTechBoard )
    , ( "alazarTechConfig"
      , case model.alazarTechBoard of
            "ATS660" ->
                AlazarTech.configToJson ATS660.defaultConfig model.alazarTechConfig

            "ATS9440" ->
                AlazarTech.configToJson ATS9440.defaultConfig model.alazarTechConfig

            "ATS9462" ->
                AlazarTech.configToJson ATS9462.defaultConfig model.alazarTechConfig

            _ ->
                AlazarTech.configToJson ATS660.defaultConfig model.alazarTechConfig
      )
    , ( "polytecModel", E.object (Polytec.encode model.polytecModel) )
    ]



-- STEP 9:
-- There are times when PLACE may need to load settings into your plugin. For
-- example, if the user wants to repeat an experiment, all the settings from the
-- experiment will need to be loaded into your plugin. Like most things, PLACE
-- will handle most of this for us. However, we still need to decode the values
-- used specifically by our plugin and save them into the Model.


decode : D.Decoder Model
decode =
    D.succeed
        Model
        -- |> required "plot" D.bool ------------------------------------------- Bool
        -- |> required "note" D.string ----------------------------------------- String
        -- |> required "samples" (D.int |> D.andThen (D.succeed << toString)) -- Int (as String)
        -- |> required "start" (D.float |> D.andThen (D.succeed << toString)) -- Float (as String)
        --
        -- you can remove this "null" field (it's just a placeholder)
        |> required "alazarTechBoard" D.string
        |> required "alazarTechConfig" AlazarTech.configFromJson
        |> required "polytecModel" Polytec.decode



-- THE END
-- What follows this is some additional code to handle some of the information
-- you provided above. Beginning users won't need to change it, but PLACE is
-- certainly capable of a great many features when harnessed by an advanced
-- user.
--
--
----------------------------------------------
-- THINGS YOU PROBABLY DON'T NEED TO CHANGE --
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
                            , metadata = common
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
                                    , metadata = common
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
