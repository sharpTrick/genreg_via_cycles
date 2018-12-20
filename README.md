# genreg_via_cycles

genreg_via_cycles is a utility that generates and returns the first regular graph of n, k, g found via cycle generation.
 
Where:
- n is the number of vertices
- k is degree (edges per node)
- g is the minimum girth

Graphs constricted by extreme arguments may take longer to generate than is reasonably useful depending on circumstances (assuming such a graph even exists).

genreg_via_cycles was built for the purpose of quickly generating graphs for:
- n between 1 and 1000
- k between 0 and 4
- g between 3 and 6

Please see:
- https://en.wikipedia.org/wiki/Regular_graph
- https://en.wikipedia.org/wiki/Girth_(graph_theory)
- http://www.mathe2.uni-bayreuth.de/markus/reggraphs.html

At this point genreg_via_cycles has the considerable drawback of failing very slowly (never ending) if there is no graph to be found because it ends up testing every possible combination of viable edges which turns into a combinatorial explosion.
