var $srtopology = (function () {
    console.log(topology);
    var container = document.getElementById("topology");
    const data_nodes = [];
    const data_links = [];

    for (let i = 0; i < topology.nodes.length; i++) {
        var node_data = {
            id: topology.nodes[i].node_id,
            label: topology.nodes[i].attributes.bgp_ls.node_name
        }
        data_nodes.push(node_data);

        for (let l = 0; l < topology.nodes[i].links.length; l++) {
            var a = topology.nodes[i].links[l].remote_node_descriptors.autonomous_system;
            var b = topology.nodes[i].links[l].remote_node_descriptors.router_id;
            var s = `${a}:${b}`;

            var link_data = {
                from: topology.nodes[i].node_id,
                to: s,
                arrows: "to",
                label: `Metric: ${topology.nodes[i].links[l].attributes.bgp_ls.igp_metric}`,
                smooth: { enabled: true, type: 'discrete', roundness: 0.1 },
                font: {
                    size: 24,
                    color: '#9E9E9E',
                    strokeColor: '#E3E3E3'
                }
            }

            console.log(a, b, s);

            data_links.push(link_data);
        }
    }

    var nodes = new vis.DataSet(data_nodes);

    // create an array with edges
    var edges = new vis.DataSet(data_links);

    var data = {
        nodes: nodes,
        edges: edges
    };

    var options = {
        physics: {
            enabled: true,
            solver: 'repulsion',
            repulsion: {
                nodeDistance: 500,
                springLength: 400
            }
        },
        interaction: { hover: true, selectConnectedEdges: false },
        manipulation: {
            enabled: true,
        },
        layout: {
            randomSeed: 3342,
            improvedLayout: true,
            hierarchical: {
                enabled: false,
                levelSeparation: 200,
                nodeSpacing: 200,
                direction: 'DU',
                sortMethod: 'hubsize'
            }
        },
        height: '100%',
        width: '100%',
        nodes: {
            shape: "dot",
            font: {
                size: 25,
                color: "#d3d3d3"
            },
        },
        edges: {
            smooth: true
        }
    };

    var network = new vis.Network(container, data, options);
})();