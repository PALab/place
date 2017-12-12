function userAddModule(type, module, name) {
    localStorage.setItem(name, "1");
    addModule(type, module, name);
}

function addModule(type, module, name) {
    if (!(name in modulelist)) {
        var node = document.createElement('div');
        elmApp = module.embed(node)
        modulelist[name] = elmApp
        node.id = name;
        node.className = type;
        placenode.appendChild(node);
        elmApp.ports.jsonData.subscribe(function(json) {
            place.ports.jsonData.send(json);
        })
        elmApp.ports.removeInstrument.subscribe(userRemoveModule);
    }
}

function addInstrument(module, name) {
    addModule("instrument", module, name)
}
function addPostProcessing(module, name) {
    addModule("postprocessing", module, name)
}
function addExport(module, name) {
    addModule("export", module, name)
}

function userRemoveModule(name) {
    elmApp = modulelist[name]
    elmApp.ports.removeInstrument.unsubscribe(userRemoveModule);
    elmApp.ports.jsonData.unsubscribe(function(json) {
        place.ports.jsonData.send(json);
    })
    var removenode = document.getElementById(name);
    placenode.removeChild(removenode);
    delete modulelist[name]
    localStorage.setItem(name, "0");
}

