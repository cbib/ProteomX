#!/usr/bin/env Rscript

# Wrapper for gProfiler enrichment analysis
# takes a data frame with a least a column (-c) with gene list
# run analysis on specified sources (-s) (or all if nothing is specified)
# returns a formatted excel file with significant results

# a<-installed.packages()
# packages<-a[,1]
# if(!is.element("argparse", packages)){
#   install.packages("argparse", repos="https://cran.irsn.fr/")
# }
library(argparse)
# a<-installed.packages()
# packages<-a[,1]
# if(!is.element("gprofiler2", packages)){
#   install.packages("gprofiler2", repos="https://cran.irsn.fr/")
# }
library(gprofiler2)
# a<-installed.packages()
# packages<-a[,1]
# if(!is.element("glue", packages)){
#   install.packages("glue", repos="https://cran.irsn.fr/")
# }
library(glue)
# a<-installed.packages()
# packages<-a[,1]
# if(!is.element("ggplot2", packages)){
#   install.packages("ggplot2", repos="https://cran.irsn.fr/")
# }
library(ggplot2)


# a<-installed.packages()
# packages<-a[,1]
# if(!is.element("openxlsx", packages)){
#   install.packages("openxlsx", repos="https://cran.irsn.fr/")
# }
library(openxlsx)

# a<-installed.packages()
# packages<-a[,1]
# if(!is.element("dplyr", packages)){
#   install.packages("dplyr", repos="https://cran.irsn.fr/")
# }
library(dplyr)

# a<-installed.packages()
# packages<-a[,1]
# if(!is.element("readxl", packages)){
#   install.packages("readxl", repos="https://cran.irsn.fr/")
# }
library("readxl")


## Create parser object
parser <- ArgumentParser()

## Specify arguments
parser$add_argument("-i", "--input_file", help = "input file")
parser$add_argument("-o", "--output_file", help = "output file")
parser$add_argument("-f", "--file_id", help = "Project ID")
parser$add_argument("-wd", "--working_directory", help = "Working directory (ProteomX)")



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

ndim = dim(df)
cat(glue("Dimension of input data frame: {ndim}"), .sep="\n")


wd = args$working_directory
file_id = args$file_id

path2json <- glue("{wd}/data/{file_id}/config_file.json")
cat(glue("Path to config file: {path2json}"), .sep="\n")

cat("Loading config file...")
rule_params <- rjson::fromJSON(file=path2json)
cat("...DONE \n")

# load parameters:
cat("Loading parameters...GPROFILER\n")
enrichment_parameters <- rule_params$enrichment

organism = rule_params$all$organism
cat(glue("... organism: {organism}"), .sep="\n")

column_with_genes_id = enrichment_parameters$column_with_gene
cat(glue("... column to parse: {column_with_genes_id}"), .sep="\n")

sources = enrichment_parameters$sources
sources_for_print <- paste(sources, collapse=", ")
cat(glue("... Data source(s) to use : {sources_for_print}"), .sep="\n")
ordered_query = enrichment_parameters$ordered_query
cat(glue("... ordered query: {ordered_query}"), .sep="\n")

if (ordered_query){
  sort_by = enrichment_parameters$sort_by
  cat(glue("... ordered query: {ordered_query}"), .sep="\n")

}

exclude_iea = enrichment_parameters$exclude_iea
cat(glue("... excluding IEA evidence code: {exclude_iea}"), .sep="\n")

cat("Loading parameters...DATA\n")
subset_query = enrichment_parameters$subset_query
cat(glue("... subsetting data: {subset_query}"), .sep="\n")

if (subset_query){
  threshold_pvalue = enrichment_parameters$subset_params$pvalue
  cat(glue("... excluding protein on pvalue: {threshold_pvalue}"), .sep="\n")
  threshold_padj = enrichment_parameters$subset_params$padj
  cat(glue("... excluding protein on padj: {threshold_padj}"), .sep="\n")
  threshold_absolute_value_log2FC = enrichment_parameters$subset_params$abslog2fc
  cat(glue("... excluding protein on abs(log2FoldChange): {threshold_absolute_value_log2FC}"), .sep="\n")
  gene_bank = enrichment_parameters$subset_params$gene_bank
  threshold_overlap = enrichment_parameters$subset_params$overlap
}


cat("Loading parameters...EXPORT\n")
cat("... exporting")
export_excel = enrichment_parameters$exports$excel
if (export_excel){
  cat(" excel +")
}
export_csv = enrichment_parameters$exports$csv
if (export_csv){
  cat(" csv +")
}
export_rdata = enrichment_parameters$exports$rdata
if (export_rdata){
  cat(" rdata ")
}
export_plots = enrichment_parameters$exports$plots
if (export_plots){
  cat("+ plots\n")
  max_result_to_plot = enrichment_parameters$max_result_to_plot
  cat(glue("... max_result_to_plot: {max_result_to_plot}"), .sep="\n")
}
cat("\nLoading parameters...DONE\n")
cat("\n")


cat("################### ANALYSIS ################### \n")

#to avoid problem with distribution fitting test that compute only pvalue
if(!"padj" %in% colnames(df))
{
  df$padj=df$pvalue
}

if (subset_query){

  cat(glue("Filtering data frame"), .sep="\n")
  df <- df %>%
    dplyr::filter(if (threshold_pvalue) pvalue < as.numeric(threshold_pvalue) else TRUE) %>%
    dplyr::filter(if (threshold_padj) padj < as.numeric(threshold_padj) else TRUE) %>%
    dplyr::filter(if (threshold_overlap) overlap > 0 else TRUE) %>%
    dplyr::filter(if (threshold_absolute_value_log2FC) abs(log2FoldChange) > as.numeric(threshold_absolute_value_log2FC) else TRUE) %>%
    dplyr::filter(if (gene_bank == "Swiss-Prot") gene_name_bank %in% c("UNIPROTSWISSPROT_ACC,UNIPROT_GN_ACC", "UNIPROTSWISSPROT_ACC", "Swiss-Prot") else TRUE) %>%
    droplevels()
}

max_pvalue <- max(df$pvalue, na.rm = TRUE)
max_padj <- max(df$padj, na.rm = TRUE)
min_abslog2FC <- min(abs(df$log2FoldChange), na.rm = TRUE)

cat(glue("max value (pvalue): {max_pvalue}"), .sep="\n")
cat(glue("max value (padj): {max_padj}"), .sep="\n")
cat(glue("min absolute value (log2FoldChange): {min_abslog2FC}"), .sep="\n")


ngenes = dim(df)[1]
cat(glue("Number of query genes: {ngenes}"), .sep="\n")

if (ngenes == 0){
  final <- data.frame ("all done!")
  write.csv(final, args$output_file, row.names=FALSE)
  quit(status=0)
}
print(column_with_genes_id)
query_list <- df[,c(column_with_genes_id)]

if (ordered_query){
	query_list <- query_list[order(query_list)]
}
# dummy analysis to get ambiguous genes
cat("Mapping input genes to ENSG identifiers \n")
init <- gost(query = query_list,
             organism = organism,
             user_threshold = 0.05,
             significant = TRUE,
             correction_method ='fdr',
             source="GO:MF")





nfailed <- length(init$meta$genes_metadata$failed)
nambiguous <- length(init$meta$genes_metadata$ambiguous)
nduplicated <- length(init$meta$genes_metadata$duplicates)

print(glue("--> {nfailed} failed gene(s) ; {nambiguous} ambiguous gene(s) ; {nduplicated} duplicated genes."))
cat("WARNING: ambiguous genes are not included in analysis\n")
res <- data.frame()

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
                  organism = organism,
                  user_threshold = 0.05,
                  significant = TRUE,
                  correction_method ='fdr',
                  source=s,
                  evcodes = TRUE,
                  ordered_query = ordered_query,
                  exclude_iea = exclude_iea)
  
  # get results as a data frame
  res <- as.data.frame(gostres$result)

  if (dim(res)[1] > 0){
    print(glue("At least one significant result!"))
    
    if (export_rdata){
      print(glue("saving results as RData"))
      saveRDS(gostres, file = output_rds)
    }
    
    # create `negative_log10_of_adjusted_p_value` column
    print(glue("creating -log10(pvalue) column"))
    res$parents <- NULL # column parents is a list of list ? Mess with dataframe format
    res$negative_log10_of_adjusted_p_value <- -log10(res$p_value)
    
    if (export_csv){
      print("saving all results as csv")
      write.csv(res, output_csv_complete, row.names=FALSE)
    }
    
    if (export_excel){
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
    if (export_plots){
      # plot enrich plot like with DOSE
      enrichment_dotplot_from_gProfiler(res, 0.05, max_result_to_plot, glue("{file_name} - {s}"), output_dotplot)
    }
  } else {
    print(glue("No result for this source"))
  }
}


full_path=dirname(output)
input_files=list.files(dirname(output), pattern = "\\.xlsx$")

for (input_file in input_files){

  input <- tools::file_path_sans_ext(input_file)
  input_file_name <- basename(input)
  project_name='enrichment_gprofiler'

  # load data
  cat("Loading data file...")

  df <- read_excel(paste(dirname(output),"/",input_file, sep=""))

  cat("...DONE \n")

  ndim = dim(df)
  cat(glue("Dimension of input data frame: {ndim}"), .sep="\n")
  # xls files
  fig_fn=paste(paste(dirname(output),"/", sub('\\.csv$', '',input_file_name ), "-log10padj.jpeg", sep =""))
  if (dim(df)[[1]]>20){
    df=df[1:20,]
  }

  df=df[order(df$negative_log10_of_adjusted_padj),]
  print(df)
  print(df$term_name)
  df=df[!duplicated(df$term_name),]
  print(df)
  df$term_name <- factor(df$term_name, levels = df$term_name)
  df$percentage=(as.numeric(df$intersection_size)/as.numeric(df$query_size))*100.0

  min_df=min(df$intersection_size)
  max_df=max(df$intersection_size)
  df$intersection_size_f <- cut(df$intersection_size, breaks= seq(min_df-min_df/2, max_df+max_df/2, by = max_df/length(df$intersection_size)),labels=seq(min_df-min_df/2, max_df+max_df/2, by = max_df/length(df$intersection_size))[-1])

  #df$intersection_size = relevel(df$intersection_size, ref=4)
  cond1=strsplit(strsplit(input_file_name,paste(project_name,"_", sep=""))[[1]][2], "_vs_")[[1]][1]
  cond2=strsplit(strsplit(strsplit(input_file_name,paste(project_name,"_", sep=""))[[1]][2], "_vs_")[[1]][2], "_GO")[[1]][1]
  GO_field=paste( "GO ", strsplit(strsplit(strsplit(input_file_name,paste(project_name,"_", sep=""))[[1]][2], "_vs_")[[1]][2], "_GO")[[1]][2], sep="")
  title=paste(project_name," ", cond1," vs ", cond2, " - ", GO_field)

  p <- ggplot(df, aes(x=term_name, y=negative_log10_of_adjusted_padj)) +
    ylim(c(min(df$negative_log10_of_adjusted_padj) - 0.5, max(df$negative_log10_of_adjusted_padj) + 0.5))  +
    geom_point(data=NULL,stat="identity", aes(size = as.factor(intersection_size_f), color=percentage), position_dodge(width = 0.5)    )  +
    labs(subtitle="Gprofiler2 v0.2.1",
         title="Enrichment dot plot",
         y="-log10(p-adj)",
         size="Count", color="%") +
    #theme_bw(base_size = 15) +
    theme(panel.background = element_rect(fill = "white"),
          panel.border = element_rect(colour = "grey", fill=NA),
          panel.grid.major = element_line(colour = "grey", size = 0.25),
          panel.grid.minor = element_line(colour = "grey", size = 0.15),
          axis.text.y = element_text(color = "grey20", size = 13, angle = 0, hjust = 1, vjust = .5, face = "plain"),
          axis.title.y = element_blank()
    ) +
    coord_flip()+
    scale_color_gradient(low="red", high="blue") #+
  #scale_size_manual(values=c(25,50,75,100))
  jpeg(fig_fn, width = 10, height = 10 ,units = "in",res= 600,pointsize = 4)
  print(p)
  dev.off()
}


# Snakemake 
final <- data.frame ("all done!")
write.csv(final, args$output_file, row.names=FALSE)

