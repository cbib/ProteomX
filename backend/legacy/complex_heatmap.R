#!/usr/bin/env Rscript


library(ComplexHeatmap)
library(dplyr)
library(RColorBrewer)

input <- '/home/claire/Documents/ProteomX_Benjamin/data/ANR_ISM_Polyphenolprot200901_PPP190725ac/18_heatmaps_karl/PPP_190725ac_gn.csv'
data <- read.csv(input, header=TRUE, row.names=c('Accession'))

list_litterature <- '/home/claire/Documents/Proteo_PolyphenolProt/Liste_protein_litterature_hsapiens.csv'
list_df <- read.csv(list_litterature, header=TRUE)

criteria = read.csv('/home/claire/Documents/ProteomX_Benjamin/data/annotation_data/criterion_karl_ISM.csv')

# output files
output_file <- '/home/claire/Documents/ProteomX_Benjamin/data/ANR_ISM_Polyphenolprot200901_PPP190725ac/18_heatmaps_karl/PPP_190725ac_170220_gn_alone'



plot_heatmap_cross_section_litterature = function(input_df, df_litterature, output_png){
  

  litterature_df <- droplevels(input_df[input_df$gene_name %in% df_litterature$gene_name, ])
  rownames(litterature_df) <- make.names(litterature_df$gene_name, unique = TRUE)

  metadata <- data.frame(litterature_df$gene_name_bank)
  rownames(metadata) <- rownames(litterature_df)
  colnames(metadata) <- c('gene bank')
  
  metadata[,"todrop"] <- 2
  
  metadata <- metadata[match(df_litterature$gene_name, rownames(metadata)),]

  metadata$todrop <- NULL # otherwise return vector with match(,)
  colors_anno = list("gene bank"=c("Swiss-Prot"="lightblue1","TrEMBL"="lightpink"))
  anno_row <- HeatmapAnnotation(df=metadata, which="row", col = colors_anno, annotation_width=unit(c(1, 4), "cm"), gap=unit(1, "mm"))
  
  litterature_df <- litterature_df %>%
    dplyr::select(-matches('gene'))

  print('OK3')
  
  # order rows as in gene list
  litterature_df <- litterature_df[match(df_litterature$gene_name, rownames(litterature_df)),]
  
  print(metadata)

  
  print(litterature_df)

  # add manip source for each column
  metadata_polyphenolprot <- read.csv('/home/clescoat/Documents/ProteomX/data/PolyPhenolProt/PPP_M5_M6/metadata_polyphenolprot.csv', sep=',')

  
  # subset metadata with manip in experience
  print(metadata_polyphenolprot)
  metadata_polyphenolprot <- metadata_polyphenolprot[metadata_polyphenolprot$name_plot %in% colnames(litterature_df), ]
  
  # order columns per experiences
  litterature_df <- litterature_df[, match(metadata_polyphenolprot$name_plot, colnames(litterature_df))]
  
  print(metadata_polyphenolprot)
  print(colnames(litterature_df))
  experience_anno <- data.frame(metadata_polyphenolprot$experience, 
                                metadata_polyphenolprot$capture_method, 
                                metadata_polyphenolprot$cell,
                                metadata_polyphenolprot$ph)

  experience_anno <- droplevels(experience_anno)
  rownames(experience_anno) <- metadata_polyphenolprot$name_plot
  
  experience_anno <- experience_anno[colnames(litterature_df),] 
  
  colnames(experience_anno) <- c("experience", "method", "cell", "ph")
  experience_anno <- experience_anno[complete.cases(experience_anno), ]
  
  print(experience_anno)
  print('OK4')
  color_anno_columns = list("experience"=c("osteo1"="antiquewhite", "osteo2"="antiquewhite3"),
                            "method"=c("C"="azure3", "D"="azure1"),
                            "cell"=c("OB"="lightblue1", "OC"="lightgoldenrod"),
                            "ph"=c("6.8"="burlywood1", "7.4"="burlywood3"))

  colAnn <- HeatmapAnnotation(df=experience_anno, 
                              which="col", 
                              annotation_width=unit(c(1, 4), "cm"), 
                              gap=unit(1, "mm"),
                              col = color_anno_columns)
  
  litterature_df$Accession <- NULL
  litterature_mat <- as.matrix(litterature_df)
  
  # heatmaps levels colors
  
  colors = c("#515357", "#b8babf", "#e8e9eb", '#FFFFB2', "#FECC5C", "#FD8D3C", "#f0652e", "#BD0026")
  names(colors) = c('A', 'N', 'R', 'E', 'S', 'F', 'CS', 'U')

  print('OK5')

  hmap <- Heatmap(
    litterature_mat,
    name = "expression",
    col = colors,
    column_order = colnames(litterature_mat),
    row_order = rownames(litterature_mat),
    width = unit(100, "mm"),
    top_annotation=colAnn)
  
  print('OK6')

  print(anno_row)
  #plot <- draw(hmap + anno_row, auto_adjust=FALSE)
  plot <- draw(anno_row + hmap, heatmap_legend_side="right", annotation_legend_side="right", auto_adjust=FALSE)
  print('OK6')

  png(filename = output_png, res = 300, units  = 'in', width = 11,
       height = 7)
  print(plot)
  dev.off()
  return(hmap)
}



# plot heatmap ------------------------------------------------------------

input_df <- read.table('/home/claire/Documents/ProteomX_Benjamin/data/ANR_ISM_Polyphenolprot081219/18_intersection_supp/results/intersection_manip6.csv', sep=',')
plot_heatmap_cross_section_litterature(input_df, list_litterature, output_png)

setwd('/home/clescoat/Documents/ProteomX/data/PolyPhenolProt/PPP_M5_M6/')
data_df <- read.csv('/home/clescoat/Documents/ProteomX/data/PolyPhenolProt/PPP_M5_M6/levels/levels_PPP_M5_M6_gn.csv')
list_litterature <- read.csv('/home/clescoat/Documents/ProteomX/data/PolyPhenolProt/PPP_M5_M6/protein_presentation_wasp_gn.csv')
output_png_PPM56 <- '/home/clescoat/Documents/ProteomX/data/PolyPhenolProt/PPP_M5_M6/levels/heatmap_wasp.png'

plot_wasp <- plot_heatmap_cross_section_litterature(data_df, list_litterature, output_png_PPM56)

list_litterature_concept <- read.csv('/home/clescoat/Documents/ProteomX/data/PolyPhenolProt/PPP_M5_M6/protein_presentation_concept_gn.csv')
output_png_PPM56_concept <- '/home/clescoat/Documents/ProteomX/data/PolyPhenolProt/PPP_M5_M6/levels/heatmap_concept.png'

plot_concept <- plot_heatmap_cross_section_litterature(data_df, list_litterature_concept, output_png_PPM56_concept)


metadata_test <- data.frame(list_litterature_concept$gene_name_bank)
rownames(metadata_test) <- list_litterature_concept$gene_name
colnames(metadata_test) <- c('gene bank')
metadata_test[,"test"] <- 2
print(metadata_test)
metadata_test <- metadata_test[order(rownames(metadata_test)),]
metadata_test2 <- metadata_test[match(list_litterature_concept$gene_name, rownames(metadata_test)),]

# previous CS color #F03B20

# brouillon/todo ----------------------------------------------------------

#colors = c('grey', 'black', 'darkorchid', 'dodgerblue2', 'green3', 'gold1', 'orange2', 'red')
#names(colors) = c('A', 'N', 'R', 'E', 'S', 'F', 'CS', 'U')
# heatmaps levels colors NORMAL
#brewer.pal(n = 4, name = "YlOrRd")
#colors = brewer.pal(n = 8, name = "RdBu")

# Basic heatmap with all data

# all_data <- data
# 
# if (nrow(all_data) > 30) {
#   rownames(all_data) <- NULL
# }
# all_data$gene_name <- NULL
# all_data$gene_name_bank <- NULL
# 
# plot <- Heatmap(all_data, col = colors)
# draw(plot)
# 
# png(filename = output_litterature_cs, res = 300, units  = 'in', width = 10,
#     height = 7)
# print(plot)
# dev.off()


