

var margin = {top: 20, right: 120, bottom: 20, left: 220},
    width = 960 - margin.right - margin.left,
    height = 800 - margin.top - margin.bottom;

var i = 0,
    duration = 750,
    root;

var tree = d3.layout.tree()
    .size([height, width])

var diagonal = d3.svg.diagonal()
    .projection(function(d) { return [d.y, d.x]; });

// defines where on our webpage (now, "body") the viz appears
var svg = d3.select("#map_viz").append("svg:svg")
    .attr("width", width + margin.right + margin.left)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

// var color = d3.scale.category20b();
var color = d3.scale.ordinal()
    .range(['rgb(84,48,5)','rgb(140,81,10)','rgb(191,129,45)','rgb(223,194,125)','rgb(246,232,195)','rgb(245,245,245)','rgb(199,234,229)','rgb(128,205,193)','rgb(53,151,143)','rgb(1,102,94)','rgb(0,60,48)']);

d3.json("/map_info.json", function(error, mapData) {
  if (error) throw error;

  root = mapData;
  root.x0 = height / 2;
  root.y0 = 0;

  function collapse(d) {
    if (d.children) {
      d._children = d.children;
      d._children.forEach(collapse);
      d.children = null;
    }
  }

  root.children.forEach(collapse);
  update(root);
});

d3.select(self.frameElement).style("height", "800px");

function update(source) {

  // Compute the new tree layout.
  var nodes = tree.nodes(root).reverse(),
    links = tree.links(nodes);

  // Normalize for fixed-depth.
  nodes.forEach(function(d) { d.y = d.depth * 180; });

  // Update the nodes…
  var node = svg.selectAll("g.node")
      .data(nodes, function(d) { return d.id || (d.id = ++i); });

  // Enter any new nodes at the parent's previous position.
  var nodeEnter = node.enter().append("g")
      .attr("class", "node")
      .attr("transform", function(d) { return "translate(" + source.y0 + "," + source.x0 + ")"; })
      .on("click", click)
// Tooltip - style more in CSS using text.info selector
      .on("mouseover", function(d) {
      var g = d3.select(this); // The node
      // The class is used to remove the additional text later
      var info = g.append('text')
         .classed('info', true)
         .attr('x', 20)
         .attr('y', 10)
         .text('More info');
  })
  .on("mouseout", function() {
      // Remove the info text on mouse out.
      d3.select(this).select('text.info').remove();
  });

  nodeEnter.append("circle")
      .attr("r", function(d) { return d.value; })
      .style("fill", function (d) {
        return color(d.industry);
      });


  nodeEnter.append("text")
      .attr("x", function(d) { return d.children || d._children ? (d.value + 4) * -1 : d.value + 4 })
      .attr("dy", ".35em")
      .attr("text-anchor", function(d) { return d.children || d._children ? "end" : "start"; })
      .text(function(d) { return d.name; })
      .style("fill-opacity", 1e-6);

  // Transition nodes to their new position.
  var nodeUpdate = node.transition()
      .duration(duration)
      .attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; });

  nodeUpdate.select("circle")
      .attr("r", function(d) { return d.value; })
      .style("opacity", function(d) { return d._children || d.children ? 1 : 0.5 });

  nodeUpdate.select("text")
      .style("fill-opacity", 1);


  // Transition exiting nodes to the parent's new position.
  var nodeExit = node.exit().transition()
      .duration(duration)
      .attr("transform", function(d) { return "translate(" + source.y + "," + source.x + ")"; })
      .remove();

  nodeExit.select("circle")
      .attr("r", 1e-6);

  nodeExit.select("text")
      .style("fill-opacity", 1e-6);

  // Update the links…
  var link = svg.selectAll("path.link")
      .data(links, function(d) { return d.target.id; });

  // Enter any new links at the parent's previous position.
  link.enter().insert("path", "g")
      .attr("class", "link")
      .attr("d", function(d) {
        var o = {x: source.x0, y: source.y0};
        return diagonal({source: o, target: o});
      })
      .attr("stroke-width", function(d) {
        return 2 * (d.target.value);
      })
      .attr("stroke", function (d) {
        return color(d.target.industry);
      })
// come back to figure out how to get circle to append to link instead of be part of link
  // link.insert("circle", "g")
  //     .attr("r", function (d) {
  //       return d.target.value;
  //     })
  //     .attr ("cx", function (d){
  //       return d.source.x0;
  //     })
  //     .attr("cy", function (d) {
  //       return d.source.y0;
  //     });

  // Transition links to their new position.
  link.transition()
      .duration(duration)
      .attr("d", diagonal);

  // Transition exiting nodes to the parent's new position.
  link.exit().transition()
      .duration(duration)
      .attr("d", function(d) {
        var o = {x: source.x, y: source.y};
        return diagonal({source: o, target: o});
      })
      .remove();

  // Stash the old positions for transition.
  nodes.forEach(function(d) {
    d.x0 = d.x;
    d.y0 = d.y;
  });
}

// Toggle children on click.
function click(d) {
  if (d.children) {
    d._children = d.children;
    d.children = null;
  } else {
    d.children = d._children;
    d._children = null;
  }
  update(d);
}
