-- STEP 1:
-- set the module name to be the same as the file name,
-- but without the .elm extenstion


port module PLACETemplate exposing (main)

import Html exposing (Html)
import Json.Decode exposing (andThen, bool, field, float, int, string, succeed)
import Json.Encode
import PluginHelpers



-- STEP 2:
-- Fill in information for who wrote this module, who maintains it currently, a
-- contact email address, and a project URL. Note that `authors` is a list, but
-- you can only list one person as the `maintainer`. Also, fill in a few string
-- values that will be used in functions behind the scenes.


common : PluginHelpers.Common
common =
    { title = "PLACE Template" -- the title to display in the web application
    , authors = [ "Dr. A. Place" ] -- list of all authors/contributors
    , maintainer = "Mo Places" -- who is currently maintaining the plugin
    , email = "moplaces@everywhere.com" -- email address for the maintainer
    , url = "https://github.com/palab/place" -- a web URL for the plugin
    , elmModuleName = "PLACETemplate" -- the name of this Elm module
    , pythonModuleName = "place_template" -- the name of the Python module used by the server
    , pythonClassName = "PLACETemplate" -- the name of the Python class within the Python module
    }



-- STEP 3:
-- Add variables needed from the user into this data structure. Generally, you
-- want to use Bool or String. However, often you will need Int and Float
-- values. These are usually best kept as Strings within the Elm code and
-- converted to number formats just before sending the data to the server.


type alias Model =
    { active : Bool
    , priority : String

    -- , plot : Bool
    -- , note : String
    -- , samples : String
    -- , start : String
    }



-- STEP 4:
-- For each variable you added, assign it a default value. Remember that it's
-- generally easier to store Ints and Floats as Strings, so we will put quotes
-- around our numeric values to make them String values.


defaultModel : Model
defaultModel =
    { active = False
    , priority = "10"

    -- , plot = True -- Bool
    -- , note : "no comment" -- String
    -- , samples : "10000" -- Int (as String)
    -- , start : "2.5" -- Float (as String)
    }



-- STEP 5:
-- Add a message to change each variable you added. If you aren't sure what to
-- name them, general PLACE convention is to prefix Toggle to variable name if
-- it is a boolean or prefix Change if it is one of the other types.
--
-- Note that all UI elements to manipulate Int, Float, and String variables
-- will return a String from the user, so even if you have a Float variable
-- named "mass", your message from the UI will be something like ChangeMass
-- String, because the UI will send a String based on the keyboard input from
-- the user.


type Msg
    = ToggleActive
    | ChangePriority String
      -- | TogglePlot -- Bool message
      -- | ChangeNote String -- String message
      -- | ChangeSamples String -- Int (as String) message
      -- | ChangeStart String -- Float (as String) message
    | SendToPlace -- sends the values in the model to PLACE
    | UpdateProgress Json.Encode.Value
    | Close -- close the plugin tab on the webpage



-- STEP 6:
-- In this step, we will write what happens when the UI sends us a message. This
-- message is sent whenever the user changes something on the UI. So, each time
-- the user types a digit into an integer box, we want to make sure we update
-- the value in our model. This means that generally, we will handle messages by
-- simply updating the appropriate variable, depending on the message received.
-- Examples have been provided to get you started.


updateModel : Msg -> Model -> ( Model, Cmd Msg )
updateModel msg model =
    case msg of
        ToggleActive ->
            toggleActive model

        -- TogglePlot ->
        --     newModel { model | plot = not model.plot } -- update Bool
        -- ChangeNote newNote ->
        --     newModel { model | note = newNote } -- update String
        -- ChangeSamples newSamples ->
        --     newModel { model | samples = newSamples } -- update Int (as String)
        -- ChangeStart newStart ->
        --     newModel { model | start = newStart } -- update Float (as String)
        --
        ChangePriority newPriority ->
            changePriority newPriority model

        SendToPlace ->
            sendJson model

        UpdateProgress value ->
            updateProgress value model

        Close ->
            close



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
    [ -- Note: the interaction for `active` is handled elsewhere
      PluginHelpers.integerField "Priority" model.priority ChangePriority

    -- , PluginHelpers.checkbox "Plot" model.plot TogglePlot -- Bool
    -- , PluginHelpers.stringField "Note" model.note ChangeNote -- String
    -- , PluginHelpers.integerField "Number of samples" model.samples ChangeSamples -- Int (as String)
    -- , PluginHelpers.floatField "Start time" model.start ChangeStart
    --
    -- Dropdown Box (for Strings with limited choices)
    -- , PluginHelpers.dropDownBox "Shape" model.shape ChangeShape [("circle", "Circle"), ("zigzag", "Zig Zag")]
    --
    -- Note that in the dropdown box, you must also pass the choices. The first
    -- string in each tuple is the value saved into the variable and the second
    -- is the more descriptive string shown to the user on the web interface.
    ]



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


encode : Model -> List ( String, Json.Encode.Value )
encode model =
    [ ( "active", Json.Encode.bool model.active )
    , ( "priority", Json.Encode.int (PluginHelpers.intDefault defaultModel.priority model.priority) )

    -- , ( "plot", Json.Encode.bool model.plot ) -- Bool
    -- , ( "note", Json.Encode.string model.note ) -- String
    -- , ( "samples", Json.Encode.int (PluginHelpers.intDefault defaultModel.samples model.samples) ) -- Int (as String)
    -- , ( "start", Json.Encode.float (PluginHelpers.floatDefault defaultModel.start model.start) ) -- Float (as String)
    ]



-- STEP 9:
-- There are times when PLACE may need to load settings into your plugin. For
-- example, if the user wants to repeat an experiment, all the settings from the
-- experiment will need to be loaded into your plugin. Like most things, PLACE
-- will handle most of this for us. However, we still need to decode the values
-- used specifically by our plugin and save them into the Model.


decode : Json.Decode.Decoder Model
decode =
    (Json.Decode.map2
        -- `map2` through `map8` are available
        -- depending on the number of fields needed
        Model
        (field "active" bool)
        (field "priority" int |> andThen (succeed << toString))
     -- (field "plot" bool) -- Bool
     -- (field "note" string) -- String
     -- (field "samples" int |> andThen (succeed << toString)) -- Int (as String)
     -- (field "start" float |> andThen (succeed << toString)) -- Float (as String)
    )



-- STEP 10:
-- If your PLACE module records data, it is expected to register it in the
-- PLACE user interface. This allows users to get an accurate representation of
-- the data layout using the "Show Data Layout" button in the webapp. This is
-- simply a list of strings describing the data. Elm will prefix each sting
-- with the python class name and a dash, so a string "time" might become
-- "PLACETemplate-time".


dataRegister : List String
dataRegister =
    -- example: ["time", "position", "temperature"]
    []



-- THE END
-- What follows this is some additional code to handle some of the information
-- you provided above. Beginning users won't need to change it, but PLACE is
-- certainly capable of a great many features when harnessed by an advanced
-- user.
--
--
----------------------------------------------
-- THINGS YOU PROBABLY DON"T NEED TO CHANGE --
----------------------------------------------


port config : Json.Encode.Value -> Cmd msg


port removePlugin : String -> Cmd msg


port processProgress : (Json.Encode.Value -> msg) -> Sub msg


main : Program Never Model Msg
main =
    Html.program
        { init = ( defaultModel, Cmd.none )
        , view = \model -> Html.div [] (viewModel model)
        , update = updateModel
        , subscriptions = always <| processProgress UpdateProgress
        }


newModel : Model -> ( Model, Cmd Msg )
newModel model =
    updateModel SendToPlace model


viewModel : Model -> List (Html Msg)
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
                userInteractionsView model

            else
                [ Html.text "" ]
           )


toggleActive : Model -> ( Model, Cmd Msg )
toggleActive model =
    if model.active then
        newModel { model | active = False }

    else
        newModel { model | active = True }


close : ( Model, Cmd Msg )
close =
    let
        ( clearModel, clearModelCmd ) =
            newModel defaultModel
    in
    ( clearModel, Cmd.batch [ clearModelCmd, removePlugin common.elmModuleName ] )


changePriority : String -> Model -> ( Model, Cmd Msg )
changePriority newPriority model =
    newModel { model | priority = newPriority }


sendJson : Model -> ( Model, Cmd Msg )
sendJson model =
    ( model
    , config <|
        PluginHelpers.encode
            { pythonModuleName = common.pythonModuleName
            , pythonClassName = common.pythonClassName
            , elmModuleName = common.elmModuleName
            , priority = PluginHelpers.intDefault defaultModel.priority model.priority
            , dataRegister = List.map (\s -> common.pythonClassName ++ "-" ++ s) dataRegister
            , config = Json.Encode.object (encode model)
            , progress = Json.Encode.list []
            }
    )


updateProgress : Json.Encode.Value -> Model -> ( Model, Cmd Msg )
updateProgress progress model =
    case Json.Decode.decodeValue PluginHelpers.decode progress of
        Err _ ->
            ( model, Cmd.none )

        Ok plugin ->
            if plugin.priority == -999999 then
                sendJson defaultModel

            else
                case Json.Decode.decodeValue decode plugin.config of
                    Err _ ->
                        ( model, Cmd.none )

                    Ok config ->
                        sendJson config
