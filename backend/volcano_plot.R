#!/usr/bin/env Rscript

# a<-installed.packages()
# packages<-a[,1]
# if(!is.element("argparse", packages)){
#   install.packages("argparse", repos="https://cran.irsn.fr/")
# }
library(argparse)
# if(!is.element("rjson", packages)){
#   install.packages("rjson")
# }
library(rjson)
# if(!is.element("glue", packages)){
#   install.packages("glue", repos="https://cran.irsn.fr/")
# }
library(glue)

# if(!is.element("tidyverse", packages)){
#   install.packages("tidyverse", repos="https://cran.irsn.fr/")
# }
library(tidyverse)
# if(!is.element("stringr", packages)){
#   install.packages("stringr")
# }
library(stringr)
# if(!is.element("EnhancedVolcano", packages)){
#   if (!requireNamespace("BiocManager", quietly = TRUE))
#     install.packages("BiocManager")
#
#   BiocManager::install("EnhancedVolcano")
# }
library(EnhancedVolcano)

## Create parser object
parser <- ArgumentParser()

## Specify arguments
parser$add_argument("-i", "--input_file", help = "input file")
parser$add_argument("-o", "--output_dir", help = "output file")
parser$add_argument("-p", "--projet_id", help = "Project ID")
parser$add_argument("-wd", "--working_directory", help = "Working directory (ProteomX)")


## Get args
args <- parser$parse_args()

## get output_dir
output_dir=args$output_dir

## Get config json
wd = args$working_directory
projet_id = args$projet_id

path2json <- glue("{wd}/data/{projet_id}/config_file.json")
cat(glue("Path to config file: {path2json}"), .sep="\n")
cat("Loading config file...")
rule_params <- rjson::fromJSON(file=path2json)
cat("...DONE \n")
gene_bank=rule_params$enrichment$subset_params$gene_bank
col_of_interest=rule_params$statistical_analysis$sort_result_by

# load data
df <- read.table(args$input_file, sep=',', quote="\"", header=TRUE)
# Remove NAs
#df = df[complete.cases(df), ]
df = df[df$pvalue!="",]
df <- df[df$gene_name!='no gene name',]
legend_labels=c('Not significant','|log2FoldChange| > 1',
                               'padj < 0.05',
                               'padj < 0.05 & |log2FoldChange| > 1')
if(!"padj" %in% colnames(df))
{
  legend_labels=c('Not significant','|log2FoldChange| > 1',
                               'pvalue < 0.05',
                               'pvalue < 0.05 & |log2FoldChange| > 1')
  df$padj=df$pvalue
}
df$pvalue=as.numeric(df$pvalue)
df$padj=as.numeric(df$padj)
rownames(df) <- NULL
if (col_of_interest=='pvalue'){
  if (gene_bank == "Swiss-Prot"){
    df=df[!grepl("TREMBL", df$gene_name_bank),]
  }
  else{
    df=df[grepl("TREMBL", df$gene_name_bank),]
  }
}else{
  if (gene_bank == "Swiss-Prot"){
    df=df[!grepl("Trembl", df$gene_name_bank),]
  }
  else{
    df=df[grepl("Trembl", df$gene_name_bank),]
  }
}
df=df[!duplicated(df$gene_name),]
df=df[!is.na(df$gene_name),]
row.names(df)=df$gene_name
data <- df %>%
  select(c(all_of(col_of_interest), "log2FoldChange"))
names(data) <- gsub("_reference", "", names(data))
names(data) <- gsub("VAL_", "", names(data))
file_name = tools::file_path_sans_ext(basename(args$input_file))
plot_title_list = strsplit(file_name, "_")
plot_title = plot_title_list[[1]][1]
plot_subtitle = paste(plot_title_list[[1]][-1], collapse=" ")
png(filename = output_dir, res = 300, units  = 'in', width = 11,
    height = 7)

EnhancedVolcano(data,
                lab = rownames(data),
                x = 'log2FoldChange',
                y = col_of_interest,
                title = plot_title,
                subtitle = plot_subtitle,
                drawConnectors = TRUE,
                legendPosition = 'right',
                legendLabSize = 12,
                labSize = 2,
                legendIconSize = 4.0,
                ylim = c(0, 4),
                pCutoff = 0.05,
                colAlpha = 0.8,
                pointSize = 2.0,
                widthConnectors = 0.75,
                selectLab=rownames(data[data$pvalue<0.05,]),
                legendLabels=legend_labels,
                xlab = bquote(~log[2]~FoldChange),
                ylab = bquote(~-log[10]~italic(pvalue)))
dev.off()






