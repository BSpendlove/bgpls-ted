# bgpls-ted
BGP-LS Traffic Engineering Database (TED)

This project is a work in progress that attempts to build a traffic engineering database (TED) using BGP-LS to collect the IGP topology from either a single AS or multiple AS'es.

### Services

bgpls-ted is made up from various parts which might be reworked in the future but for now it contains:

- ExaBGP + Publisher
- RabbitMQ
- Consumer
- MongoDB

![Topology](/imgs/bgpls-ted-diag-1.PNG)

#### ExaBGP

ExaBGP is used as a control plane BGP-LS ingestor which will peer with a router (or routers) within your AS to learn the link state topology, whether it be OSPF or ISIS. A python script is attached to the ExaBGP container which will essentially proxy the BGP updates received via ExaBGP to a message queue system, in this case RabbitMQ however there may be plans to include other destinations like directly to the database, redis and more.

#### RabbitMQ

The message queueing system used in the default project which allows multiple consumers to dial into the queue and process the data, the reason this exist is simply to scale horizontally if the single worker is taking its time to process the BGP-LS updates and insert them into the database, more workers can be added to consume the updates from the queue and speed up the process.

#### Consumer

The consumer is a docker container which acts as a "worker". This container can process the BGP-LS updates that were published to the message queue system and begin to correlate BGP-LS updates and insert them into the database (or withdraw node/links/prefixes).

#### MongoDB

A NoSQL database which holds the full topology, essentially being your traffic engineering database which you can proceed to gather insights about your topology and begin to process that data to do some cool stuff with, for example build traffic engineering tunnels and perform offline computation which can instruct routers within the network to install these tunnels using something like PCEP.

### Useful information

- Each node is uniquelly identified based on the ASN + BGP Router-ID tuple, as per [Section 3.2 in Segment Routing EPE BGP-LS Extensions draft](https://datatracker.ietf.org/doc/html/draft-ietf-idr-bgpls-segment-routing-epe-19#section-3.2).
- There are 4 types of BGP-LS updates this application captures which are: Node, Link, Prefix v4 and Prefix v6. Each update inserted into the database is assosicated with the relevant node_id (as explained above) so therefore you can easily obtain all the relevant data for a specific node such as the TE attributes for all links and prefixes belonging to a specific node
- Currently, if you want redundancy within your AS to this application, a separate BGP-LS update is stored in the database per BGP-LS neighbor therefore you will technically have 2 copies of the same TED if you peer with 2 routers within the same AS, this will be looked at in the future if I can be bothered to continue this project... Remember this is only an idea at the moment :-)

### Frontend

There is a frontend example which draws out the topology learned from BGP-LS and only demonstrates viewing the topology using vis.js Network. Any disjointed path between 2 ASNs will only show as separate topologies within the diagram. I will introduce examples in the future when I get PCE/PCEP working and figure out a few ways to calculate best path between 2 ASNs etc...

Imagine this scenario:

[Scenario](/imgs/bgpls-ted-diag-2.PNG)

IGP domain `ISIS` has no visibility to IGP domain `OSPF`, therefore an LSP can't actually be built between router `A` and router `B`. But because we have a router within each domain which distributes its link state database into BGP-LS towards the controller/application, bgpls-ted has full visibility of both domains and can initiate a traffic engineering tunnel from the headend (`A`) and program the tunnel so that we have an end to end LSP, segment routing in this case we would just program the tunnel from A to B if we want traffic taking the specific path of the dashed orange lines on the diagram.

#### Frontend examples

Topology:
![Topology](/imgs/bgpls-ted-diag-3.PNG)

Links:
![Links](/imgs/bgpls-ted-diag-4.PNG)

Prefixes:
![Prefixes](/imgs/bgpls-ted-diag-5.PNG)

JSON:
![JSON](/imgs/bgpls-ted-diag-6.PNG)


Eve-NG topology vs what bgpls-ted captured:

`eve-ng`
![EVE-NG](/imgs/bgpls-ted-diag-7.PNG)

`bgpls-ted`
![bgpls-ted](/imgs/bgpls-ted-diag-8.PNG)

### How to run

Firstly, edit the env files located in the `env` directory, if you leave this without any customization everything will work but I do not advise to run this project at all in production since I have only managed to test this on a topology with around 500+ prefixes and 200+ links.

Edit the exabgp configuration file to point to your BGP neighbor `bgpls-ted\exabgp\exabgp.conf`.

`docker-compose up -d --build`

If you change the MongoDB or RabbitMQ credentials, ensure this is reflected within the environment files. Also ensure that you change `BGPLS_DEFAULT_ASN` if you are testing the frontend. To get the frontend running, you can just run:

`pip3 install -r requirements.txt` and then from the root directory: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8080`...