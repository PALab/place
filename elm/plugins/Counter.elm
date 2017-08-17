-- This file has been written to demonstrate the development of a webapp
-- interface for place. In this file, we look at a simple interface to a
-- "counter", that simply records a unit count for each update and demonstrates
-- the basics of PLACE.
--
-- This first line of Elm code defines the module we are writing. 'port' is a
-- special keyword that defines this module to be accessible through internal
-- ports. It is through these ports that the module we are writing will be able
-- to communicate with the main PLACE scan module. All the PLACE webapp modules
-- will appear on the same webpage, but will communicate back and forth through
-- these ports. This allows plugins to be added to PLACE with much greater
-- ease.
--
-- Additionally, Elm requires us to "expose" at least one function externally,
-- so we will expose the HTML view for our webapp.


port module Counter exposing (view)

{-| A web inerface to a simple counter for PLACE.

This instrument is intended more as a demo than for actual use.

# Main HTML

@docs view

-}

-- Elm enforces strict documentation of all modules. Any functions which are
-- exposed must be documented. The format below this comment is typical. Since
-- we only have one exposed function, we list by itself after the @docs
-- keyword. The other text is written in standard markdown. More infor can be
-- found at: http://package.elm-lang.org/help/documentation-format
--
-- Imports must all be done at the top of the file. This format is similar to
-- that of Python.

import Html exposing (Html)
import Html.Events
import Html.Attributes
import Json.Encode
import Result exposing (withDefault)
import ModuleHelpers exposing (..)


-- Elm was designed to write HTML programs and has helper functions to assist
-- us. We will use the standard program, as it handles all our needs.


main =
    Html.program
        { init = init
        , view = view
        , update = update
        , subscriptions = subscriptions
        }



-- If you are new to Elm, the format may seem strange. The above function can
-- be read as:
--    "When main is executed, return an HTML program, passing it a
--     record object (i.e. dictionary) where init equals init, view equals view,
--     update equals update, and subscriptions equals subscriptions."
--
-- In Python, this could be seen as similar to:
--    main = Html.program(init=init, view=view, update=update, subscriptions=subscriptions)
--
-- However, keep in mind that Elm is a functional programming language, so many
-- things will work a little differently to other programming languages you've
-- probably seen.
--
-- Moving on, we have now committed ourselves to writing at least four more
-- functions, namely, 'init', 'view', 'update', and 'subscriptions'. So, we
-- will now do each of those and talk about what they are each used for.
--
-- 'init' is the first one we will tackle. 'init' is used to initialize the
-- default model. To keep things simple, you can think of the model as the set
-- of all the things that can change (i.e. variables). Functional programs
-- always try to keep variables in boxes, so that access to them can be highly
-- structured. Additionally, 'init' must contain the first command to execute,
-- which is currently nothing.
--
-- Ignoring the first line for a second, let's look at the init function.


init : ( Counter, Cmd msg )
init =
    ( { active = False
      , priority = 10
      , sleep = 1.0
      , plot = False
      }
    , Cmd.none
    )



-- So, our model will consist of an active Boolean, a priority value, a sleep
-- value, and a plot value. The value of active will tell us if the Counter is
-- active or not. The priority is a value used by all PLACE instruments to
-- determine the order of update. The sleep value is used to determined how
-- long we should sleep during each update, and the plot value will indicate if
-- we should send plot data back to the webapp or not. Our section of the
-- webapp will need to provide controls to manipulate all these values, and
-- when a scan is started, we will need to send JSON data for these values into
-- the Scan app.
--
-- Now that we know our model, let's take a momement to define it.


type alias Counter =
    { active : Bool
    , priority : Int
    , sleep : Float
    , plot : Bool
    }



-- Elm is a strongly-typed language, meaning it is important that it always
-- knows what type everything is. In fact, if it can't tell what type
-- everything is at all times, it will complain. Additionally, by using a type
-- alias, we are saying that we want to use the short name 'Counter' to
-- represent the record of four values with different types. This is similar to
-- the idea of a struct in C.
--
-- Now that we have defined the Counter type, we can make sense of that first
-- line above the init function. "init : (Counter, Cmd msg)" can be read as,
-- "The function init returns a Counter and a Cmd." It's essentiall a function
-- that takes no arguments and always returns the same value, which is how
-- constants are defined in functional languages.
--
-- Okay, let's move on to the view function.


view : Counter -> Html Msg
view counter =
    Html.div [] <| mainView counter



-- It's just a few lines, but let's make sure we know what's going on here. The
-- first line tells us that the view function takes in a Counter and produces
-- an Html Msg. This makes sense for what we want our view to do. When view is
-- called, it makes sense that we should tranform our model (Counter) into a
-- webpage (Html Msg).
--
-- The next line again states the name of the function. The second word,
-- 'counter' is simply assigning a name to the Counter object that is being
-- passed into the function. Then, we are saying that this function equals an
-- Html div object. But what happens on the rest of that line?
--
-- Well, [] is the empty list, just like in Python. It is being passed into the
-- Html.div function as the first argument. The '<|' is a special symbol. It
-- basically says to stop processing this line left-to-right for a minute. It
-- says to evaluate everything to the right of it first, and then come back and
-- apply it to the left. Some programmers (especially functional programmers)
-- see this as a better alternative to parenthesis. But, parathesis are still
-- allowed in Elm, so you should know that the line is exactly the same as:
--     Html.div [] (mainView counter)
--
-- If we read the documentation for Html.div, we see that it does indeed take
-- two arguments. So in our case we can see that the first argument to div is
-- the empty list, and the second is whatever we get back from "mainView
-- counter". If you know a little HTML, this makes a bit more sense, but the
-- first argument to div is a list of attributes for the div and the second
-- argument is everything that we want inside the div node on our HTML page. We
-- do this so that the main PLACE webapp can receive our entire webapp 'plugin'
-- in a nice, neat, div box.
--
-- Writing HTML is a bit of a chore, and Elm does not really shorten this
-- process, but it will help us break it into chunks. So, just take your time
-- and you will get used to the Elm style pretty quickly.
--
-- We will come back and write the mainView function in a bit. For now lets
-- stick to the other functions from our main program.


update : Msg -> Counter -> ( Counter, Cmd Msg )
update msg counter =
    case msg of
        ChangePriority newValue ->
            changePriority newValue counter

        ChangeSleep newValue ->
            changeSleep newValue counter

        PlotSwitch yesOrNo ->
            plotSwitch yesOrNo counter

        ToggleActive ->
            toggleActive counter

        SendJson ->
            sendJson counter



-- The update function is the only way to update our model. It is all done here
-- so that we can assure that the rest of our code is working with unchanging
-- data. As the user, we don't really care about why this is, but we need to
-- understand that it IS the way it is.
--
-- So, we can see that update takes a Msg and a Counter and produces a Counter
-- and a Cmd (with a Msg). Basically, this is saying, "If I give you a Counter
-- object and some message that tells you to update something, will you make me
-- a new Counter object that has the change made to it. Oh, and also, you can
-- call another command when you are done, if you need to."
--
-- To support this request, we have a case statement that lists a bunch of
-- names of possible messages. But, we need to formally define these.


type Msg
    = ChangePriority String
    | ChangeSleep String
    | PlotSwitch String
    | ToggleActive
    | SendJson



-- Msg is a 'type', roughly meaning that it is our own custom type. In this
-- case, we are saying that our message is 1 of 5 things... 3 of which also
-- have a String attached to them. This String will be pulled from the webapp.
-- The 5th Msg, SendJson, is a message we need to send the data to the main
-- webapp. It does not require a String, so it doesn't have one.
--
-- Going back to our update function, we can see that each Msg in the case
-- statement just leads to calling another function. Again, this is simply to
-- break all this up for this tutorial. In a real life situation, these
-- functions would frequently be written in the case statement.
--
-- For now, let's move on to the subscriptions function.


subscriptions : Counter -> Sub msg
subscriptions counter =
    Sub.none



-- This one is actually easy. We aren't using it. If our webapp were waiting for
-- any messages from anywhere, we would need to specify those here. Instead,
-- PLACE waits for us to send stuff to it, so all the subscriptions are done on
-- its end. Here, we just return Sub.none anytime the program calls it.
--
-- Okay, so the functions of the Html.program have all been written, but we
-- have created an even larger list of functions to write. So let's start
-- digging into those. We'll finish up the HTML first.


mainView : Counter -> List (Html Msg)
mainView counter =
    -- Remember that mainView is the second argument of our Html.div function,
    -- and must therefore produce a List of Html elements. div will put all
    -- those into an HTML div for us.
    --
    -- We will have 2 different displays available here. If the counter is of,
    -- we will only display nothing. If it is on, we will show all the other
    -- options.
    --
    -- So, let's start with an if statement:
    title "PLACE Demo Instrument" counter.active ToggleActive
        ++ if counter.active then
            [ -- Here is a paragraph for the priority.
              Html.p [] (priorityView counter)
            , -- And we will put 2 paragraphs for the other 2 options.
              Html.p [] (sleepView counter)
            , Html.p [] (plotView counter)
            ]
           else
            [ -- Just return a blank text block
              Html.text ""
            ]



-- Each subfunction gets passed the current Counter model. We continue working
-- deeper into the HTML tree until we cover it all.


priorityView counter =
    [ Html.text "Priority: "
    , -- This input box allows users to type in a value.
      Html.input
        [ -- We display the current number as a string.
          Html.Attributes.value <| toString counter.priority
        , -- We ensure the value is a number.
          Html.Attributes.type_ "number"
        , -- On new input, we send a message.
          Html.Events.onInput ChangePriority
        ]
        []
    ]


sleepView counter =
    [ Html.text "Sleep: "
    , Html.input
        [ Html.Attributes.value <| toString counter.sleep
        , Html.Attributes.type_ "number"
        , -- This changes the step amount that is valid for the number.
          Html.Attributes.step "0.001"
        , Html.Events.onInput ChangeSleep
        ]
        []
    ]


plotView counter =
    [ Html.text "Plot: "
    , Html.select [ Html.Events.onInput PlotSwitch ]
        [ Html.option
            [ Html.Attributes.value "No"
            , Html.Attributes.selected (not counter.plot)
            ]
            [ Html.text "No" ]
        , Html.option
            [ Html.Attributes.value "Yes"
            , Html.Attributes.selected counter.plot
            ]
            [ Html.text "Yes" ]
        ]
    ]



-- There! That sorts out all the HTML. The online Elm documentation for HTML is
-- very thorough, so feel free to investigate it for all the other options.
-- Also, learning how HTML works is useful.
--
-- Now let's write those message functions. Before we start, though, we should
-- think about what needs to happen when the user changes something in the
-- webapp. As I mentioned before, the main PLACE webapp doesn't know about the
-- plugin parts of the webapp. And since we don't have any subscriptions,
-- nothing can ask our part of the webapp if any changes have been made.
-- Therefore, we must send our changes to PLACE when they happen. That way,
-- PLACE always has the latest model created by the user interations.
--
-- To achieve our goal, every time there is a user interaction it will generate
-- a message to change the model. However, after the model has been changed, we
-- will produce a new message to send the latest JSON data to PLACE using the
-- SendJson message - it's a message for messages to use.
--
-- Let's see how this works, and also show you the 'let' statement in Elm.


toggleActive counter =
    let
        -- 'let' is a convenience syntax. It allows us to reference a longer
        -- calculation with a single name. In this case, we are representing
        -- the new model with the short name, newCounterModel.
        newCounterModel =
            -- This syntax here is a way of constructing a new record (or
            -- model) from an existing one. It can be read, "The value of
            -- 'counter' such that 'active' equals the not of 'active' in
            -- 'counter'".
            { counter | active = not counter.active }
    in
        -- The computations in the 'let' statements are sent into the SendJson
        -- function.
        update SendJson newCounterModel



-- Most of the other functions are similar. Here's one without the 'let'
-- statement. Note that since priority is an integer, we are converting it and
-- setting a default, in case the user enters an invalid string or something.


changePriority newValue counter =
    update SendJson { counter | priority = withDefault 10 (String.toInt newValue) }



-- Here we use that weird '<|' instead of parenthesis again.


changeSleep newValue counter =
    update SendJson { counter | sleep = withDefault 1.0 <| String.toFloat newValue }


plotSwitch yesOrNo counter =
    update SendJson { counter | plot = (yesOrNo == "Yes") }



-- The last message we need to write is the SendJson message. On the surface, it looks simple.


sendJson counter =
    ( counter, jsonData (toJson counter) )



-- So, what is this all about? The update function always has to return a
-- Counter and a Cmd, so 'counter' is the new Counter and "jsonData (toJson
-- counter)" must be the Cmd. jsonData is a function will still need to write,
-- so let's do that now.


port jsonData : Json.Encode.Value -> Cmd msg



-- That's it! That's the whole function. The keyword 'port' at the beginning
-- basically means that we don't need to write the function. We just pass
-- jsonData a JSON encoded value and it will make a Cmd. The update function
-- will run this command for us, and the command essentially sends the data to
-- whoever is listening for it. In this case that's PLACE.
--
-- So now we just need to write the toJson function, which will produce our
-- encoded JSON value for us.


toJson counter =
    -- PLACE expects to get back a list of instruments, in case some webapps
    -- return multiple instruments. So we always start our JSON with a list.
    Json.Encode.list
        -- Inside the list is our model. Since JSON doesn't support arbitrary
        -- objects, we encode them using a dictionary of name and value pairs.
        [ Json.Encode.object
            [ -- The module_name must be the name of our Python module.
              ( "module_name", Json.Encode.string "counter" )
            , -- The class_name must be the name of the Python class in our
              -- module, or "None" if the instrument isn't active.
              ( "class_name"
              , Json.Encode.string
                    (if counter.active then
                        "Counter"
                     else
                        "None"
                    )
              )
            , -- Priority is required by PLACE.
              ( "priority", Json.Encode.int counter.priority )
            , -- The is used to record the field headings we will generate.
              ( "data_register"
              , Json.Encode.list
                    (List.map Json.Encode.string
                        [ "Counter-count", "Counter-trace" ]
                    )
              )
            , -- This must be called config.
              ( "config"
              , Json.Encode.object
                    -- Everything in here is "for our eyes only". In other
                    -- words, PLACE won't look at it, so we can name it
                    -- anything we want and make it as complicated or as small
                    -- as we would like.
                    [ ( "sleep_time", Json.Encode.float counter.sleep )
                    , ( "plot", Json.Encode.bool counter.plot )
                    ]
              )
            ]
        ]
