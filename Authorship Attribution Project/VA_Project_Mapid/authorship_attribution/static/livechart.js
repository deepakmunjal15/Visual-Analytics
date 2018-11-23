/**
 * Created by mj on 11/18/2017.
 */
var margin = {top: 40, right: 20, bottom: 30, left: 100},
    width = 1000 - margin.left - margin.right,
    height = 400 - margin.top - margin.bottom;

var x = d3.scale.ordinal()
        .rangeRoundBands([0, width - 150], .1),
    y = d3.scale.linear()
        .rangeRound([height, 0]);

var svg_bar, xAxis_bar, yAxis_bar, xAxisG_bar, yAxisG_bar;
$(function () {

    $('ul.sidebar-comp').find('a').click(function () {
        var $href = $(this).attr('href');
        var $anchor = $('#' + $href).offset();
        $('body').animate({scrollTop: $anchor.top});
        return false;
    });

    svg_bar = d3.select("#barchart").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform",
            "translate(" + margin.left + "," + margin.top + ")");

    xAxis_bar = d3.svg.axis()
        .scale(x)
        .orient("bottom");
    yAxis_bar = d3.svg.axis()
        .scale(y)
        .orient("left");

    xAxisG_bar = svg_bar.append("g")
        .attr("class", "x_axis")
        .attr("transform", "translate(0," + height + ")");
    yAxisG_bar = svg_bar.append("g")
        .attr("class", "y_axis");
});

var update = function (data) {

    data = d3.entries(data);

    // Reset the axes domains with new data
    x.domain(data.map(function (d) {
        return d['key'];
    }));
    y.domain([0, d3.max(data, function (d) {
        return d['value'];
    })]);

    xAxisG_bar
        .transition()
        .duration(500)
        .call(xAxis_bar);


    yAxisG_bar
        .transition()
        .duration(500)
        .call(yAxis_bar);

    var bars_live = svg_bar.selectAll("rect")
        .data(data, function (d) {
            return d['key'];
        });

    bars_live
        .transition()
        .duration(500)
        .style("fill", "#0D47A1")
        .attr("x", function (d) {
            return x(d['key']);
        })
        .attr("width", x.rangeBand())
        .attr("y", function (d) {
            return y(d['value']);
        })
        .attr("height", function (d) {
            return height - y(d['value']);
        });

    bars_live
        .enter()
        .append("rect")
        .style("fill", "#0D47A1")
        .attr("width", x.rangeBand())
        .attr("x", 0)
        .attr("x", function (d) {
            return x(d['key']);
        })
        .attr("y", y(0))
        .attr("height", 0)
        .style("opacity", 0)
        .transition()
        .duration(500)
        .attr("y", function (d) {
            return y(d['value']);
        })
        .attr("height", function (d) {
            return height - y(d['value']);
        }).style("opacity", 1);

    // EXIT
    bars_live
        .exit()
        .transition()
        .duration(500)
        .style("fill", "#0D47A1")
        .style("opacity", 0)
        .remove();
};

