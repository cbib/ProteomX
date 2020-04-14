#!/usr/bin/env Rscript

### Pour comparaison de deux conditions

library(pheatmap)
library(argparse)
library(RColorBrewer)
library(tidyverse)
library(data.table)
library(tools) #file_path_sans_ext

## Create parser object
parser <- ArgumentParser()

## Specify arguments
parser$add_argument("-i", "--input_file", help = "input file")
parser$add_argument("-o", "--output_file", help = "output file")
parser$add_argument("-id", "--id_col", help = "Protein/gene ID")

## Get args
args <- parser$parse_args()

output_dir <- paste0(dirname(args$output_file), basename(args$output_file))
id_col <- args$id_col

# Check target directory 
if (!dir.exists(output_dir)){
  dir.create(output_dir)
} else {
  print("Dir already exists!")
}

## Get data
#input_file <- paste0(c('/home/claire/Documents/ProteomX_Benjamin/'), args$input_file)

input_df <- read.csv(args$input_file, header=TRUE, sep=",")
print(input_df)
colnames(input_df) <- gsub('_reference', '', colnames(input_df), fixed=TRUE)
colnames(input_df) <- gsub('Reduced_R', 'R', colnames(input_df), fixed=TRUE)

print(dim(input_df))
if (dim(input_df)[1] > 1){
  ## Remove proteins specific to one condition
  input_df <- input_df[!(input_df$pvalue == "0"),]
  rownames(input_df) <- input_df[[id_col]]

  filtered_df <- input_df
  
  ## Select plotted data : accession (index) and abundance columns
  filtered_df <- filtered_df %>%
    select(matches('^Reduced_')) 
  rownames(filtered_df) <- rownames(input_df)
  
  print(head(filtered_df))
  #filtered_df[is.na(filtered_df)] <- 0.00000000001
  #filtered_df[,] <- log(filtered_df[,])

  ## Get labels for heatmap
  col_filtered_df <- vector(mode="character", length=dim(filtered_df)[2])
  
  for (i in 1:dim(filtered_df)[2]){
    col_name <- names(filtered_df)[i]
    print(col_name)
    list_label <- strsplit(col_name, '_')
    print(list_label)
    print(lengths(list_label[1]))
    print(dim(list_label[1]))
    if (lengths(list_label) == 8) {
      col_label <- paste(list_label[[1]][5], list_label[[1]][6], list_label[[1]][8], sep = ' ')
      print(col_label)
      col_filtered_df[i] <- col_label
    } else if (lengths(list_label) == 7) {
      col_label <- paste(list_label[[1]][5], list_label[[1]][7], sep = ' ')
      print(col_label)
      col_filtered_df[i] <- col_label
    } else if (lengths(list_label) == 9) {
      col_label <- paste(list_label[[1]][5], list_label[[1]][6], list_label[[1]][7], list_label[[1]][9], sep = ' ')
      print(col_label)
      col_filtered_df[i] <- col_label
    }
  }
  print(col_filtered_df)
  
  names(filtered_df) <-  col_filtered_df
  print(head(filtered_df))
  print(names(filtered_df))
  ## Highlights groups 
  print(length(col_filtered_df))
  for (i in 1:length(col_filtered_df)){
    col_filtered_df[i] <- gsub('[[:digit:]]+', '', col_filtered_df[i])
    col_filtered_df[i] <- gsub('SA ', '', col_filtered_df[i])
    #col_filtered_df[i] <- gsub("[[:space:]]", "", col_filtered_df[i])
  }
  print(col_filtered_df)
  name_conditions <- unique(unlist(col_filtered_df, use.names = FALSE))
  nb_cond1 <- sum(lengths(regmatches(col_filtered_df, gregexpr(name_conditions[1], col_filtered_df))))
  nb_cond2 <- sum(lengths(regmatches(col_filtered_df, gregexpr(name_conditions[2], col_filtered_df))))
  colnames(filtered_df) <- gsub('SA ', '', colnames(filtered_df))
  annotation_col <- data.frame(Groupe = c(rep(name_conditions[1], nb_cond1), c(rep(name_conditions[2], nb_cond2))))
  rownames(annotation_col) = colnames(filtered_df)
  print(head(filtered_df))
  #rownames(filtered_df) <- rownames(input_df)
  print(rownames(filtered_df))
  
  color_row = list(Group = c(Control= '#f74747', Disease = '#5977ff'))
  
  ## Produce heatmap
  #heatmap <- pheatmap(filtered_df, annotation_col = annotation_col, annotation_colors = color_row, show_rownames = TRUE)
  if (dim(filtered_df)[1] > 40){
    heatmap <- pheatmap(filtered_df, annotation_col = annotation_col, annotation_colors = color_row, show_rownames = FALSE)
  } else {
    heatmap <- pheatmap(filtered_df, annotation_col = annotation_col, annotation_colors = color_row, show_rownames = TRUE)
  }
  
  ## Save image
  png(filename = args$output_file, res = 300, units  = 'in', width = 10,
      height = 7)
  print(heatmap)
  dev.off()
} else {
  print('here')
  c <- 1
  d <- 2
  
  a <- -2
  b <- 3.5
  
  ll <- pnorm(a, c, d)
  ul <- pnorm(b, c, d)
  
  x <- qnorm( runif(3000, ll, ul), c, d )
  print(x, x)
  heatmap <- plot(x, type='l')
  png(filename = args$output_file, res = 300, units  = 'in', width = 10,
      height = 7)
  print(heatmap)
  dev.off()
}








#### Heatmap présentation 

