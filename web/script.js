var url = window.location.toString(),
    query_string = url.replace(/\//g,'').split("?");

var moneyFormat = d3.format("$,d"),
    commaFormat = d3.format(",");

var colors = d3.scaleOrdinal(d3.schemeCategory10);
var bisectDate = d3.bisector(function(d) { return d.time; }).left

d3.csv("data/tweets_per_minute.csv", type, function(error, data) {
  if (error) throw error;

  var lines = data.columns.slice(2).map(function(id, count) {
    return {
      id: id.replace("_", " "),
      values: data.map(function(d) {
        return {time: d.time, quantity: d[id]};
      }),
      lineColor: colors(count) //storing this so we can label the coresponding current boxes above chart
    };
  });

  //update the current price tickers at the top
  for (var i=0; i<lines.length; i++){
    var my_line = lines[i],
        label = my_line.id,
        firstWord = label.split(" ")[0];

    if(firstWord !== "listing"){ //TODO add listings line
      my_line.formatter = moneyFormat;
    } else {
      my_line.formatter = commaFormat;
      firstWord = "listings";
      label = "listings";
    }
    var $topBox = d3.select("#"+firstWord +"-ticker-box");
    $topBox.html("Current "+ label + ": "+ my_line.formatter(my_line.values[my_line.values.length-1].quantity));
    $topBox.style("border-bottom", "3px solid "+my_line.lineColor); //match colors to the lines
  }
  drawChart([lines[0], lines[1]]); //average/lowest price
  drawChart([lines[2]]); //highest price


  function drawChart(lines){
    var svg, g, margin = {}, width, height;
    //get dimensions based on window size
    updateDimensions(window.innerWidth);

    svg = d3.select('#charts').append('svg')
      .attr('width', width + margin.right + margin.left)
      .attr('height', height + margin.top + margin.bottom);

    g = svg.append("g");
    g.attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

    var formatMillisecond = d3.timeFormat(".%L"),
        formatSecond = d3.timeFormat(":%S"),
        formatMinute = d3.timeFormat("%-I:%M %p"),
        formatHour = d3.timeFormat("%-I %p"),
        formatDay = d3.timeFormat("%a %d"),
        formatWeek = d3.timeFormat("%b %d"),
        formatMonth = d3.timeFormat("%B"),
        formatYear = d3.timeFormat("%Y");

    function multiFormat(date) { //to display the new date at midnight, new month on the 1st, etc. Returns the first one that is true
      return (d3.timeSecond(date) < date ? formatMillisecond
          : d3.timeMinute(date) < date ? formatSecond
          : d3.timeHour(date) < date ? formatMinute
          : d3.timeDay(date) < date ? formatHour
          : d3.timeMonth(date) < date ? (d3.timeWeek(date) < date ? formatDay : formatWeek)
          : d3.timeYear(date) < date ? formatMonth
          : formatYear)(date);
    }



    var x = d3.scaleTime().range([0, width]),
        y = d3.scaleLinear().range([height, 0]),
        z = d3.scaleOrdinal(d3.schemeCategory10);


    var line = d3.line()
        //.curve(d3.curveBasis)
        .x(function(d) { return x(d.time); })
        .y(function(d) { return y(d.quantity); });

    x.domain(d3.extent(data, function(d) { return d.time; }));

    y.domain([
      d3.min(lines, function(c) { return d3.min(c.values, function(d) { return d.quantity; }); }),
      d3.max(lines, function(c) { return d3.max(c.values, function(d) { return d.quantity; }); })
    ]);

    z.domain(lines.map(function(c) { return c.id; }));

    var fullTimestampFormat = d3.timeFormat("%-I:%M %p %A, %b. %-d, %Y");
    d3.select("#last-updated").html("Last updated: "+fullTimestampFormat(x.domain()[1])); //this doesn't really need to run for each chart but whatever

    var xAxis = d3
        .axisBottom(x)
        .tickFormat(multiFormat);

    if(width <= 500){ //mobile
      xAxis.ticks(5);
    }


    var yAxis = d3
      .axisLeft(y)
      .tickFormat(moneyFormat);
  
    g.append("g")
        .attr("class", "axis axis--x")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

    g.append("g")
        .attr("class", "axis axis--y")
        .call(yAxis)
      .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", "0.71em");
        //.attr("fill", "#000")
        //.text("quantity in dollars");

    var category = g.selectAll(".category")
      .data(lines)
      .enter().append("g")
        .attr("class", "category");

    category.append("path")
        .attr("class", "line")
        .attr("d", function(d) { return line(d.values); })
        .style("stroke", function(d) { return d.lineColor; });

    category.append("text")
        .datum(function(d) { return {id: d.id, value: d.values[d.values.length - 1]}; })
        .attr("transform", function(d) { return "translate(" + x(d.value.time) + "," + y(d.value.quantity) + ")"; })
        .attr("x", 3)
        .attr("dy", "0.35em")
        .style("font", "10px sans-serif")
        .text(function(d) { return d.id; });


    var focus = category.append("g")
        .attr("class", "focus")
        .style("display", "none");

    focus.append("line")
        .attr("class", "x-hover-line hover-line")
        .attr("y1", 0)
        .attr("y2", height);

    focus.append("line")
        .attr("class", "y-hover-line hover-line");

    focus.append("circle")
        .attr("r", 7.5);

    focus.append("text")
        .attr("x", 15)
        .attr("dy", ".31em");


    svg.append("rect") //hotspot to trigger mouseover on lines when mousing over whole chart
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
        .attr("class", "overlay")
        .attr("width", width)
        .attr("height", height)
        .on("mouseover", function() { focus.style("display", null); })
        .on("mouseout", function() { focus.style("display", "none"); })
        .on("mousemove", mousemove);

    function mousemove() {
        var x0 = x.invert(d3.mouse(this)[0]), //convert mouse x to its equivalent on time value on the x axis
            i = bisectDate(lines[0].values, x0, 1), //find the insertion index for theoretical point x0 into the data array. Using line[0] because all lines share x axis point
            d0 = function(line){ return line.values[i - 1]; }, //data point to the left of bisector index in the array
            d1 = function(line){ return line.values[i]; }, //data point to the right of the bisector index in the data array
            closest = x0 - d0.time > d1.time - x0 ? d1 : d0; // determine which point is closer to the target value and use that

        focus.attr("transform", function(d) {var line = closest(d); return "translate(" + x(line.time) + "," + y(line.quantity) + ")"; }); //place the focus circle
        focus.select("text").text(function(d) { return d.formatter(closest(d).quantity); }) //label it
          .attr("dy", "-15");
        focus.select(".x-hover-line").attr("y2", function(d){ return height - y(closest(d).quantity)}) //draw dashed line to x axis
        focus.select(".y-hover-line").attr("x1", function(d){ return -1 * x(closest(d).time)}).attr("x2", 0); //draw dashed line to y axis - I guess bc we are in .mousemove() 0 is our current mouse xPos
        focus.selectAll(".hover-line").style("stroke", function(d){ return d.lineColor }); 
        focus.select("circle").style("stroke", function(d){ return d.lineColor});
    }

    function updateDimensions(winWidth) {
      margin.top = 20;
      margin.right = 80;
      margin.left = 50;
      margin.bottom = 30;
      width = winWidth - margin.left - margin.right;
      height = 350 - margin.top - margin.bottom;
    }

  }//draw chart
});


function type(d, _, columns) {
  //d.time = parseTime(d.time);
  var tmpDate = Date.parse(d.time);
  var myDate = new Date(tmpDate - (5*60*60000)); //5 hours = 5 * 60 minutes * 60000 milliseconds
  d.time = myDate;

  for (var i = 1, n = columns.length, c; i < n; ++i) d[c = columns[i]] = +d[c];
  return d;
}

</script>

