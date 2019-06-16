'use strict';

// localStorage.setItem("skrt", "test");

let domTemperatuur, domVolume, domVolumeCircle, domTemperatureOutside, domWeather;
let tempInsideBool = 0;
let tempOutsideBool = 0;

const IP = window.location.hostname + ':5000';
const socket = io.connect(IP)

//#region ***********  DOM references ***********
//#endregion

//#region ***********  Callback - HTML Generation (After select) ***********
// show________
const showTemperatuur = function(jsonTemperatuur){
    let toInsert = ``;
    let temperatuur = jsonTemperatuur[0].Waarde;

    toInsert = `<h1 class="c-ti__temperature">${temperatuur}</h1>`;
    domTemperatuur.innerHTML = toInsert;
};

const showVolume = function(jsonVolume){
    let toInsert = ``;
    let volume = jsonVolume[0].Waarde;

    toInsert = `<h1 class="c-progress-percentage">${volume}%</h1><h2 class="c-progress-volume">Volume</h2>`
    domVolume.innerHTML = toInsert;

    domVolumeCircle.setAttribute("data-percentage", volume);
};

const showWeather = function(jsonWeather){
    let tempInsert = '';
    let toTemperature = jsonWeather.list[0].main.temp;
    Number((toTemperature).toFixed(1))

    tempInsert = `<h1 class="c-to__temperature">${toTemperature}</h1>`;
    domTemperatureOutside.innerHTML = tempInsert;

    let weatherInsert = '';
    let woTitle = jsonWeather.list[0].weather[0].main;
    console.log(woTitle);
    let woPressure = jsonWeather.list[0].main.pressure;
    let woHumidity = jsonWeather.list[0].main.humidity;
    let woWind = jsonWeather.list[0].wind.speed;

    weatherInsert = `<h1 class="c-wo__status">${woTitle}</h1>
    <h3 class="c-wo__detailed">
    <span class="c-wo__pressure c-wo__detail">Pressure: ${woPressure}</span><br>
    <span class="c-wo__humidity c-wo__detail">Humidity: ${woHumidity}</span><br>
    <span class="c-wo__wind c-wo__detail">Wind: ${woWind}km/h</span>`;
    domWeather.innerHTML = weatherInsert;
};

const showHistoriek = function(jsonHistoriek) {
    console.log(jsonHistoriek);
    const labels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
    var data = [];

    for (let el of jsonHistoriek) {
        data.push(el.Waarde);
    }

    var new_data = data.reverse();
    var ctx = document.getElementById('myChart').getContext('2d');
    var myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Temperature',
                data: new_data,
                backgroundColor: [
                    'transparent'
                ],
                borderColor: [
                    'rgba(0, 0, 255, 1)'
                ],
                pointBackgroundColor: 'white'
            }]
        },

    });
};

const colorShow = function(color){
    document.querySelector('.c-cp__color').innerHTML = color;
}

const statusShow = function(status){
    let toInsert = `<h2 class="c-cp__head">Current status</h2><h3 class="c-cp__info">${status}</h3>`;
    document.querySelector('.c-cp__status').innerHTML = toInsert;
}

const showColorReload = function(colorReload) {
    console.log(colorReload.color);
    let toInsert = colorReload.color;
    document.querySelector('.c-cp__color').innerHTML = toInsert;
}
//#endregion

//#region ***********  Callback - (After update/delete/insert) ***********
// callback______
//#endregion

//#region ***********  Data Access ***********
// get_______
const getTemperatuur = function() {
    handleData(`http://${IP}/temperatuur`, showTemperatuur, 'GET');
};

const simpleGet = function(url, callback) {
  fetch(url)
      .then(function(response) {
        if (!response.ok) {
          throw Error(`Probleem bij de fetch(). Status Code: ${response.status}`);
        } else {
          console.info('Er is een response teruggekomen van de server');
          return response.json();
        }
      })
      .then(function(jsonObject) {
        console.info('json object is aangemaakt');
        console.info('verwerken data');
        callback(jsonObject);
      })
      .catch(function(error) {
        console.error(`fout bij verwerken json ${error}`);
      });
};

const getWeather = function(locatie) {
    simpleGet(`http://api.openweathermap.org/data/2.5/forecast?q=${locatie},BE&appid=15448470067381744e3697b424339773&units=metric&lang=en`, showWeather);
};

const getTempHistoriek = function() {
    handleData(`http://${IP}/temperatuurhistoriek`, showHistoriek, 'GET');
};

const getColorReload = function() {
    handleData(`http://${IP}/colorreload`, showColorReload, 'GET');
};
//#endregion

//#region ***********  Event Listeners ***********
// listenTo________________
const listenToFahrenheitInside = function(){
    document.querySelector('.c-ti__fahrenheit').addEventListener('click', function() {
        if (tempInsideBool == 0){
            let valueCelcius = document.querySelector('.c-ti__temperature').innerHTML;
            console.log(valueCelcius);
            let valueFahrenheit = (parseFloat(valueCelcius.replace(",", ".")) * 9 / 5) + 32;
            console.log(valueFahrenheit);
            document.querySelector('.c-ti__temperature').innerHTML = Number((valueFahrenheit).toFixed(1));;
            document.getElementById('c-ti__degrees').style.opacity = "0.2";
            document.getElementById('c-ti__fahrenheit').style.opacity = "1";
            tempInsideBool = 1;
        };
    });
};

const listenToCelciusInside = function(){
    document.querySelector('.c-ti__degrees').addEventListener('click', function() {
        if (tempInsideBool == 1){
            let valueFahrenheit = document.querySelector('.c-ti__temperature').innerHTML;
            console.log(valueFahrenheit);
            let valueCelcius = (valueFahrenheit - 32) * 5 / 9;
            console.log(valueCelcius);
            document.querySelector('.c-ti__temperature').innerHTML = Number((valueCelcius).toFixed(1));;
            document.getElementById('c-ti__degrees').style.opacity = "1";
            document.getElementById('c-ti__fahrenheit').style.opacity = "0.2";
            tempInsideBool = 0;
        };
    });
};

const listenToFahrenheitOutside = function(){
    document.querySelector('.c-to__fahrenheit').addEventListener('click', function() {
        if (tempOutsideBool == 0){
            let valueCelcius = document.querySelector('.c-to__temperature').innerHTML;
            console.log(valueCelcius);
            let valueFahrenheit = (parseFloat(valueCelcius.replace(",", ".")) * 9 / 5) + 32;
            console.log(valueFahrenheit);
            document.querySelector('.c-to__temperature').innerHTML = Number((valueFahrenheit).toFixed(1));;
            document.getElementById('c-to__degrees').style.opacity = "0.2";
            document.getElementById('c-to__fahrenheit').style.opacity = "1";
            tempOutsideBool = 1;
        };
    });
};

const listenToCelciusOutside = function(){
    document.querySelector('.c-to__degrees').addEventListener('click', function() {
        if (tempOutsideBool == 1){
            let valueFahrenheit = document.querySelector('.c-to__temperature').innerHTML;
            console.log(valueFahrenheit);
            let valueCelcius = (valueFahrenheit - 32) * 5 / 9;
            console.log(valueCelcius);
            document.querySelector('.c-to__temperature').innerHTML = Number((valueCelcius).toFixed(1));;
            document.getElementById('c-to__degrees').style.opacity = "1";
            document.getElementById('c-to__fahrenheit').style.opacity = "0.2";
            tempOutsideBool = 0;
        };
    });
};
//#endregion

//#region ***********  INIT / DOMContentLoaded ***********
const init = function() {
    domTemperatuur = document.querySelector('.c-ti__tempinfo');
    domVolume = document.querySelector('.c-progress-info');
    domVolumeCircle = document.querySelector('.c-progress-circle');
    domTemperatureOutside = document.querySelector('.c-to__tempinfo');
    domWeather = document.querySelector('.c-wo__info');

    socket.on('volumeshow', function(volume){
        console.log(volume.volume);
        let volumeValue = volume.volume;
        let toInsert = `${volume.volume}%`;
        document.querySelector('.c-progress-percentage').innerHTML = toInsert;
        domVolumeCircle.setAttribute("data-percentage", volumeValue);
    })

    socket.on('colorshow', function(data){
        console.log(data.color);
        colorShow(data.color);
    })

    socket.on('statusshow', function(data){
        console.log(data.status);
        statusShow(data.status);
    })

    getTemperatuur();
    getWeather(localStorage.getItem("location"));
    getTempHistoriek();
    getColorReload();
    setInterval(getTemperatuur, 600000);
    setInterval(getWeather(localStorage.getItem("location")), 10000);
    setInterval(getTempHistoriek, 600000);

    listenToFahrenheitInside();
    listenToCelciusInside();
    listenToFahrenheitOutside();
    listenToCelciusOutside();
};

document.addEventListener('DOMContentLoaded', init);
//#endregion
