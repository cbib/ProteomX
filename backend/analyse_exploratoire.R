#!/usr/bin/env Rscript

# Analyse exploratoire sur l'ensemble des échantillons pour toutes les conditions étudiées
# utilisation du fichier "preprocessed" (c'est à dire, après mapping,
# suppression des protéines non master, contaminantes ou avec moins de deux peptides uniques)
# pas de filtres sur les valeurs manquantes ou CV

# a<-installed.packages()
# packages<-a[,1]
# if(!is.element("tibble", packages)){
#   install.packages("tibble", repos='http://cran.us.r-project.org')
# }
library(tibble)
# if(!is.element("paletteer", packages)){
#   install.packages("paletteer", repos='http://cran.us.r-project.org')
# }
library(paletteer)

# if(!is.element("dplyr", packages)){
#   install.packages("dplyr", repos='http://cran.us.r-project.org')
# }
library(dplyr)

# if(!is.element("factoextra", packages)){
#   install.packages("factoextra", repos='http://cran.us.r-project.org')
# }
library(factoextra)

# if(!is.element("FactoMineR", packages)){
#   install.packages("FactoMineR", repos='http://cran.us.r-project.org')
# }
library(FactoMineR)

# if(!is.element("dendextend", packages)){
#   install.packages("dendextend", repos='http://cran.us.r-project.org')
# }
library(dendextend)

# if(!is.element("RColorBrewer", packages)){
#   install.packages("RColorBrewer", repos='http://cran.us.r-project.org')
# }
library("RColorBrewer")

# if(!is.element("argparse", packages)){
#   install.packages("argparse", repos='http://cran.us.r-project.org')
# }
library(argparse)

# if(!is.element("dichromat", packages)){
#   install.packages("dichromat", repos='http://cran.us.r-project.org')
# }
library(dichromat)


## Create parser object
parser <- ArgumentParser()

## Specify arguments
parser$add_argument("-i", "--input_file", help = "csv file")
parser$add_argument("-o", "--output_file", help = "filename without extension")

## Get args
args <- parser$parse_args()

# load data
df <- read.csv(args$input_file)

# prepare data
data <- df %>%
  tibble::column_to_rownames("Accession") %>%
  dplyr::select(matches("VAL_")) %>%
  rename_all(function(x) gsub("VAL_", "", x))


# habillage : metadata
habillage <-data.frame(group=names(data))
habillage$group <- gsub("_[0-9]{1,2}", "", habillage$group)
habillage$sample <- names(data)
habillage$replicate <- habillage$sample
habillage$replicate <- gsub("[[:alpha:]]{1,3}_", "", habillage$replicate)

# remove row with too many NaN (percentage p)
p = 30
n = ncol(data) * p /100
data <- data[ rowSums(!is.na(data)) >= n, ]

# PCA
# res.pca <- PCA(t(data),  graph = FALSE)
# eig.val <- get_eigenvalue(res.pca)
#
# scree_plot <- fviz_eig(res.pca, addlabels=TRUE, hjust = -0.3)
# plot_acp <- fviz_pca_ind(res.pca,
#                          col.var = "black",
#                          geom=c("point", "text"),
#                          habillage = as.factor(habillage$group),
#                          palette = "jco",
#                          repel=TRUE,
#                          pointsize=1,
#                          pointshape = 19,
#                          addEllipses=FALSE,
#                          title="")
#
# png(filename = paste0(args$output_file, '_all_samples_acp.png'), res = 300, units  = 'in', width = 10,
#     height = 7)
# print(plot_acp)
# dev.off()
#
# plot_acp <- fviz_pca_ind(res.pca,
#                          geom=c("point"),
#                          habillage = as.factor(habillage$group),
#                          palette = "jco",
#                          show.clust.cent = FALSE,
#                          pointsize=1.7,
#                          pointshape = 19,
#                          title="",
#                          invisible="quali")
#
#
#
# png(filename = paste0(args$output_file, '_all_samples_acp_no_sample_names.png'), res = 300, units  = 'in', width = 10,
#     height = 7)
# print(plot_acp)
# dev.off()

# DENDROGRAMMS
nreplicates = length(unique(as.vector(habillage$replicate)))
ngroups = length(unique(as.vector(habillage$group)))
color_day= dichromat::colorschemes$SteppedSequential.5
#color_day = brewer.pal(n = nreplicates, name = "Set3")
palette_day = color_day
color_group = dichromat::colorschemes$SteppedSequential.5
#color_group = brewer.pal(n = ngroups, name = "RdBu")
palette_group = color_group
# pas bon si nombre variable de réplicats entre chaque groupes
#https://stackoverflow.com/questions/10803585/r-repeat-elements-of-a-list-based-on-another-list
# palette_group_24 = unlist(lapply(seq_along(palette_group), function(i)rep(palette_group[[i]], nsample_per_group)))


# habillage$color_group <- palette_group_24

color_group=color_group[1:length(unique(as.vector(habillage$group)))]
names(color_group) <- unique(as.vector(habillage$group)) 
pg <- data.frame(color_group)
pg$group <- rownames(pg)

color_day=color_day[1:length(unique(as.vector(habillage$replicate)))]

names(color_day) <- unique(as.vector(habillage$replicate)) 
pr <- data.frame(color_day)
pr$replicate <- rownames(pr)

habillage <- left_join(habillage, pg)
habillage <- left_join(habillage, pr)

# Raw data
dend_data <- t(data) %>% 
  dist %>% 
  hclust() %>% 
  as.dendrogram

png(filename =paste0(args$output_file, "_dendrogram_not_scaled.png"), res = 300, units  = 'in', width = 15,
    height = 15)

# Set the plot margin: bottom, left, top & right
par(mar = c(8, 10, 5, 10) + 0.1,
    xpd = NA) # allow content to go into outer margin 

plot(dend_data)


# Setup the color bar based on group & dau
bar_group <- habillage$color_group
bar_day <- habillage$color_day
the_bars <- cbind(bar_group, bar_day)
colored_bars(colors = the_bars, dend = dend_data, rowLabels = c("Group", "Replicat"))


# Add the legend manually
legend("bottomright", legend = levels(as.factor(habillage$replicate)), pch = 15, pt.cex = 2, cex = 1, bty = 'n',
       inset = c(-0.1, 0), # place outside
       title = "Replicat",
       col = palette_day)

legend("right", legend = levels(as.factor(habillage$group)), pch = 15, pt.cex = 2, cex = 1, bty = 'n',
       inset = c(-0.1, 0), # place outside
       title = "Group",
       col = palette_group)
dev.off()





# Dendrogramm on scaled data
dend_data <- t(t(scale(t(data), center=TRUE, scale=TRUE))) %>% 
  dist %>% 
  hclust() %>% 
  as.dendrogram



print('Plot dendrogramm') # in every case, for quick checking
png(filename =paste0(args$output_file, "_dendrogram_scaled.png") , res = 300, units  = 'in', width = 15,
    height = 15)

# Set the plot margin: bottom, left, top & right
par(mar = c(8, 10, 5, 10) + 0.1,
    xpd = NA) # allow content to go into outer margin 

plot(dend_data)


# Setup the color bar based on $am & $vs
bar_group <- habillage$color_group
bar_day <- habillage$color_day
the_bars <- cbind(bar_group, bar_day)
colored_bars(colors = the_bars, dend = dend_data, rowLabels = c("Group", "Replicat"))


# Add the legend manually
legend("bottomright", legend = levels(as.factor(habillage$replicate)), pch = 15, pt.cex = 2, cex = 1, bty = 'n',
       inset = c(-0.1, 0), # place outside
       title = "Replicat",
       col = palette_day)

legend("right", legend = levels(as.factor(habillage$group)), pch = 15, pt.cex = 2, cex = 1, bty = 'n',
       inset = c(-0.1, 0), # place outside
       title = "Group",
       col = palette_group)
dev.off()

