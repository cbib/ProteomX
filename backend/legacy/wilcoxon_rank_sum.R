#!/usr/bin/env Rscript

### Pour comparaison de deux conditions
#setwd('/home/claire/Documents/ProteomX_Benjamin/')

library(argparse)
library(data.table)
library(tidyverse)
library(gtools)
source("/home/clescoat/Documents/ProteomX/scripts/Rfunctions.R")

## Create parser object
parser <- ArgumentParser()

## Specify arguments
parser$add_argument("-i", "--input_file", help = "input file")
parser$add_argument("-o", "--output_file", help = "output file")

## Get args
args <- parser$parse_args()


## Get data
input_df <- read.csv(args$input_file, header=TRUE, sep=",", row.names = 1)
#input_df <- input_df[input_df$Reduced_GR_Control_SA_Control_REP_1 != Inf,]

abundance_df <- input_df %>%
  select(matches('Count_')) 
abundance_df <- t(scale(t(abundance_df)))

rownames(abundance_df) <- input_df$Probe_Name
print(head(abundance_df))
abundance_df <- abundance_df[abundance_df[,3] != Inf,]


#abundance_df  <- apply (abundance_df, 1, function(x) any(x==Inf) )


df = abundance_df


# Get rid of "_REP_XX" at the end of column names to get condition names
colnames(abundance_df) <- gsub('_reference', '', colnames(abundance_df))
colnames(abundance_df) <- gsub('_[0-9]{1,2}', '', colnames(abundance_df))
conditions <- unique(colnames(abundance_df))
print(conditions)

output_file <- args$output_file
print(names(df))
cols_group1 <- grep(conditions[1], colnames(df), value=T)
cols_group2 <- grep(conditions[2], colnames(df), value=T)

print(cols_group1)

print(cols_group2)
group1 = df[, cols_group1]
group2 = df[, cols_group2]

print(head(group1))
print(head(group2))

wilcox_<- wilcoxon_test(df, group1, group2, output_file )
print(head(wilcox))


