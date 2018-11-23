var ngram3, ngram4;
var svg, m_bar_data, m_author_names;

function updateBar() {
    var updatedData = [];
    $('#bar-checkbox :checked').each(function () {
        updatedData.push(m_bar_data[+$(this).val()])

    });
    barChart(updatedData, m_author_names, true, false);
}

function barChart(data, author_names, fromCheckBox, fromRadio) {

    var margin = {top: 20, right: 30, bottom: 130, left: 60},
        width = 960 - margin.left - margin.right,
        height = 600 - margin.top - margin.bottom;

    if (fromRadio) {
        data = d3.entries(data);
        m_bar_data = data
    }

    if (fromCheckBox) {
        svg.selectAll("*")
            .attr("fill-opacity", 1)
            .attr("stroke-opacity", 1)
            .transition()
            .duration(500)
            .attr("fill-opacity", 0)
            .attr("stroke-opacity", 0).remove();
    } else {
        d3.select("#barcharts").selectAll("svg").remove();
        data = d3.entries(data);
        m_bar_data = data
        m_author_names = author_names
        svg = d3.select("#barcharts").append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("svg:g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

        var html = "";
        for (var i = 0; i < data.length; i++) {
            html += '<label><input type="checkbox" name="checkdocs" value="' + i + '" checked>D' + (i + 1) + '</label>&nbsp;&nbsp;&nbsp;'
        }
        $('.checkbox').html(html);

        html = "ngrams : ";
        var checked;
        for (i = 3; i < 5; i++) {
            if (i === 3)
                checked = 'checked'
            else checked = ''
            html += '<label class="radio-inline"><input type="radio" name="ngramsradio" value="' + i +
                '" ' + checked + '>' + i + '</label>'
        }
        $('.radio-ngrams').html(html);


        $('#bar-checkbox input').click(updateBar);

        // Bar Listener
        $('input[type=radio][name=ngramsradio]').change(function () {
            if (+this.value === 3) {
                m_bar_data = ngram3
            }
            else if (+this.value === 4) {
                m_bar_data = ngram4

            }
            $('input[name=checkdocs]').prop('checked', true);
            barChart(m_bar_data, m_author_names, true, true);

        });

    }

    var y = d3.scale.linear()
        .domain([0, 1])
        .range([height, 0]);

    var x0 = d3.scale.ordinal()
        .domain(d3.range(data[0]['value'].length))
        .rangeBands([0, width], .2);

    var x1 = d3.scale.ordinal()
        .domain(d3.range(data.length))
        .rangeBands([0, x0.rangeBand()]);

    var z = d3.scale.category10();

    var xAxis = d3.svg.axis()
        .scale(x0)
        .orient("bottom")
        .tickFormat(function (d, i) {
            return author_names[i]
        });

    var yAxis = d3.svg.axis()
        .scale(y)
        .orient("left");

    //

    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis);

    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis).selectAll("text")
        .style("text-anchor", "end")
        .attr("dx", "-.8em")
        .attr("dy", ".15em")
        .attr("transform", function (d) {
            return "rotate(-55)"
        });

    svg.append("g").selectAll("g")
        .data(data)
        .enter().append("g")
        .style("fill", function (d, i) {
            return z(i);
        })
        .attr("transform", function (d, i) {
            return "translate(" + x1(i) + ",0)";
        })
        .selectAll("rect")
        .data(function (d) {
            return d['value'];
        })
        .enter().append("rect")
        .attr("width", x1.rangeBand())
        .attr("height", y)
        .attr("x", function (d, i) {
            return x0(i);
        })
        .attr("y", function (d) {
            return height - y(d);
        }).attr("fill-opacity", 0)
        .attr("stroke-opacity", 0)
        .transition()
        .duration(500)
        .attr("fill-opacity", 1)
        .attr("stroke-opacity", 1)
}