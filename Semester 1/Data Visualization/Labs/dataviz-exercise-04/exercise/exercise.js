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

//const MARGIN = { top: 10, right: 10, bottom: 10, left: 10 }

class ScatterPlot {
	/* your code here */
	plot(data) {
		/* Define coordinate limits */
		const min_x = d3.min(data.map((val) => val.x));
		const max_x = d3.max(data.map((val) => val.x));
		const max_y = d3.max(data.map((val) => val.y));
		/* Define scaling rules */
		const scale_x = d3.scaleLinear()
							.domain([min_x, max_x])
							.range([0, 200]);
		const scale_y = d3.scaleLinear()
							.domain([max_y, 0])
							.range([0, 100]);

		/* Draw the circles in the scatter plot */
		const svg = d3.select('svg');
		svg.append('rect')
			.attr('x', 0)
			.attr('y', 0)
			.attr('width', 200)
			.attr('height', 100)
			.style('fill', 'black');
		svg.selectAll('circle')
			.data(data)
			.enter().append('circle')
				.attr('cx', d => scale_x(d.x))
				.attr('cy', d => scale_y(d.y))
				.attr('r', 1)
				.style('fill', d => {
					if (d.y < 17)
						return 'blue';
					else if (d.y > 23)
						return 'red';
					return 'white';
				});

		/* Generate labels data */
		const X_AXIS_TEXT = -1.2;
		const Y_AXIS_TEXT = -0.13;
		const Y_AXIS_GRANULARITY = 5;
		const x_labels_data = data.map((val) => {
			return {
				'x': val.x,
				'y': X_AXIS_TEXT,
				'name': val.name
			};
		});
		const NR_VALS = Array.from(Array(Y_AXIS_GRANULARITY + 1).keys());
		let y_labels_data = NR_VALS.map((val) => val * max_y / Y_AXIS_GRANULARITY);
		y_labels_data = y_labels_data.map((val) => {
			return {
				'x': Y_AXIS_TEXT,
				'y': val,
				'name': d3.format('.1f')(val).toString()
			};
		});
		const labels_data = x_labels_data.concat(y_labels_data);
		console.log(labels_data)
		/* Draw labels for x and y axes */
		svg.selectAll('text')
			.data(labels_data)
			.enter().append('text')
			.attr('x', d => scale_x(d.x))
			.attr('y', d => scale_y(d.y))
			.text(d => d.name);
	}
}

whenDocumentLoaded(() => {

	// prepare the data here
	let data = [];
	for (i = 0; i < DAYS.length; i++) {
		data.push({
			'y': TEST_TEMPERATURES[i],
			'x': i,
			'name': DAYS[i]
		});
	}

	const plot = new ScatterPlot('plot', data);
	plot.plot(data);
});
