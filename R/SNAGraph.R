library(igraph)
library(dplyr)
library(extrafont) #Fully Optional!

#Settings
corpusPath <- "../Python/results/"
file.names <- dir(corpusPath, pattern =".graphml")
outputSizeH <- 3750
outputSizeW <- 5000
outputResultion <- 300
targetQuantile <- 0.75
arrowSize <- 0.01
howCurved <- 0.2

#Run through all files and generate network graphs
for (i in 1:length(file.names)) {
  fileName = file.names[i]
  fileNamePath = paste (corpusPath, fileName, sep = "", collapse = NULL)
  g <- igraph::read_graph(fileNamePath, "graphml")
  g <- igraph::simplify(g, remove.multiple = TRUE, remove.loops = TRUE)
  
  #Basic Calculations
  qWeight = quantile(E(g)$weight, targetQuantile) #Quantile
  qLength <- quantile(V(g)$length, targetQuantile)
  
  #Vertices
  V(g)[V(g)$length < 5000]$color <- "gray90"
  V(g)[V(g)$length >= qLength]$color <- "#B11010" #Maybe based on average!
  V(g)$size = V(g)$length/1000
  V(g)[V(g)$size < 15]$size <- 15 #Minimal Size
  V(g)[V(g)$size > 40]$size <- 40 #Maximum Size
  
  #Labels
  #loadfonts(device="win")
  V(g)$label.cex <- V(g)$size/15
  V(g)$label.family <- 'Roboto Bk'
  V(g)$label.color <- 'gray70'
  V(g)[V(g)$length >= qLength]$label.color <- "black"
  V(g)[V(g)$label.cex >= 1.5]$label.cex <- 1.5 #Maximum Size
  
  #Edges
  E(g)$color <- "grey80"
  E(g)[E(g)$weight > qWeight]$color <- "#003D46"
  E(g)$width <- E(g)$weight
  
  #Output
  lnicely <- layout_nicely(g, dim=2)
  lwithdrl <- layout_with_drl(g, dim=2)
  lfr <- layout_with_fr(g, niter=50)
  lcircle <- layout_in_circle(g) #SmallWorld
  
  png(filename=paste("img/", fileName, "-circle.png", sep=""), height=outputSizeW, width=outputSizeH, res=outputResultion, bg = "transparent")
  igraph::plot.igraph(g, layout=lcircle, edge.arrow.size=arrowSize, edge.curved=howCurved, vertex.label=igraph::V(g)$id, vertex.frame.color="gray40")
  dev.off()
  
  png(filename=paste("img/", fileName, "-nicely.png", sep=""), height=outputSizeH, width=outputSizeW, res=outputResultion, bg = "transparent")
  igraph::plot.igraph(g, layout=lnicely, edge.arrow.size=arrowSize, edge.curved=howCurved, vertex.label=igraph::V(g)$id, vertex.frame.color="gray40")
  dev.off()

  png(filename=paste("img/", fileName, "-fr.png", sep=""), height=outputSizeH, width=outputSizeW, res=outputResultion, bg = "transparent")
  igraph::plot.igraph(g, layout=lfr, edge.arrow.size=arrowSize, edge.curved=howCurved, vertex.label=igraph::V(g)$id, vertex.frame.color="gray40")
  dev.off()

  png(filename=paste("img/", fileName, "-fr.png", sep=""), height=outputSizeH, width=outputSizeW, res=outputResultion, bg = "transparent")
  igraph::plot.igraph(g, layout=lwithdrl, edge.arrow.size=arrowSize, edge.curved=howCurved, vertex.label=igraph::V(g)$id, vertex.frame.color="gray40")
  dev.off()
}
