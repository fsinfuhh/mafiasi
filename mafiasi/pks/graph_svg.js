document.addEventListener("DOMContentLoaded", function() {
	var edge_backup = {};
	var edges = document.querySelectorAll('g[class="edge"]');
	for (var i = 0; i < edges.length; i++) {
		var edge = edges[i];
		var path = edge.querySelector('path');
		edge_backup[edge.getAttribute("id")] = {
			"color": path.getAttribute("stroke"),
            "width": path.getAttribute("stroke-width")
		};
	}
	
	var edge_re = /^([A-F0-9]{16})_([A-F0-9]{16})$/
	var nodes = document.querySelectorAll('g[class="node"]');
	for (var i = 0; i < nodes.length; i++) {
		var node = nodes[i];
		node.addEventListener("click", function(ev) {
			var keyid = ev.currentTarget.getAttribute("id");
			for(var j = 0; j < edges.length; j++) {
				var edge = edges[j];
				var conn = edge.getAttribute("id").match(edge_re);
				if (conn == null) {
					continue;
				}
				var signer_keyid = conn[1];
				var signed_keyid = conn[2];
				
				var path = edge.querySelector('path');		
				var polygons = edge.querySelectorAll('polygon');

				var attrs = {}
				if (keyid == signer_keyid || keyid == signed_keyid) {
					attrs["color"] = "#00d";
                    attrs["width"] = 3;
				} else {
					var edge_id = edge.getAttribute("id");
					attrs["color"] = edge_backup[edge_id]["color"];
					attrs["width"] = edge_backup[edge_id]["width"];
				}
				path.setAttribute("stroke", attrs["color"]);
                path.setAttribute("stroke-width", attrs["width"]);
				for (var k = 0; k < polygons.length; k++) {
					var polygon = polygons[k];
					polygon.setAttribute("stroke", attrs["color"]);
					polygon.setAttribute("fill", attrs["color"]);
				}
			}
		}, false);
	}
}, false);
