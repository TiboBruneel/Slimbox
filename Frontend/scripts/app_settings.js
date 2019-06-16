'use strict';

let domLocationButton, domCurrentLocationTitle;
let apiLocation = '';

const IP = window.location.hostname + ':5000';
const socket = io.connect(IP)

//#region ***********  DOM references ***********
//#endregion

//#region ***********  Callback - HTML Generation (After select) ***********
// show________
const showCurrentLocation = function() {
    domCurrentLocationTitle.innerHTML = `Current location: ${localStorage.getItem("location")}`;
}

const showColorReload = function(colorReload) {
    console.log(colorReload.color);
    let toInsert = `Current color: ${colorReload.color}`;
    document.querySelector('.c-cs__status').innerHTML = toInsert;
}
//#endregion

//#region ***********  Callback - (After update/delete/insert) ***********
// callback______
//#endregion

//#region ***********  Data Access ***********
// get_______
const getColorReload = function() {
    handleData(`http://${IP}/colorreload`, showColorReload, 'GET');
};
//#endregion

//#region ***********  Event Listeners ***********
// listenTo________________
const listenToLocationInput = function(){
    document.querySelector('.c-location__input').addEventListener('input', function() {
        apiLocation = this.value;
    });
};

const listenToLocationButton = function(){
    document.querySelector('.c-location__button').addEventListener('click', function() {
        console.log(apiLocation);
        localStorage.setItem("location", apiLocation);
        document.querySelector('.c-ls__action').innerHTML = `Current location: ${localStorage.getItem("location")}`;
    });
};

const listenToClickColor = function() {
    for (let button of document.querySelector('.c-cs__content').children) {
        button.addEventListener('click', function() {
            let color = this.title;
            console.log(color);
            socket.emit('colorchoice', {color:color});
            let colorclass = `c-button__${color.toLowerCase()}`;
            let toInsert = `Current color: ${color}`;
            document.querySelector('.c-cs__status').innerHTML = toInsert;
        });
    };
};
//#endregion

//#region ***********  INIT / DOMContentLoaded ***********
const init = function() {
    domLocationButton = document.querySelector('.c-location__button');
    domCurrentLocationTitle = document.querySelector('.c-ls__action');

    showCurrentLocation();
    getColorReload();
    listenToLocationInput();
    listenToLocationButton();
    listenToClickColor();
};

document.addEventListener('DOMContentLoaded', init);
//#endregion
