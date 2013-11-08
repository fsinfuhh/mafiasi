$(function() {
    var graph = $('#pks-graph');
    var graphscroll = $('#pks-graphscroll');
    var graphthumb = $('#pks-graph-thumb');
    var graphselector = $('#pks-graphselector');
    
    
    function rescaleElements() { 
        graphscroll.css('height', $(window).height() - graphscroll.offset().top - $('#footer').height());
        graphselectorWidth = graphthumb.width() / (graph.width() / graphscroll.innerWidth());
        graphselectorHeight = graphthumb.height() / (graph.height() / graphscroll.innerHeight());
        graphselector.css({
            "width": graphselectorWidth,
            "height": graphselectorHeight,
            "top": (graphthumb.height() - graphselectorHeight) / 2,
            "left": (graphthumb.width() - graphselectorWidth) / 2
        });
    }

    function initialize() {
        var origGraphSize = {
            "width": graph.width(),
            "height": graph.height()
        };
        graph.css({
            "width": origGraphSize.width * 0.80,
            "height": origGraphSize.height * 0.80
        });
        rescaleElements();
        graphscroll.scrollTop((graph.height() - graphscroll.height()) / 2);
        graphscroll.scrollLeft((graph.width() - graphscroll.width()) / 2);
    }
    
    $(window).load(initialize);
    $(window).resize(rescaleElements);
    
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

    function handleGraphthumbAction(posX, posY) {
        var maxScrollLeft = graphscroll[0].scrollWidth - graphscroll[0].clientWidth;
        var maxScrollTop = graphscroll[0].scrollHeight - graphscroll[0].clientHeight;
        var percLeft = posX / (graphthumb.width() - graphselector.width());
        var percTop = posY / (graphthumb.height() - graphselector.height());
        graphscroll.scrollLeft(percLeft * maxScrollLeft);
        graphscroll.scrollTop(percTop * maxScrollTop);
    }
    graphselector.draggable({
        "containment": "parent",
        "drag": function(ev, ui) {
            handleGraphthumbAction(ui.position.left, ui.position.top);
        },
        "start": function(ev, ui) {
            graphscroll.unbind("scroll");
        },
        "stop": function(ev, ui) {
            graphscroll.scroll(handleGraphscroll);
        }
    });

    graphthumb.click(function(ev) {
        var offset = graphthumb.offset()
        var posX = ev.clientX - offset.left - (graphselector.width() / 2);
        var posY = ev.clientY - offset.top - (graphselector.height() / 2);
        handleGraphthumbAction(posX, posY, true);
    });
});
