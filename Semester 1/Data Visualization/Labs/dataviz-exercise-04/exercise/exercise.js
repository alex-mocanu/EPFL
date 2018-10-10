


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

const TEST_TEMPERATURES = [13, 18, 21, 19, 26, 25, 16];
const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

//const MARGIN = { top: 10, right: 10, bottom: 10, left: 10 };
let data = []
for (i = 0; i < DAYS.length; i++) {
	data.push({
		'y': TEST_TEMPERATURES[i],
		'x': i,
		'name': DAYS[i]
	});
}

class ScatterPlot {
	/* your code here */
	plot() {
		const svg = d3.select('svg');
		svg.selectAll('circle')
			.data(data)
			.enter().append('circle')
				.attr('cx', d => d.x)
				.attr('cy', d => d.y)
				.attr('r', 1)
				.style('fill', d => {
					if (d.y < 17)
						return 'blue';
					else if (d.y > 23)
						return 'red';
					return 'white';
				});
	}
}

whenDocumentLoaded(() => {

	// prepare the data here

	//console.log(data);

	const plot = new ScatterPlot('plot', data);
	plot.plot();
});
