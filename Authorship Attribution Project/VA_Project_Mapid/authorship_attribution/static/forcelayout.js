var superNode;
var forceLayoutData;
var fwto;

$(function () {
    $("#force-layout-slider-div").hide();
    $("#force-layout-slider").on("slide", function (slideEvt) {
        clearTimeout(fwto);
        fwto = setTimeout(function () {
            fdata = []
            jsonNew = []
            for (var i = 0; i < forceLayoutData['results'].links.length; i++) {
                var sliderValue = actualSliderVal[+slideEvt.value]
                if (forceLayoutData['results'].links[i].value >= +sliderValue) {
                    fdata.push(forceLayoutData['results'].links[i])
                }
            }
            jsonNew['nodes'] = forceLayoutData['results']['nodes']
            jsonNew['links'] = fdata
            forceLayout(jsonNew, forceLayoutData['author'])
        }, 500);
    });
});

function forceLayout(data, author) {
    console.log("data " + data)
    var width = 960,
        height = 600

    var myjson = data
    console.log(myjson.nodes)
    console.log(myjson.links)

    s_width = [.5, 1.3, 2.1, 3.0, 4.5]
    s_opacity = [.2, .4, .6, .8, 1.0]


    $("#force-layout").html("");
    $("#force-layout-slider-div").show();
    var svg = d3.select("#force-layout").append("svg")
        .attr("width", width)
        .attr("height", height);

    var force = d3.layout.force()
        .gravity(0.05)
        .distance(200)
        .charge(-100)
        .size([width, height]);

    json = data; //add this line

    force
        .nodes(json.nodes)
        .links(json.links)
        .start();

    force.linkDistance(function (link) {
        console.log(link.value)
        return 100 * link.value;
    });

    var link = svg.selectAll(".link")
        .data(json.links)
        .enter().append("line")
        .attr("stroke", function (d) {
            return "#6539AA"
        })
        .attr("stroke-opacity", function (d) {
            if (d.value === .9) {
                return s_opacity[4]
            } else if (d.value > .88) {
                return s_opacity[3]
            } else if (d.value > .76) {
                return s_opacity[2]
            } else if (d.value > .68) {
                return s_opacity[1]
            } else if (d.value > .6) {
                return s_opacity[0]
            }
        }).attr("stroke-width", function (d) {
            if (d.value === .9) {
                return s_width[4]
            } else if (d.value > .88) {
                return s_width[3]
            } else if (d.value > .76) {
                return s_width[2]
            } else if (d.value > .68) {
                return s_width[1]
            } else if (d.value > .6) {
                return s_width[0]
            }
        }).attr("class", "link");

    var node = svg.selectAll(".node")
        .data(json.nodes)
        .enter().append("g")
        .attr("class", "node")
        .call(force.drag);


    node.append("circle")
        .attr("r", 10)
        .attr("fill", function (d) {
            return author.indexOf(d["name"]) === -1 ? "#6539AA" : "#ffffffff"
        })
        .attr("x", -8)
        .attr("y", -8)
        .attr("width", 16)
        .attr("height", 16);

    node.append("image")
        .attr("xlink:href", function (d) {
            if (author.indexOf(d["name"]) > -1) {
                return "https://upload.wikimedia.org/wikipedia/commons/3/38/Wikipedia_User-ICON_byNightsight.png";
            }
        })
        .attr("x", -8)
        .attr("y", -8)
        .attr("width", 16)
        .attr("height", 16);


    superNode = node

    node.append("text")
        .attr("dx", 12)
        .attr("dy", ".35em")
        .text(function (d) {
            return d.name
        });

    force.on("tick", function () {
        link.attr("x1", function (d) {
            return d.source.x;
        })
            .attr("y1", function (d) {
                return d.source.y;
            })
            .attr("x2", function (d) {
                return d.target.x;
            })
            .attr("y2", function (d) {
                return d.target.y;
            });

        node.attr("transform", function (d) {
            return "translate(" + d.x + "," + d.y + ")";
        });
    });

}