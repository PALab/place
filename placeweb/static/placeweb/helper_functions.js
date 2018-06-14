function userAddModule(type, module, name) {
    localStorage.setItem(name, "1");
    addModule(type, module, name);
}

function addModule(type, module, name) {
    if (!(name in modulelist)) {
        var pluginButtonDiv = document.getElementById('pluginbuttons');
        var pluginAreaDiv = document.getElementById('pluginarea');
        // make the new plugin div
        var newPlugin = document.createElement('div');
        newPlugin.id = name;
        newPlugin.className = "plugin";
        // activate Elm
        elmApp = module.embed(newPlugin)
        modulelist[name] = elmApp
        pluginAreaDiv.appendChild(newPlugin);
        elmApp.ports.jsonData.subscribe(function (json) {
            place.ports.jsonData.send(json);
        })
        elmApp.ports.removeModule.subscribe(userRemoveModule);
        // make the new button
        var newPluginButton = document.createElement('button');
        newPluginButton.id = name + "Button";
        newPluginButton.className = "pluginButton";
        newPluginButton.onclick = function (event) { openModule(event, name) };
        var text = document.createTextNode(name);
        newPluginButton.appendChild(text);
        pluginButtonDiv.appendChild(newPluginButton);
        // turn off all modules
        allPlugins = document.getElementsByClassName("pluginActive");
        for (i = 0; i < allPlugins.length; i++) {
            allPlugins[i].className = allPlugins[i].className.replace("Active", "");
        }
        allButtons = document.getElementsByClassName("pluginButtonActive");
        for (i = 0; i < allButtons.length; i++) {
            allButtons[i].className = allButtons[i].className.replace("Active", "");
        }
        // turn on the new module
        newPlugin.className += "Active";
        newPluginButton.className += "Active";
    }
}

function userRemoveModule(name) {
    // disconnect Elm
    elmApp = modulelist[name]
    elmApp.ports.removeModule.unsubscribe(userRemoveModule);
    elmApp.ports.jsonData.unsubscribe(function (json) {
        place.ports.jsonData.send(json);
    });
    delete modulelist[name];

    // remove the module button
    var allButtonsDiv = document.getElementById('pluginbuttons');
    var buttonname = name + "Button";
    var buttonToRemove = document.getElementById(buttonname);
    allButtonsDiv.removeChild(buttonToRemove);

    // remove the module box
    var pluginAreaDiv = document.getElementById('pluginarea');
    var pluginToRemove = document.getElementById(name);
    pluginAreaDiv.removeChild(pluginToRemove);

    // remember
    localStorage.setItem(name, "0");

    // set a new active plugin
    allPlugins = document.getElementsByClassName("plugin");
    allButtons = document.getElementsByClassName("pluginButton");
    if (allPlugins.length >= 1) {
        allPlugins[0].className += "Active";
        allButtons[0].className += "Active";
    }
}

function openModule(evt, name) {
    var i
    // lookup the plugin
    var name = evt.currentTarget.id.replace("Button", "");
    var openPlugin = document.getElementById(name);
    // deactivate other plugins
    var allPlugins = document.getElementsByClassName("pluginActive");
    for (i = 0; i < allPlugins.length; i++) {
        allPlugins[i].className = allPlugins[i].className.replace("Active", "");
    }
    // deactivate other buttons
    var allButtons = document.getElementsByClassName("pluginButtonActive");
    for (i = 0; i < allButtons.length; i++) {
        allButtons[i].className = allButtons[i].className.replace("Active", "");
    }
    // make this plugin active
    openPlugin.className += "Active";
    evt.currentTarget.className += "Active";
}

function openPlace() {
    // deactivate other plugins
    var allPlugins = document.getElementsByClassName("pluginActive");
    for (i = 0; i < allPlugins.length; i++) {
        allPlugins[i].className = allPlugins[i].className.replace("Active", "");
    }
    // deactivate other buttons
    var allButtons = document.getElementsByClassName("pluginButtonActive");
    for (i = 0; i < allButtons.length; i++) {
        allButtons[i].className = allButtons[i].className.replace("Active", "");
    }
    // make Place active
    var placePlugin = document.getElementById("Place")
    placePlugin.className += "Active";
    var placeButton = document.getElementById("PlaceButton")
    placeButton.className += "Active";
}