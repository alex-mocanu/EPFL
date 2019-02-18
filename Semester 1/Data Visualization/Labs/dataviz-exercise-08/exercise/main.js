
class MapPlot {

	makeColorbar(svg, color_scale, top_left, colorbar_size, scaleClass=d3.scaleLog) {

		const value_to_svg = scaleClass()
			.domain(color_scale.domain())
			.range([colorbar_size[1], 0]);

		const range01_to_color = d3.scaleLinear()
			.domain([0, 1])
			.range(color_scale.range())
			.interpolate(color_scale.interpolate());

		// Axis numbers
		const colorbar_axis = d3.axisLeft(value_to_svg)
			.tickFormat(d3.format(".0f"))

		const colorbar_g = this.svg.append("g")
			.attr("id", "colorbar")
			.attr("transform", "translate(" + top_left[0] + ', ' + top_left[1] + ")")
			.call(colorbar_axis);

		// Create the gradient
		function range01(steps) {
			return Array.from(Array(steps), (elem, index) => index / (steps-1));
		}

		const svg_defs = this.svg.append("defs");

		const gradient = svg_defs.append('linearGradient')
			.attr('id', 'colorbar-gradient')
			.attr('x1', '0%') // bottom
			.attr('y1', '100%')
			.attr('x2', '0%') // to top
			.attr('y2', '0%')
			.attr('spreadMethod', 'pad');

		gradient.selectAll('stop')
			.data(range01(10))
			.enter()
			.append('stop')
				.attr('offset', d => Math.round(100*d) + '%')
				.attr('stop-color', d => range01_to_color(d))
				.attr('stop-opacity', 1);

		// create the colorful rect
		colorbar_g.append('rect')
			.attr('id', 'colorbar-area')
			.attr('width', colorbar_size[0])
			.attr('height', colorbar_size[1])
			.style('fill', 'url(#colorbar-gradient)')
			.style('stroke', 'black')
			.style('stroke-width', '1px')
	}

	constructor(svg_element_id) {
		this.svg = d3.select('#' + svg_element_id);

		// may be useful for calculating scales
		const svg_viewbox = this.svg.node().viewBox.animVal;
		this.svg_width = svg_viewbox.width;
		this.svg_height = svg_viewbox.height;


		const population_promise = d3.csv("data/cantons-population.csv").then((data) => {

			// process the population data here

			return data;
		});

		const map_promise = d3.json("data/ch-cantons.json").then((topojson_raw) => {
			const canton_paths = topojson.feature(topojson_raw, topojson_raw.objects.cantons);
			return canton_paths.features;
		});

		const point_promise = d3.csv("data/locations.csv").then((data) => {

			// process the Instagram data here (optional)

			return data;
		});

		Promise.all([population_promise, map_promise, point_promise]).then((results) => {
			let cantonId_to_population = results[0];
			let map_data = results[1];
			let point_data = results[2];

			console.log('Data loaded')

			// Store population inside map_data
			for (let i = 0; i < map_data.length; i++) {
				for (let j = 0; j < cantonId_to_population.length; j++)
					if (map_data[i].id === cantonId_to_population[j].code) {
						map_data[i].properties.density = cantonId_to_population[j].density;
						break;
					}
			}

			// Draw the cantons
			const swiss_lat = 46.8182;
			const swiss_lon = 8.2275;
			const swiss_coords = [swiss_lon, swiss_lat];
			const swiss_scale = 8;
			const svg_center = [this.svg_width / 2, this.svg_height / 2];
			const projection = d3.geoNaturalEarth1()
												.center(swiss_coords)
												.scale(swiss_scale);
												// .translate(svg_center);
			const path = d3.geoPath(projection);

			const map = this.svg.append("path")
													.attr("d", path());

			// Draw the canton labels

			// Draw the points

			// this.makeColorbar(this.svg, color_scale, [50, 30], [20, this.svg_height - 2*30]);
		});
	}
}

function whenDocumentLoaded(action) {
	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", action);
	} else {
		// `DOMContentLoaded` already fired
		action();
	}
}

whenDocumentLoaded(() => {
	plot_object = new MapPlot('map-plot');
	// plot object is global, you can inspect it in the dev-console
});
