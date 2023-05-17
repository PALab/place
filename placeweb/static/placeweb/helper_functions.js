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
        for (idx in pluginList) {
            plugin = pluginList[idx];
            if (elmModuleName == plugin['metadata']['elm_module_name']) {
                // yes - this one is being used
                // send progress update to this plugin's Elm module
                modulelist[elmModuleName].ports.processProgress.send(plugin);
                foundFlag = true;
            }
        }
        if (!foundFlag) {
            // this plugin is not being used by the current experiment.
            // send empty data so it turns off
            emptyData = {
                "active": false,
                "priority": -1,
                "metadata": null,
                "config": null,
                "progress": null
            };
            modulelist[elmModuleName].ports.processProgress.send(emptyData);
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
    console.log(type, module, name)
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
        pluginApp.ports.removePlugin.subscribe(userRemoveModule);

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
    place.ports.pluginRemove.send(name)
    pluginApp = modulelist[name]
    pluginApp.ports.removePlugin.unsubscribe(userRemoveModule);
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

function showPlugins(requiredPluginsList) {
    // Load the required plugins and show the plugin area.
    const elmNames = pluginsList.map(subArray => subArray[subArray.length - 2]);
    for (var i = 0; i < requiredPluginsList.length; i++) {
        var plugin = requiredPluginsList[i];
        if (elmNames.indexOf(plugin) !== -1) {
            pluginIndex = elmNames.indexOf(plugin);
            addModule(...pluginsList[pluginIndex]);
        }
    }
    place.ports.updateFromJavaScript.send(null)

    // lookup the plugin area
    var pluginBar = document.getElementById("plugin-navbar");
    var pluginArea = document.getElementById("plugin-content");
    // show the plugin area
    pluginBar.style.display = "block";
    pluginArea.style.display = "block";
}

function showPluginsDropdown(plugins) {
    // Show the plugins dropdown list
    var pluginsDropdown = document.getElementById("plugins-dropdown-list");

    if (typeof(pluginsDropdown) == 'undefined' || pluginsDropdown == null) {
        var pluginsDropdown = document.createElement("div");
        pluginsDropdown.id  = "plugins-dropdown-list";

        for (idx in pluginsList) {
            plugin = pluginsList[idx];
            button = document.createElement("button");
            button.id = plugin[3];
            button.innerHTML = plugin[3];
            button.addEventListener("click", function(plugin) { return function() {userAddModule(plugin[0],plugin[1],plugin[2])} }(plugin));
            pluginsDropdown.appendChild(button); 
        }
        var addModuleButton = document.getElementById("add-module-button");
        addModuleButton.appendChild(pluginsDropdown); 
    }

    pluginsDropdown.style.display = "block";
}

function hidePluginsDropdown() {
    // Remove the plugins dropdown list
    var pluginDropdown = document.getElementById("plugins-dropdown-list");
    pluginDropdown.style.display = "none";
}

function uploadConfigFile() {
    // Create an input button to upload a config file
    var uploadButton = document.getElementById("upload-config-button");
    var input = document.getElementById("upload-file-button");

    if (typeof(input) == 'undefined' || input == null) {
        var input = document.createElement('input');
        var input = document.createElement('input');

        input.type = "file";
        input.id = "upload-file-button";
        input.accept = ".json";

        input.addEventListener('change', function(e) {
            if (e.target.files[0]) {
                openConfigFile(e.target.files[0]);
            }
          });

        input.style.width = uploadButton.offsetWidth;
        input.style.height = uploadButton.offsetHeight;
        console.log(uploadButton.offsetWidth,uploadButton.offsetHeight)
        uploadButton.appendChild(input);
    }
    
}

function openConfigFile(file) {
    // Pass a user-uploaded config file to Elm PLACE app

    const reader = new FileReader();

    reader.onload = function (e) {
        const fileContent = e.target.result;
    
        const configJson = JSON.parse(fileContent);
        place.ports.receiveConfigFile.send(configJson);
    }
    
    if (file) {
        reader.readAsText(file);
    }
}