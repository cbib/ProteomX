#!/usr/bin/env Rscript

library(data.table)
library(argparse)
library(plyr)
library(clusterProfiler)
library("org.Hs.eg.db")
library(tools)

## Create parser object
parser <- ArgumentParser()

## Specify arguments
parser$add_argument("-i", "--input_file", help = "input file")
parser$add_argument("-o", "--output_file", help = "output file")
parser$add_argument("-l", "--log", help = "which proteins to kkeep")

## Get args
args <- parser$parse_args()


## Get data
#input_file <- paste0(c('/home/claire/Documents/ProteomX_Benjamin/'), args$input_file)
input_file <-  args$input_file
input_df <- read.csv(input_file, header=TRUE, sep=",", row.names = 1, stringsAsFactors = FALSE)

#output_dir <- paste0('/home/claire/Documents/ProteomX_Benjamin/', file_path_sans_ext(args$output_file))
output_dir <- dirname(args$output_file)

if (!dir.exists(output_dir)){
  dir.create(output_dir)
} else {
  print("Dir already exists!")
}

input_df = input_df[input_df$gene_name_bank == 'Swiss-Prot', ]

if (args$log == 'pos'){
  print('log==pos')
  input_df <- input_df[(input_df$Log2FoldChange > 0),]
} else if (args$log == 'neg'){
  print('log==neg')
  input_df = input_df[input_df$Log2FoldChange < 0,]
} else if (args$log == 'all'){
  print("keeping all proteins")
}
output_name <- basename(args$output_file)

#output_name_CC <- paste0(output_dir, '/', output_name, '_CC.png')
#output_name_MF <- paste0(output_dir, '/', output_name, '_MF.png')
#output_name_BP <- paste0(output_dir, '/', output_name, '_BP.png')
#print(file_path_sans_ext(args$output_file))
output_name_CC <- paste0(file_path_sans_ext(args$output_file), '_CC.png')
output_name_MF <- paste0(file_path_sans_ext(args$output_file), '_MF.png')
output_name_BP <- paste0(file_path_sans_ext(args$output_file), '_BP.png')

#output_csv_CC <- paste0(output_dir, '/', output_name, '_CC.csv')
#output_csv_MF <- paste0(output_dir, '/', output_name, '_MF.csv')
#output_csv_BP <- paste0(output_dir, '/', output_name, '_BP.csv')
output_csv_CC <- paste0(file_path_sans_ext(args$output_file), '_CC.csv')
output_csv_MF <- paste0(file_path_sans_ext(args$output_file), '_MF.csv')
output_csv_BP <- paste0(file_path_sans_ext(args$output_file), '_BP.csv')

gene_list <- input_df$gene_name

## ENRICHISSEMENT

CC_human <- enrichGO(gene          = gene_list,
                      OrgDb         = org.Hs.eg.db,
                      keyType       = 'SYMBOL',
                      ont           = "CC",
                      pAdjustMethod = "BH",
                      pvalueCutoff  = 0.05,
                      qvalueCutoff  = 0.2)
plot_CC <- dotplot(CC_human,showCategory=10)


png(filename = output_name_CC, res = 300, units  = 'in', width = 10,
    height = 7)
print(plot_CC)

cc_df <- data.frame(CC_human)
cc_df <- cc_df[1:10,c('ID', 'Description', 'Count', 'geneID')]
cc_df <- cc_df[order(-cc_df$Count),]
write.csv(cc_df, output_csv_CC, row.names = TRUE)


MF_human <- enrichGO(gene          = gene_list,
                     OrgDb         = org.Hs.eg.db,
                     keyType       = 'SYMBOL',
                     ont           = "MF",
                     pAdjustMethod = "BH",
                     pvalueCutoff  = 0.05,
                     qvalueCutoff  = 0.2)
plot_MF <- dotplot(MF_human,showCategory=10)
png(filename = output_name_MF, res = 300, units  = 'in', width = 10,
    height = 7)
print(plot_MF)

mf_df <- data.frame(MF_human)
print('---')
mf_df <- mf_df[1:10,c('ID', 'Description', 'Count', 'geneID')]
print(mf_df)
print('---')
#print(mf_df[order(-mf_df$Count), ])
mf_df <- mf_df[order(-mf_df$Count), ]
write.csv(mf_df, output_csv_MF, row.names = TRUE)

BP_human <- enrichGO(gene          = gene_list,
                     OrgDb         = org.Hs.eg.db,
                     keyType       = 'SYMBOL',
                     ont           = "BP",
                     pAdjustMethod = "BH",
                     pvalueCutoff  = 0.05,
                     qvalueCutoff  = 0.2)
plot_BP <- dotplot(BP_human,showCategory=10)
png(filename = output_name_BP, res = 300, units  = 'in', width = 10,
    height = 7)
print(plot_BP)

bp_df <- data.frame(BP_human)
bp_df <- bp_df[1:10,c('ID', 'Description', 'Count', 'geneID')]
bp_df <- bp_df[order(-bp_df$Count),]
write.csv(bp_df, output_csv_BP, row.names = TRUE)
