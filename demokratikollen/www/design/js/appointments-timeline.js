demokratikollen.graphics.AppointmentsTimeline = function() {

  var rowHeight = 40,
    lineOffsetY = 10,
    margin = { top: 40, right: 0, bottom: 5, left: 0 },
    rowLabelsMarginLeft = 10,
    timeUnit = d3.time.year,
    tickLabelWidth = 100,
    tipHtml = null,
    markerSize = 4,
    cssClass = "timeline",
    hoverLinesWidth = rowHeight - 15;

  function getMinDate(blocks) { 
    return d3.min(blocks, function (block) { return block.startDate; });
  }

  function getMaxDate(blocks) { 
    return d3.max(blocks, function (block) { return block.endDate; });
  }

  function ordering(rowA, rowB) {
    // rowA and rowB are arrays of data entries
    maxDates = [getMaxDate(rowA.values), getMaxDate(rowB.values)];
    if (maxDates[0] != maxDates[1]) {
      return maxDates[1] - maxDates[0];
    } else {
      return getMinDate(rowB.values) - getMinDate(rowA.values);
    }

  }

  function unique(arr) {
    return arr.reduce(function(collected, current) {
      if (collected.indexOf(current) < 0) collected.push(current);
      return collected;
    }, []);
  };

  function chart(selection) {
    selection.each(function(data) {

      dataByRowLabel = d3.nest()
        .key(function(d) { return d.rowLabel; })
        .entries(data);
      dataByRowLabel.sort(ordering);


      var rowLabels = dataByRowLabel.map(function(d) { return d.key; }),
        minDate = getMinDate(data),
        maxDate = getMaxDate(data);

      
      d3.select(this).classed("chart", true);

      var width = this.getBoundingClientRect().width - margin.left - margin.right,
          height = rowLabels.length * rowHeight;

      var svg = d3.select(this)
        .append("svg")
        .classed(cssClass, true)
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

      svg.append("rect")
        .attr("width", width)
        .attr("height", height)
        .classed("background", true);

      var x = d3.time.scale()
        .domain([minDate, maxDate])
        .range([0, width])
        .nice(timeUnit);

      var y = d3.scale.ordinal()
        .domain(rowLabels)
        .rangePoints([0, height], 1);

      var tickValues = x.ticks(Math.floor(width / tickLabelWidth));

      tickValues = unique(tickValues.map(timeUnit.floor));

      var xAxis = d3.svg.axis()
        .scale(x)
        .orient("top")
        .tickSize(-height, 0)
        .tickValues(tickValues);

      xAxis = svg.append("g")
        .classed("axis x", true)
        .call(xAxis);
      xAxis.selectAll("text")
        .style("text-anchor", "start");
      
      svg.append("g")
        .classed("rowLabels", true)
        .selectAll("rowLabels")
        .data(rowLabels)
        .enter()
        .append("text")
        .text(function(d) { return d; })
        .attr("transform", function(d) { return "translate(" + rowLabelsMarginLeft +"," + y(d) + ")"; });

      var line = d3.svg.line()
        .x(function(d) { return x(d[0]); })
        .y(function(d) { return y(d[1]); });

      linesSelection = svg.append("g")
        .attr("transform", function(d) { return "translate(0," + lineOffsetY + ")"; })
        .classed("lines", true)
        .selectAll("lines")
        .data(data)
        .enter();

      lines = linesSelection.append("path")
        .attr("d", function(d) { 
          return line([[d.startDate, d.rowLabel], [d.endDate, d.rowLabel]]); 
        })
        .attr("class", function(d) { return d.cssClass || ""; });

      linesSelection.append("circle")
        .attr("cx", function(d) { return x(d.startDate); })
        .attr("cy", function(d) { return y(d.rowLabel); })
        .attr('r', markerSize);

      linesSelection.append("circle")
        .attr("cx", function(d) { return x(d.endDate); })
        .attr("cy", function(d) { return y(d.rowLabel); })
        .attr('r', markerSize);


      if (tipHtml) {
        tip = d3.tip()
        .attr('class', 'd3-tip timeline')
        .direction(function(d) {
          var startX = x(d.startDate),
            endX = x(d.endDate),
            lineMidX = (startX + endX) / 2,
            figMidX = width/2;

          if (startX <= figMidX && figMidX <= endX) { 
            // Line covers middle of figure.
            return 's';
          } else if (startX >= figMidX) { 
            // Line is right of middle of figure.
            return 'sw';
          } else if (endX <= figMidX) { 
            // Line is left of middle of figure.
            return 'se';
          }
        })
        .offset(function(d) {
          var startX = x(d.startDate),
            endX = x(d.endDate),
            lineMidX = (startX + endX) / 2,
            figMidX = width/2;

          if (startX <= figMidX && figMidX <= endX) { 
            // Line covers middle of figure. Move tooltip to fig middle.
            return [hoverLinesWidth/2+1, figMidX-lineMidX]; 
          } else if (startX >= figMidX) { 
            // Line is right of middle of figure.
            return [hoverLinesWidth/2+1, -hoverLinesWidth/3];
          } else if (endX <= figMidX) { 
            // Line is left of middle of figure.
            return [hoverLinesWidth/2+1, hoverLinesWidth/3];
          }
        })
        .html(tipHtml);

        linesSelection.append("path")
          .style("stroke", "rgba(0,0,0,0)")
          .style("stroke-width", hoverLinesWidth)
          .attr("d", function(d) { return line([[d.startDate, d.rowLabel], [d.endDate, d.rowLabel]]); })
          .call(tip)
          .on('mouseover', tip.show)
          .on('mouseout', tip.hide);
      }
        

    });
  }

  chart.tipHtml = function(value) {
    if (!arguments.length) return tipHtml;
    tipHtml = value;
    return chart;
  };

  chart.timeUnit = function(value) {
    if (!arguments.length) return timeUnit;
    timeUnit = value;
    return chart;
  };

  chart.tickLabelWidth = function(value) {
    if (!arguments.length) return tickLabelWidth;
    tickLabelWidth = value;
    return chart;
  };

  return chart;
}