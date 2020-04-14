library(RColorBrewer)
library(tidyverse)
library(data.table)
#library(NormalizeMets)

# Wilcoxon rank sum -------------------------------------------------------
wilcoxon_test <- function(df, controls, patients, output_file){
  # controls : dataframe with abundances for controls patients ; genes are row names, sample names are column names. 
  # patients : dataframe with abundances for patients patients ; genes are row names, sample names are column names. 
  # geneList : list of individual genes in the panel
  # output_file : output path for csv 
  
  # this function computes the wilcoxon test for relevant groups and output a csv file with statistics 
  print(head(controls))
  print(as.numeric(controls[2,]))
  # Compute wilcoxon test
  pvalue = sapply(rownames(df), function(x){ wilcox.test(as.numeric(controls[x,]), as.numeric(patients[x,]))$p.value })
  print(pvalue)
  wilcox_results =  sapply(rownames(df), function(x){ wilcox.test(as.numeric(controls[x,]), as.numeric(patients[x,]))$statistic })
  print(wilcox_results)
  # create vector of FDr corrected p values.
  padj= p.adjust(pvalue, method="fdr")
  
  # create list of log2foldchanges
  ## fold changes are on the geometric mean of the changes between samples for the two conditions.
  log2FC = foldchange2logratio(sapply(rownames(df), function(x){ foldchange(gm_mean(as.numeric(patients[x,])), gm_mean(as.numeric(controls[x,]))) } ), base=2)
  
  # create table of p.value, logfoldchange and FDRs
  wilcox_test_result_table = cbind.data.frame(rownames(df), pvalue, padj, log2FC)
  
  # export table
  #write.csv(wilcox_test_result_table, output_file)
  return(wilcox_test_result_table)
}





# geometric mean ----------------------------------------------------------
gm_mean = function(x, na.rm=TRUE, zero.propagate = FALSE){
  if(any(x < 0, na.rm = TRUE)){
    return(NaN)
  }
  if(zero.propagate){
    if(any(x == 0, na.rm = TRUE)){
      return(0)
    }
    exp(mean(log(x), na.rm = na.rm))
  } else {
    exp(sum(log(x[x > 0]), na.rm=na.rm) / length(x))
  }
}



# Volcano_plot ------------------------------------------------------------
volcano_plot = function(input_df, output_file, plot_name, id_col){
  # Function that returns a volcano plot with the NormalizeMets package volcano function
  # inpt_df : dataframe with at least 
  # output_file : name of the png file
  # plot_name : title of the plot
  # id_col : column with identifiers (protein accession, gene name...)
  
  ## Conditions names
  abundance_df <- input_df %>%
    select(matches('GR_'))
  #print(head(abundance_df))
  colnames(abundance_df) <- gsub('_reference', '', colnames(abundance_df), fixed=TRUE)
  colnames(abundance_df) <- gsub('_REP_[0-9]{1,2}', '', colnames(abundance_df), fixed=TRUE)
  coef <- input_df$Log2FoldChange
  names(coef) <- input_df[[id_col]]
  
  VolcanoPlot(coef = coef,
              pvals = input_df$padj,
              cexcutoff = 0.0, 
              cexlab = 5, 
              pointsize = 0.9,
              plimit = 0.05, 
              coeflimit = 1,
              negcontrol = NULL, 
              poscontrol = NULL,
              saveplot = TRUE, 
              plotname = output_file, 
              savetype = c("png", "bmp", "jpeg", "tiff", "pdf"), 
              xlab = "log2FoldChange", ylab = "-log(p-adjusted)",
              labelunderlim = FALSE, 
              labelsig = FALSE, 
              interactiveplot = FALSE,
              saveinteractiveplot = FALSE,
              interactiveplotname = "interactiveVolcanPlot", 
              interactiveonly = FALSE,
              main = plot_name, 
              fclabel = "", chooselegend = NULL,
              vlines = TRUE, 
              tolabel = NULL)
}








# Violin_plot ------------------------------------------------------------
vp_prepare_df = function(df, id){
  # Function that returns a dataframe ready to be used for violin plot function
  # df : dataframe with at least 
  # experience : name of experience (string)
  
  df$group <- id
  ratio_col <- df %>%
    select(matches('ratio'))
  
  df <- rename(df, ratio = colnames(ratio_col)[1])
  df <- select(df, Accession, group, ratio)
  return(df)
  
}

vp_plot = function(output_file, ...){
  # Function that returns a violin plot
  #... : list of dataframes with a value to plot against categorical variable, with all the same colnames
  # output_file : path to output png
  
  df_toplot <- bind_rows(...)
  
  # supress arbitrary ratio = 1000 that would affect violin plot aspect 
  df_toplot <- df_toplot[df_toplot$ratio != 1000,]
  
  violinplot <- ggplot(df_toplot, aes(x=group, y=ratio, color = group)) + 
    geom_violin(trim=TRUE)
  violinplot <- violinplot + geom_boxplot(width=0.1)
  
  png(filename = output_file, res = 300, units  = 'in', width = 10,
      height = 7)
  print(violinplot)
  dev.off()
}

vp_plot_log = function(output_file, group_order, ...){
  # Function that returns a violin plot
  #... : list of dataframes with a value to plot against categorical variable, with all the same colnames
  # output_file : path to output png
  
  df_toplot <- bind_rows(...)
  
  # supress arbitrary ratio = 1000 that would affect violin plot aspect 
  df_toplot <- df_toplot[df_toplot$ratio != 1000,]
  df_toplot <- df_toplot[df_toplot$ratio != 0.01,]
  
  # log value 
  df_toplot[, 3] <- log(df_toplot[3], 2)
  
  # plot violin plot (ggplot2)
  violinplot <- ggplot(df_toplot, aes(x=group, y=ratio, color = group)) + 
    geom_violin(trim=TRUE)
  violinplot <- violinplot + geom_boxplot(width=0.1)
  violinplot <- violinplot + scale_x_discrete(limits=group_order)
  
  png(filename = output_file, res = 300, units  = 'in', width = 10,
      height = 7)
  print(violinplot)
  dev.off()
}

# Enrichissement plot -----------------------------------------------------

data_test <- data_filtered
data_test_up <- subset(data_test, log2FC > 0)
data_test_down <- subset(data_test, log2FC < 0)


res_filtered <- subset(res, padj < 0.05, select=c(res.wilcox, padj, log2FC))
graph_enrichR_bidirectional <- function(up,down,significance_threshold,graph_title){
  #### Source of following code: Ahmad Mousavi's ggplot2 script 
  # https://www.biostars.org/p/343196/
  up$type <- "up"
  down$type <- "down"
  
  # either have the 20 elements filter before the ordering, in which case it's the 20 best unadjjusted p-values that are selected:
  up <- up[order(up$Adjusted.P.value), ]  
  up <- up[up$Adjusted.P.value < significance_threshold,]
  up$Adjusted.P.value <- -log10(up$Adjusted.P.value)
  # or have it afterwards, in which case it's the 20 highest combined scores (pval*zscore) that are chosen for the graph:
  # in this case it might be necessary to get the orderingof Combined Scores to be decreasing too...
  #up <- up [c(1:20),]
  
  down <- down[order(down$Combined.Score), ]  # sort
  down <- down[down$Adjusted.P.value < significance_threshold,]
  down$Adjusted.P.value <- log10(down$Adjusted.P.value)
  
  #up <- up [c(1:20),]
  gos <- rbind(down,up)
  gos$Term <- factor(gos$Term, levels=unique(gos$Term))
  # Diverging Barcharts
  ggplot(gos, aes(x=Term, y=Adjusted.P.value, ylab("test"))) +
    ylim(c(min(gos$Adjusted.P.value)-1,max(gos$Adjusted.P.value)+1))  + # add extra space to y axis
    #geom_bar(stat='identity', aes(fill=type) ,position="dodge", width=.5)  +
    geom_point(data=NULL,stat="identity", aes(colour = type,size = as.numeric(sub("/.*","",Overlap))),position_dodge(width = 0.5)    )  +
    scale_colour_manual(name="Expression", 
                        labels = c("Down regulated", "Up regulated"), 
                        values = c("down"="#f8766d", "up"="#00ba38")) + 
    labs(subtitle="functional enrichment analysis", 
         title= graph_title,
         y="-log10(Adj.P.value)",
         size="Gene Counts") +
    coord_flip()
  #return(gos[,c(1,8)]) # return the gos term, for checking.
}