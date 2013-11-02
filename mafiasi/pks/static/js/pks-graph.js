$(function() {
    var graph = $('#pks-graph');
    var graphscroll = $('#pks-graphscroll');
    var graphthumb = $('#pks-graph-thumb');
    var graphselector = $('#pks-graphselector');
    
    var origGraphSize = {
        "width": graph.width(),
        "height": graph.height()
    };
    graph.css({
        "width": origGraphSize.width * 0.80,
        "height": origGraphSize.height * 0.80
    });
    
    function rescaleElements() { 
        graphscroll.css('height', $(window).height() - graphscroll.offset().top - $('#footer').height());
    }
    rescaleElements();
    $(window).resize(rescaleElements);
    graphscroll.scrollTop((graph.height() - graphscroll.height()) / 2);
    graphscroll.scrollLeft((graph.width() - graphscroll.width()) / 2);
    
    function handleGraphscroll(ev) {
        var maxScrollLeft = graphscroll[0].scrollWidth - graphscroll[0].clientWidth;
        var maxScrollTop = graphscroll[0].scrollHeight - graphscroll[0].clientHeight;
        var maxPosLeft = graphthumb.width() - graphselector.width();
        var maxPosTop = graphthumb.height() - graphselector.height();
        var posLeft = graphscroll.scrollLeft() / maxScrollLeft * maxPosLeft;
        var posTop = graphscroll.scrollTop() / maxScrollTop * maxPosTop;
        graphselector.css({
            "left": posLeft,
            "top": posTop
        });
    }
    graphscroll.scroll(handleGraphscroll);

    graphselectorWidth = 0.20 * graphthumb.width();
    graphselectorHeight = graph.height() / graph.width() * graphselectorWidth;
    graphselector.draggable({
        "containment": "parent",
        "drag": function(ev, ui) {
            var percLeft = ui.position.left / graphthumb.width();
            var percTop = ui.position.top / graphthumb.height();
            graphscroll.scrollLeft(percLeft * graph.width());
            graphscroll.scrollTop(percTop * graph.height());
        },
        "start": function(ev, ui) {
            graphscroll.unbind("scroll");
        },
        "stop": function(ev, ui) {
            graphscroll.scroll(handleGraphscroll);
        }
    }).css({
        "width": graphselectorWidth,
        "height": graphselectorHeight,
        "top": (graphthumb.height() - graphselectorHeight) / 2,
        "left": (graphthumb.width() - graphselectorWidth) / 2
    });
});
