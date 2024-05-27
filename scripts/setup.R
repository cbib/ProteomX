#!/usr/bin/env Rscript


lubripack_BiocManager <- function(...,silent=FALSE){

  #check names and run 'require' function over if the given package is installed
  requirePkg<- function(pkg){if(length(setdiff(pkg,rownames(installed.packages())))==0)
                                    require(pkg, quietly = TRUE,character.only = TRUE,warn.conflicts=FALSE)
                            }

  packages <- as.vector(unlist(list(...)))
  if(!is.character(packages))stop("No numeric allowed! Input must contain package names to install and load")

  if (length(setdiff(packages,rownames(installed.packages()))) > 0 )
     BiocManager::install(setdiff(packages,rownames(installed.packages())))

  res<- unlist(sapply(packages, requirePkg))

  if(silent == FALSE && !is.null(res)) {cat("\nBellow CRAN Packages Successfully Installed:\n\n")
                    print(res)
                   }
}

lubripack <- function(...,silent=FALSE){

  #check names and run 'require' function over if the given package is installed
  requirePkg<- function(pkg){if(length(setdiff(pkg,rownames(installed.packages())))==0)
                                    require(pkg, quietly = TRUE,character.only = TRUE, warn.conflicts=FALSE)
                            }

  packages <- as.vector(unlist(list(...)))
  if(!is.character(packages))stop("No numeric allowed! Input must contain package names to install and load")

  if (length(setdiff(packages,rownames(installed.packages()))) > 0 )
     install.packages(setdiff(packages,rownames(installed.packages())),
                      repos = c("http://cran.us.r-project.org"))

  res<- unlist(sapply(packages, requirePkg))

  if(silent == FALSE && !is.null(res)) {cat("\nBellow BioConductor Packages Successfully Installed:\n\n")
                    print(res)
                   }
}

lubripack("tibble", "paletteer", "dplyr", "factoextra", "FactoMineR", "dendextend", "RColorBrewer",
           "argparse", "dichromat", "gprofiler2", "ggplot2", "openxlsx", "readxl", "pheatmap", "tidyverse",
            "data.table", "glue","rjson","stringr","BiocManager", silent = FALSE)

lubripack_BiocManager("ComplexHeatmap","EnhancedVolcano", silent = FALSE)

# a<-installed.packages()
# packages<-a[,1]
# if(!is.element("tibble", packages)){
#   install.packages("tibble", repos='http://cran.us.r-project.org')
# }
# if(!is.element("paletteer", packages)){
#   install.packages("paletteer", repos='http://cran.us.r-project.org')
# }
# if(!is.element("dplyr", packages)){
#   install.packages("dplyr", repos='http://cran.us.r-project.org')
# }
# if(!is.element("factoextra", packages)){
#   install.packages("factoextra", repos='http://cran.us.r-project.org')
# }
# if(!is.element("FactoMineR", packages)){
#   install.packages("FactoMineR", repos='http://cran.us.r-project.org')
# }
# if(!is.element("dendextend", packages)){
#   install.packages("dendextend", repos='http://cran.us.r-project.org')
# }
# if(!is.element("RColorBrewer", packages)){
#   install.packages("RColorBrewer", repos='http://cran.us.r-project.org')
# }
# if(!is.element("argparse", packages)){
#   install.packages("argparse", repos='http://cran.us.r-project.org')
# }
# if(!is.element("dichromat", packages)){
#   install.packages("dichromat", repos='http://cran.us.r-project.org')
# }
# if(!is.element("gprofiler2", packages)){
#   install.packages("gprofiler2", repos="https://cran.irsn.fr/")
# }
# if(!is.element("ggplot2", packages)){
#   install.packages("ggplot2", repos="https://cran.irsn.fr/")
# }
# if(!is.element("openxlsx", packages)){
#   install.packages("openxlsx", repos="https://cran.irsn.fr/")
# }
# if(!is.element("readxl", packages)){
#   install.packages("readxl", repos="https://cran.irsn.fr/")
# }
# if(!is.element("pheatmap", packages)){
#   install.packages("pheatmap", repos='http://cran.us.r-project.org')
# }
# if(!is.element("tidyverse", packages)){
#   install.packages("tidyverse", repos='http://cran.us.r-project.org')
# }
# if(!is.element("data.table", packages)){
#   install.packages("data.table", repos='http://cran.us.r-project.org')
# }
# if(!is.element("glue", packages)){
#   install.packages("glue", repos='http://cran.us.r-project.org')
# }
# if(!is.element("rjson", packages)){
#   install.packages("rjson")
# }
# if(!is.element("stringr", packages)){
#   install.packages("stringr")
# }
# if(!is.element("ComplexHeatmap", packages)){
#   if (!requireNamespace("BiocManager", quietly = TRUE))
#     install.packages("BiocManager", repos='http://cran.us.r-project.org')
#   BiocManager::install("ComplexHeatmap")
# }
# if(!is.element("EnhancedVolcano", packages)){
#   if (!requireNamespace("BiocManager", quietly = TRUE))
#     install.packages("BiocManager")
#   BiocManager::install("EnhancedVolcano")
# }
#
# print(packages<-a[,1])
