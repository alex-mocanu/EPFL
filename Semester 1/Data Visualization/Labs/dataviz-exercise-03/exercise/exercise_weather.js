
/*
	Run the action when we are sure the DOM has been loaded
	https://developer.mozilla.org/en-US/docs/Web/Events/DOMContentLoaded
	Example:
	whenDocumentLoaded(() => {
		console.log('loaded!');
		document.getElementById('some-element');
	});
*/
function whenDocumentLoaded(action) {
	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", action);
	} else {
		// `DOMContentLoaded` already fired
		action();
	}
}

const TEST_TEMPERATURES = [13, 18, 21, 19, 26, 25,16];


// Part 1 - DOM
function showTemperatures(container_element, temperature_array) {
	container_element.innerHTML = "";
	temperature_array.reduce((container, temp) => {
		const para = document.createElement("p");
		const para_text = document.createTextNode(String(temp));
		// Set the temperature
		para.appendChild(para_text);
		// Set the appropriate color for the given temperature
		if (temp <= 17)
			para.classList.add("cold");
		else if (temp >= 23)
			para.classList.add("warm");
		container.appendChild(para);
		return container;
	}, container_element);
}

whenDocumentLoaded(() => {
	// Part 1.1: Find the button + on click event
	const weather_button = document.querySelector('#btn-part1');
	// weather_button.onclick = () => {console.log("The button was clicked");};
	// Part 1.2: Write temperatures
	const weather_div = document.querySelector("div#weather-part1");
	weather_button.onclick = () => showTemperatures(weather_div, TEST_TEMPERATURES);
});

// Part 2 - class

class Forecast {
	constructor(container) {
		this.container = container;
		this.temperatures = [1,2,3,4,5,6,7];
	}

	toString() {
		return "Container: " + String(container) + " Temperatures: " + String(temperatures);
	}

	print() {
		console.log(this.toString());
	}

	show() {
		showTemperatures(this.container, this.temperatures);
	}

	reload() {
		this.temperatures = TEST_TEMPERATURES;
		this.show();
	}
}

whenDocumentLoaded(() => {
	// Identify the weather div element and create the forecast object
	const weather_div2 = document.querySelector("div#weather-part2");
	const forecast = new Forecast(weather_div2);
	forecast.reload();
});

// Part 3 - fetch

const QUERY_LAUSANNE = 'http://query.yahooapis.com/v1/public/yql?format=json&q=select * from weather.forecast where woeid in (select woeid from geo.places(1) where text="Lausanne") and u="c"';

function yahooToTemperatures(data) {
	let raw_data = data.query.results.channel.item.forecast;
	return raw_data.map((elem) => (parseInt(elem.high) + parseInt(elem.low)) / 2);
}

class ForecastOnline extends Forecast {
	constructor(container) {
		super(container);
	}

	reload() {
		fetch(QUERY_LAUSANNE)
		.then((response) => response.json())
		.then((json_data) => {
			this.temperatures = yahooToTemperatures(json_data);
			this.show();
		});
	}
}

whenDocumentLoaded(() => {
	// Identify the weather div element and create the forecast object
	const weather_div3 = document.querySelector("div#weather-part3");
	const forecast = new ForecastOnline(weather_div3);
	forecast.reload();
});

// Part 4 - interactive
class ForecastOnlineCity extends ForecastOnline {
	constructor(container) {
		super(container);
	}

	show() {
		// Create paragraph containing the city name
		const city_para = document.createElement("p");
		const city_text = document.createTextNode(this.city);
		city_para.appendChild(city_text);
		this.container.parentNode.insertBefore(city_para, this.container);
		super.show();
	}

	setCity() {
		// Read the queried city
		this.city = document.querySelector("input#query-city").value;
		console.log(this.city);
	}

	reload() {
		const query = 'http://query.yahooapis.com/v1/public/yql?format=json&q=select * from weather.forecast where woeid in (select woeid from geo.places(1) where text="' + this.city + '") and u="c"';;
		fetch(query)
		.then((response) => response.json())
		.then((json_data) => {
			this.temperatures = yahooToTemperatures(json_data);
			this.show();
		});
	}
}

whenDocumentLoaded(() => {
	// Identify the weather div element and create the forecast object
	const weather_button = document.querySelector('#btn-city');
	const weather_div4 = document.querySelector("div#weather-city");
	const forecast = new ForecastOnlineCity(weather_div4);
	weather_button.onclick = () => {
		forecast.setCity();
		forecast.reload();
	}
});
