#!/usr/bin/env Rscript


library(argparse)
library(tidyverse)
library(factoextra)
library(FactoMineR)

## Create parser object
parser <- ArgumentParser()

## Specify arguments
parser$add_argument("-i", "--input_file", help = "input file")
parser$add_argument("-o", "--output_dir", help = "output file")

## Get args
args <- parser$parse_args()



plot_pca <- function(df, habillage_user, output_dir, filename){
  
  dir.create(paste0(output_dir, filename, '/'))
  output_acp <- paste0(output_dir, filename, '/', filename, '_acp.png')
  output_acp2 <- paste0(output_dir, filename, '/', filename, '_acp2.png')
  output_screeplot <- paste0(output_dir, filename, '/', filename, '_scree_plot.png')
  output_contrib_axe1 <- paste0(output_dir, filename, '/', filename, '_contib_axe_1.png')
  output_contrib_axe2 <- paste0(output_dir, filename, '/', filename, '_contrib_axe_2.png')
  
  output_rdata <- paste0(output_dir, tools::file_path_sans_ext(filename), '.RData')
  res.pca <- PCA(t(df),  graph = FALSE)
  
  # Extraction des valeurs propres/variances
  get_eig(res.pca)
  #print(sessionInfo())
  scree_plot <- fviz_eig(res.pca, addlabels=TRUE, hjust = -0.3)
  
  plot_acp <- fviz_pca_ind(res.pca, 
                           repel = TRUE,
                           geom=c("point", "text"),
                           habillage = as.factor(habillage_user),
                           palette = c("blue", "red"),
                           invisible="quali")
  
#  plot_acp <- fviz_pca_ind(res.pca,
#                           col.var = "black",
#                           label="all",
#                           geom=c("point"),
#                           habillage = as.factor(habillage_user),
#                           palette = c("blue", "red"),
#                           addEllipses=FALSE,
#                           invisible="quali")

  # https://stackoverflow.com/questions/53572037/adjusting-output-in-fviz-cluster
  
  plot_acp <- plot_acp+theme(legend.position = "none")
  
  #plot_acp <- plot_acp + ggrepel::geom_text_repel(data=plot_acp$data, 
  #                                                force = 0.5,
  #                                                aes(x=x, y=y, label=name, colour=Groups),
  #                                 vjust=-1, show.legend = F)

  plot_contrib_axe_1 <- fviz_contrib(res.pca, choice = "var", axes = 1, top = 30)
  plot_contrib_axe_2 <- fviz_contrib(res.pca, choice = "var", axes = 2, top = 30)
  
  
  png(filename = output_screeplot, res = 300, units  = 'in', width = 10,
      height = 7)
  print(plot(scree_plot))
  dev.off()
  
  png(filename = output_acp, res = 300, units  = 'in', width = 7,
      height = 7)
  print(plot_acp)
  dev.off()
  
  png(filename = output_contrib_axe1, res = 300, units  = 'in', width = 10,
      height = 7)
  print(plot(plot_contrib_axe_1))
  dev.off()
  
  png(filename = output_contrib_axe2, res = 300, units  = 'in', width = 10,
      height = 7)
  print(plot(plot_contrib_axe_2))
  dev.off()
  
  save(res.pca, habillage_user, filename, file = output_rdata)
}


# load data
df <- read.table(args$input_file, sep=',', quote="\"", header=TRUE)

data <- df %>%
  column_to_rownames("Accession") %>%
  dplyr::filter(specific != "specific") %>%
  select(matches("VAL_"))
  

names(data) <- gsub("_reference", "", names(data))
names(data) <- gsub("VAL_", "", names(data))

names(data) <- gsub("Cond", "", names(data))

if (dim(data)[1] < 2){
  print("Not enough significant proteins to plot")
  quit(status=0)
  
}
habillage <-data.frame(group=names(data))
habillage$group <- gsub("_[0-9]{1,3}", "", habillage$group)

comparison <- basename(tools::file_path_sans_ext(args$input_file))
comparison <- strsplit(comparison, "_")
comparison <- comparison[[1]][-1] 
comparison <- paste(comparison, collapse='_')


dir_output_dir <- dirname(args$output_dir)

plot_pca(data, habillage$group, args$output_dir, comparison)




