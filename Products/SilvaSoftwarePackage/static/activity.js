
(function($, RGraph) {
    $(document).ready(function () {
        $('.activity-graph').each(function() {
            var values = $(this).data('values'),
                maximum = Math.max.apply(Math.max, values) + 1,
                activity = new RGraph.Line(this, values);
            activity.Set('chart.linewidth', 3);
            activity.Set('chart.hmargin', 5);
            activity.Set('chart.spline', 1);
            activity.Set('chart.noaxes', true);
            activity.Set('chart.variant', true);
            activity.Set('chart.ymin', 0);
            activity.Set('chart.ymax', maximum);
            activity.Set('chart.ylabels.count', Math.min(maximum, 5));
            activity.Set('chart.background.grid.autofit.numhlines', Math.min(maximum, 5));
            activity.Draw();
        });
    });
})(jQuery, RGraph);
