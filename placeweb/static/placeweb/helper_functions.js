// this function is called when PLACE needs to send progress data to plugins
function runHandlers(experiment) {
    // get the plugin list inside the experiment data
    pluginList = experiment['plugins'];

    // loop through all the active plugins on the webpage
    for (elmModuleName in modulelist) {

        // keep track of whether we found it or not
        foundFlag = false;
        // see if the active plugin on the webpage is being used
        // by the current experiment
        for (plugin in pluginList) {
            if (elmModuleName == plugin['elmModuleName']) {
                // yes - this one is being used
                // send progress update to this plugin's Elm module
                modulelist[elmModuleName].port.processProgress.send(plugin);
                foundFlag = true;
            }
        }
        if (!foundFlag) {
            // this plugin is not being used by the current experiment.
            // send empty data so it turns off
            emptyData = {
                "python_module_name": "none",
                "python_class_name": "none",
                "elm_module_name": elmModuleName,
                "priority": -999999,
                "data_register": [],
                "config": {},
                "progress": {}
            };
            modulelist[elmModuleName].port.processProgress.send(emptyData);
        }
    }
    // Note that we only check plugins that are active on the current
    // webpage. This means that if the user has not activated the plugin,
    // it will not display progress or load settings into that plugin.
}

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
        pluginApp = module.embed(newPlugin);
        modulelist[name] = pluginApp;
        // link up ports
        handlerlist[name] = [];
        pluginAreaDiv.appendChild(newPlugin);
        handlerlist[name]['config'] = function (config) {
            // connect output of plugin's `config` function
            // to input of PLACE's `pluginConfig` function
            place.ports.pluginConfig.send(config);
        };
        pluginApp.ports.config.subscribe(handlerlist[name]['config'])
        pluginApp.ports.removeModule.subscribe(userRemoveModule);

        // make the new button
        var newPluginButton = document.createElement('button');
        newPluginButton.id = name + "Button";
        newPluginButton.className = "pluginButton";
        newPluginButton.onclick = function (event) {
            openModule(event, name)
        };
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
    pluginApp = modulelist[name]
    pluginApp.ports.removeModule.unsubscribe(userRemoveModule);
    place.ports.pluginProgress.unsubscribe(handlerlist[name]['progress']);
    pluginApp.ports.config.unsubscribe(handlerlist[name]['config']);
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

function hidePlugins() {
    // lookup the plugin area
    var pluginBar = document.getElementById("plugin-navbar");
    var pluginArea = document.getElementById("plugin-content");
    // hide the plugin area
    pluginBar.style.display = "none";
    pluginArea.style.display = "none";
}

function showPlugins() {
    // lookup the plugin area
    var pluginBar = document.getElementById("plugin-navbar");
    var pluginArea = document.getElementById("plugin-content");
    // show the plugin area
    pluginBar.style.display = "block";
    pluginArea.style.display = "block";
}