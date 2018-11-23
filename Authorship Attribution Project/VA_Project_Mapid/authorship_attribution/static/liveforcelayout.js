var superNode;
var forceLiveData;
var actualSliderVal = [.5, .6, .7, .8, .9]

$(function () {
    $("#force-live-slider-div").hide();
    $("#force-live-slider").on("slide", function (slideEvt) {
        clearTimeout(fwto);
        fwto = setTimeout(function () {
            fdata = []
            jsonNew = []
            for (var i = 0; i < forceLiveData['force']['results'].links.length; i++) {
                var sliderValue = actualSliderVal[+slideEvt.value]
                if (forceLiveData['force']['results'].links[i].value >= +sliderValue) {
                    fdata.push(forceLiveData['force']['results'].links[i])
                }
            }
            jsonNew['nodes'] = forceLiveData['force']['results']['nodes']
            jsonNew['links'] = fdata
            liveforceLayout(jsonNew, forceLiveData['force']['author'], forceLiveData['force']['clustering' + num_clusters])
        }, 500);
    });
});


function liveforceLayout(data, author, clusters) {
    var width = 960,
        height = 600

    var myjson = data
    console.log(myjson.nodes)
    console.log(myjson.links)

    // Change group according to clusters
    for (var i = 1; i < myjson.nodes.length; i++) {
        myjson.nodes[i]['group'] = clusters[i - 1]
    }

    colors = ["#F7412C", "#EC1562", "#9D1DB2", "#6733B9", "#3F4DB8", "#1099F9", "#009D86"]
    s_width = [.7, 1.1, 1.5, 1.9, 2.3]
    s_opacity = [.2, .4, .6, .8, 1.0]

    $("#force-live").html("");
    $("#force-live-slider-div").show();
    var svg_force_live = d3.select("#force-live").append("svg")
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
        return 300 * link.value;
    });

    var link = svg_force_live.selectAll(".link")
        .data(json.links)
        .enter().append("line")
        .attr("stroke", function (d) {
            return "#6539AA"
        })
        .attr("stroke-opacity", function (d) {
            if (d.value === 1) {
                return s_opacity[4]
            } else if (d.value > .98) {
                return s_opacity[3]
            } else if (d.value > .89) {
                return s_opacity[2]
            } else if (d.value > .79) {
                return s_opacity[1]
            } else if (d.value > .7) {
                return s_opacity[0]
            }
        }).attr("stroke-width", function (d) {
            if (d.value === 1) {
                return s_width[4]
            } else if (d.value > .98) {
                return s_width[3]
            } else if (d.value > .89) {
                return s_width[2]
            } else if (d.value > .79) {
                return s_width[1]
            } else if (d.value > .7) {
                return s_width[0]
            }
        }).attr("class", "link");

    var node = svg_force_live.selectAll(".node")
        .data(json.nodes)
        .enter().append("g")
        .attr("class", "node")
        .call(force.drag);


    node.append("circle")
        .attr("r", 10)
        .attr("fill", function (d, i) {
            if (author.indexOf(d["name"]) === -1) {
                return "#FF5722";
            }
            else return "#ffffffff";
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