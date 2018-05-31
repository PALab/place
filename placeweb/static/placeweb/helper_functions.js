function userAddModule(type, module, name) {
    localStorage.setItem(name, "1");
    addModule(type, module, name);
}

function addModule(type, module, name) {
    if (!(name in modulelist)) {
        var tablinks = document.getElementById('placetablinks');
        var tabsnode = document.getElementById('placetabs');
        var node = document.createElement('div');
        // make the tab button
        var button = document.createElement('button');
        button.id = name + "button";
        button.className = "placetabslink";
        button.onclick = function(event){ openModule(event, name) };
        var text = document.createTextNode(name);
        button.appendChild(text);
        tablinks.appendChild(button);

        elmApp = module.embed(node)
        modulelist[name] = elmApp
        node.id = name;
        node.className = "tabcontent";
        tabsnode.appendChild(node);
        elmApp.ports.jsonData.subscribe(function(json) {
            place.ports.jsonData.send(json);
        })
        elmApp.ports.removeModule.subscribe(userRemoveModule);

        // turn on the new module
        tabcontent = document.getElementsByClassName("tabcontent");
        for (i = 0; i < tabcontent.length; i++) {
            tabcontent[i].style.display = "none";
        }
        placetablinks = document.getElementsByClassName("placetablinks");
        for (i = 0; i < placetablinks.length; i++) {
            placetablinks[i].className = placetablinks[i].className.replace(" active", "");
        }
        node.style.display = "block";
        node.className += " active";
    }
}

function userRemoveModule(name) {
    // remove the module button
    var tablinks = document.getElementById('placetablinks');
    var buttonname = name + "button";
    var button = document.getElementById(buttonname);
    tablinks.removeChild(button);
    // remove the module box
    var tabsnode = document.getElementById('placetabs');
    elmApp = modulelist[name]
    elmApp.ports.removeModule.unsubscribe(userRemoveModule);
    elmApp.ports.jsonData.unsubscribe(function(json) {
        place.ports.jsonData.send(json);
    })
    var removenode = document.getElementById(name);
    tabsnode.removeChild(removenode);
    delete modulelist[name]
    localStorage.setItem(name, "0");
    tabcontent = document.getElementsByClassName("tabcontent");
    if (tabcontent.length >= 1) {
        tabcontent[0].style.display = "block";
        tabcontent[0].className += " active";
    }
}

function openModule(evt, name) {
    var i, tabcontent, placetablinks;

    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    placetablinks = document.getElementsByClassName("placetablinks");
    for (i = 0; i < placetablinks.length; i++) {
        placetablinks[i].className = placetablinks[i].className.replace(" active", "");
    }

    document.getElementById(name).style.display = "block";
    evt.currentTarget.className += " active";
}
