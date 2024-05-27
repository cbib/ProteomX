#!/usr/bin/env Rscript

#
# a<-installed.packages()
# packages<-a[,1]
# if(!is.element("pheatmap", packages)){
#   install.packages("pheatmap", repos='http://cran.us.r-project.org')
# }
library(pheatmap)
# if(!is.element("argparse", packages)){
#   install.packages("argparse", repos='http://cran.us.r-project.org')
# }
library(argparse)
# if(!is.element("RColorBrewer", packages)){
#   install.packages("RColorBrewer", repos='http://cran.us.r-project.org')
# }
library(RColorBrewer)
# if(!is.element("tidyverse", packages)){
#   install.packages("tidyverse", repos='http://cran.us.r-project.org')
# }
library(tidyverse)
# if(!is.element("data.table", packages)){
#   install.packages("data.table", repos='http://cran.us.r-project.org')
# }
library(data.table)
# if(!is.element("ComplexHeatmap", packages)){
#   if (!requireNamespace("BiocManager", quietly = TRUE))
#     install.packages("BiocManager", repos='http://cran.us.r-project.org')
#
#   BiocManager::install("ComplexHeatmap")
# }
library(ComplexHeatmap)
library(tools) #file_path_sans_ext

# if(!is.element("glue", packages)){
#   install.packages("glue", repos='http://cran.us.r-project.org')
# }
library(glue)



## Create parser object
parser <- ArgumentParser()

## Specify arguments
parser$add_argument("-i", "--input_file", help = "input file")
parser$add_argument("-o", "--output_file", help = "output file")

## Get args
args <- parser$parse_args()


select_data <- function(df, col_id, specific_filter, prefic_ab_col){
  if (!missing(specific_filter)){
    print("Argument not missing")
    select = TRUE
  } else {
    select = FALSE
  }

  res <- df %>%
    column_to_rownames(col_id) %>%
    dplyr::filter(specific != "specific") %>%
    #dplyr::filter(if (select) specific %in% specific_filter else TRUE) %>%
    dplyr::select(matches(prefic_ab_col)) %>%
    filter_all(any_vars(!is.na(.)))

  return(res)
}

remove_substring_from_column_name <- function(df, ...){
  for (tochange in list(...)){
    names(df) <- gsub(tochange, "", names(df))
  }
  return(df)
}

create_annotation_data <- function(df){

  conditions <- data.frame(group=names(df))
  rownames(conditions) <- names(df)
  conditions$group <- gsub("_[0-9]{1,3}", "", conditions$group)
  return(conditions)
}


create_annotation_colors <- function(annot_df){
  
  annotation_color = list(group = c(g1 = "#E6433E", g2 = "#268C83"))
  
  group_names <- unique(annot_df[c("group")])
  g1 <- glue("{group_names[1,1]}")
  g2 <- glue("{group_names[2,1]}")
  names(annotation_color$group) <- c(g1, g2)
  return(annotation_color)
}

save_plot <- function(plot_to_save, output_png){
  png(filename = output_png, res = 300, units  = 'in', width = 7,
      height = 7)
  print(plot_to_save)
  dev.off()
  
}

plot_heatmap <- function(input_data, output_png, prefix_abundance_columns){
  print("Select data")
  data_df <- select_data(input_data, "Accession", prefic_ab_col=prefix_abundance_columns)

  if (dim(data_df)[1] < 1){
    print("Not enough significant proteins to plot")
    library(nat.utils)
    touch(output_png)
    quit(status=0)
    
  }
  print("Clean colnames")
  data_to_plot <- remove_substring_from_column_name(data_df, prefix_abundance_columns, "_reference", "Cond")
  print("Create annotation data")
  annotation_df <- create_annotation_data(data_to_plot)
  print("Create annotations colors")
  annotation_color <- create_annotation_colors(annotation_df)
  data_to_plot[is.na(data_to_plot)] <- 0
  # p <- pheatmap(t(scale(t(data_to_plot), center = TRUE, scale = FALSE)),
  #               annotation_col=annotation_df,
  #               show_rownames=FALSE,
  #               annotation_colors = annotation_color)

  if (dim(data_to_plot)[1] == 1){
    p <- pheatmap(as.matrix(data_to_plot),
                  annotation_col=annotation_df,
                  show_rownames=FALSE,
                  annotation_colors = annotation_color,
                  cluster_rows=FALSE,
                  cellheight=20)
  } else {
    p <- pheatmap(as.matrix(data_to_plot),
                  annotation_col=annotation_df,
                  show_rownames=FALSE,
                  annotation_colors = annotation_color)
  }

  
  save_plot(p, output_png)
}

#### input File from CV folder
input_df <- read.csv(args$input_file, sep=',')
output_png <- args$output_file

# c


plot_heatmap(input_df, output_png, "VAL_")





