#!/usr/bin/env Rscript

# Wrapper for gProfiler enrichment analysis
# takes a data frame with a least a column (-c) with gene list
# run analysis on specified sources (-s) (or all if nothing is specified)
# returns a formatted excel file with significant results


library(argparse)
library(gprofiler2)
library(glue)
library(ggplot2)
library(openxlsx)
library(dplyr)

## Create parser object
parser <- ArgumentParser()

## Specify arguments
parser$add_argument("-i", "--input_file", help = "input file")
parser$add_argument("-o", "--output_file", help = "output file (without extension)")
parser$add_argument("-f", "--file_id", help = "Project ID")
parser$add_argument("-wd", "--working_directory", help = "Working directory (ProteomX)")


parser$add_argument("-m", "--max_result_to_plot", default=10, help = "Maximal number of significant terms to plots")
parser$add_argument("-org", "--organism", default="hsapiens", help = "Query organism. hsapiens / mmusculus / other")
parser$add_argument("-c", "--column", help = "Name of column with genes", default="gene_name")
parser$add_argument("-s", "--sources", nargs="+", help = "Data sources for enrichment", default=c("GO:MF", "GO:BP", "GO:CC", "KEGG", "REAC", "TF", "MIRNA", "CORUM", "HP", "HPA", "WP"))
parser$add_argument("-oq", "--ordered_query", action="store_true", help = "True if analysis to run as ordered query")
parser$add_argument("-iea", "--exclude_iea", action="store_true", help = "True if analysis to run without GO electronic annotations (IEA)")

parser$add_argument("-e", "--export_excel", action="store_false", help="Add -e option if you wish to export excel file with only relevant columns")
parser$add_argument("-csv", "--export_csv", action="store_true", help="Add -e option if you wish to export excel file with only relevant columns")
parser$add_argument("-r", "--export_rdata", action="store_true", help="Add -r option if you wish to export analysis results as RData")
parser$add_argument("-pl", "--plot_results", action="store_false", help = "By default, plot results as dotplot")

parser$add_argument("-pv", "--pvalue", default="1", help = "Filter data on p-value (keeping inferior to given value)")
parser$add_argument("-l", "--log2fc", default="0", help = "Filter data on log2FC (keeping superior to given value)")

## Get args
args <- parser$parse_args()

enrichment_dotplot_from_gProfiler <- function(df_to_plot, significance_threshold, nterms, graph_title, output_fig){
  #### Source of following code: Ahmad Mousavi's ggplot2 script : https://www.biostars.org/p/343196/
  print(glue("Plotting dot plot"))
  
  # Keep only significant terms
  print(glue("... keepin only terms with pvalue < {significance_threshold}"))
  df <- df_to_plot[df_to_plot$p_value < significance_threshold,]
  
  
  # order dataframe by adjusted pvalue in case it' not the case
  print(glue("... ordering results by p-value"))
  df <- df[order(df$negative_log10_of_adjusted_p_value, df$intersection_size), ]  
  
  # get first only the first fifteen
  print(glue("... keepin only {nterms} first terms"))
  df <- utils::tail(df, as.numeric(nterms))

  df$term_name <- factor(df$term_name, levels=unique(df$term_name))
  
  # Barcharts
  print(glue("... creating ggplot2 object"))
  p <- ggplot(df, aes(x=term_name, y=negative_log10_of_adjusted_p_value)) +
    ylim(c(min(df$negative_log10_of_adjusted_p_value) - 0.5, max(df$negative_log10_of_adjusted_p_value) + 0.5))  +
    geom_point(data=NULL,stat="identity", aes(size = as.numeric(sub("/.*","",intersection_size))), position_dodge(width = 0.5)    )  +
    labs(subtitle="functional enrichment analysis", 
         title= graph_title,
         y="-log10(p-adj)",
         size="Gene Counts") +
    theme(axis.text.y = element_text(color = "grey20", size = 15, angle = 0, hjust = 1, vjust = .5, face = "plain"),
          axis.title.y = element_blank()) +
    coord_flip()
  
  # export png file
  png(filename = output_fig, res = 300, units  = 'in', width = 15, height = 7)
  print(p)
  dev.off()
  
  print(glue("... DONE"))
}


cat("################### PARAMETERS ################### \n")
# check target directory 
output <- tools::file_path_sans_ext(args$output_file)
file_name <- basename(output)

if (dir.exists(dirname(output))){
  cat(glue("Directory {dirname(output)} already exists"), .sep="\n")
} else {
  cat(glue("Creating directory {dirname(output)}"), .sep="\n")
  dir.create(dirname(output))
}


# load data
cat("Loading data file...")
df <- read.table(args$input_file, sep=',', header=TRUE, quote="\"")
cat("...DONE \n")

wd = args$working_directory
file_id = args$file_id

path2json <- glue("{wd}/data_folder/{file_id}/config_file.json")
cat(glue("Path to config file: {path2json}"), .sep="\n")

cat("Loading config file...")
rule_params <- rjson::fromJSON(file=path2json)
cat("...DONE \n")

# load parameters:
cat("Loading parameters...GPROFILER\n")
enrichment_parameters <- rule_params$enrichment

organism = enrichment_parameters$organism
cat(glue("... organism: {organism}"), .sep="\n")

column_with_genes_id = enrichment_parameters$column_with_gene
cat(glue("... column to parse: {column_with_genes_id}"), .sep="\n")

sources = enrichment_parameters$sources
sources_for_print <- paste(sources, collapse=", ")
cat(glue("... Data source(s) to use : {sources_for_print}"), .sep="\n")

ordered_query = enrichment_parameters$ordered_query
cat(glue("... ordered query: {ordered_query}"), .sep="\n")

exclude_iea = enrichment_parameters$exclude_iea
cat(glue("... excluding IEA evidence code: {exclude_iea}"), .sep="\n")

cat("Loading parameters...DATA\n")
subset_query = enrichment_parameters$subset_query
cat(glue("... subsetting data: {subset_query}"), .sep="\n")
if (subset_query){
  pvalue = enrichment_parameters$subset_params$pvalue
  absolute_value_log2FC = enrichment_parameters$subset_params$abslog2fc
}


cat("Loading parameters...EXPORT\n")
cat("... exporting")
excel_export = enrichment_parameters$exports$excel
if (excel_export){
  cat(" excel +")
}
csv_export = enrichment_parameters$exports$csv
if (csv_export){
  cat(" csv +")
}
rdata_export = enrichment_parameters$exports$rdata
if (rdata_export){
  cat(" rdata +")
}
plots_export = enrichment_parameters$exports$plots
if (plots_export){
  cat(" plots\n")
  max_result_to_plot = enrichment_parameters$max_result_to_plot
  cat(glue("... max_result_to_plot: {max_result_to_plot}"), .sep="\n")
}
cat("Loading parameters...DONE\n")
cat("\n")




cat("################### ANALYSIS ################### \n")
if (subset_query){
  df <- df %>%
    filter(pvalue < as.numeric(enrichment_parameters$subset_params$pvalue))
}
print(sds)

ngenes = dim(df)[1]
cat(glue("Number of query genes: {ngenes}"), .sep="\n")

cat(glue("Query genes from \'{args$column}\' column"), .sep="\n")
query_list <- df[,c(args$column)]

# enrichment analysis
sources <- args$sources

# dummy analysis to get ambiguous genes
cat("Mapping input genes to ENSG identifiers \n")
init <- gost(query = query_list,
             organism = args$organism,
             user_threshold = 0.05,
             significant = TRUE,
             correction_method ='fdr',
             source="GO:MF")


nfailed <- length(init$meta$genes_metadata$failed)
nambiguous <- length(init$meta$genes_metadata$ambiguous)
nduplicated <- length(init$meta$genes_metadata$duplicates)

print(glue("--> {nfailed} failed gene(s) ; {nambiguous} ambiguous gene(s) ; {nduplicated} duplicated genes."))
cat("WARNING: ambiguous genes are not included in analysis\n")
for (s in sources){
  print(glue("#### Analysis running on: {s}"))
  
  output_file <- paste(output, s, sep='_')
  output_file <- gsub(":", "", output_file) # remove special characters as ":" in GO:CC
  output_csv_complete <- paste0(output_file, '_complete.csv')
  output_xlsx <- paste0(output_file, '.xlsx')
  output_rds <- paste0(output_file, '.rds')
  output_dotplot <- paste0(output_file, '_dotplot.png')

  # run gProfiler
  gostres <- gost(query = query_list,
                  organism = args$organism,
                  user_threshold = 0.05,
                  significant = TRUE,
                  correction_method ='fdr',
                  source=s,
                  evcodes = TRUE,
                  ordered_query = args$ordered_query,
                  exclude_iea = args$exclude_iea)
  
  # get results as a data frame
  res <- as.data.frame(gostres$result)
  
  if (dim(res)[1] > 0){
    print(glue("At least one significant result!"))

    if (args$export_rdata){
      print(glue("saving results as RData"))
      saveRDS(gostres, file = output_rds)
    }
    
    # create `negative_log10_of_adjusted_p_value` column
    print(glue("creating -log10(pvalue) column"))
    res$parents <- NULL # column parents is a list of list ? Mess with dataframe format
    res$negative_log10_of_adjusted_p_value <- -log10(res$p_value)
    
    if (args$export_csv){
      print("saving all results as csv")
      write.csv(res, output_csv_complete, row.names=FALSE)
    }

    if (args$export_excel){
      print(glue("Exporting relevant results as excel"))
      
      print(glue("... subsetting data frame"))
      res_filtered <- res[,c("source", "term_name", "term_id", "p_value", "negative_log10_of_adjusted_p_value", "term_size", "query_size", "intersection_size", "intersection")]
      names(res_filtered) <- gsub("p_value", "padj", names(res_filtered)) # change -log10 pvalue column as well
      class(res_filtered$padj) <- "scientific"
      class(res_filtered$negative_log10_of_adjusted_padj) <- "numeric"
      
      print(glue("... creating excel object"))
      options("openxlsx.numFmt" = NULL)
      options("openxlsx.numFmt" = "0.000")
      
      wb <- createWorkbook()
      addWorksheet(wb, "enrichment_results")
      hs <- createStyle(textDecoration = "Bold", border = "Bottom", fontColour = "black")
      writeData(wb, "enrichment_results", res_filtered, headerStyle = hs)
      
      nlines <- nrow(res_filtered) + 1
      icol <- grep("negative_log10_of_adjusted_padj", colnames(res_filtered))

      print(glue("... adding conditional formatting"))
      conditionalFormatting(wb, "enrichment_results", 
                            cols = icol, 
                            rows = 1:nlines, 
                            type = "databar", 
                            rule = c(0, 50),
                            style = c("#0BA31B", "#3FE075"),
                            gradient = FALSE,
                            showvalue = TRUE,
                            border = FALSE)
      class(res_filtered$negative_log10_of_adjusted_padj) <- "number"
      setColWidths(wb, "enrichment_results", cols = 1:ncol(res_filtered), widths = "auto")

      print(glue("... writing excel file"))
      x <- saveWorkbook(wb, output_xlsx, overwrite = TRUE, returnValue = TRUE)

      if (x){
        print(glue("... DONE"))
      } else {
        print(glue("... PROBLEM WITH EXCEL EXPORT"))
      }
      
    }
    if (args$plot_results){
      # plot enrich plot like with DOSE
      enrichment_dotplot_from_gProfiler(res, 0.05, args$max_result_to_plot, glue("{file_name} - {s}"), output_dotplot)
    }
  } else {
    print(glue("No result for this source"))
  }
}


