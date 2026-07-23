# Fast AI Score Checker (R Wrapper)
#
# R wrapper for check_ai_plagiarism.py's check_ai_score_only() function.
# Provides fast AI score checking for real-time writing workflow.
#
# Usage:
#   source("behavior_rules/tools/check_ai_score_fast.R")
#   result <- check_ai_score_fast("path/to/text.txt", fast_mode = TRUE)
#   result <- check_ai_score_fast(text = "Your text here", fast_mode = TRUE)

check_ai_score_fast <- function(file_path = NULL, text = NULL, fast_mode = TRUE) {
  """
  Fast AI score check without plagiarism detection.
  
  Args:
    file_path: Path to text file (optional if text is provided)
    text: Text to check directly (optional if file_path is provided)
    fast_mode: If TRUE, uses only fast methods (basic_ai, text_statistics)
               If FALSE, includes transformers (slower but more accurate)
  
  Returns:
    List with:
    - score: AI probability (0-1)
    - recommendations: Character vector of recommendations
    - method: Detection method used
    - status: "success" or "error"
  """
  
  # Determine script path
  script_dir <- dirname(sys.frame(1)$ofile)
  if (is.null(script_dir)) {
    script_dir <- getwd()
  }
  
  python_script <- file.path(script_dir, "..", "behavior_rules", "tools", "check_ai_plagiarism.py")
  
  # Check if Python script exists
  if (!file.exists(python_script)) {
    stop(paste("Python script not found:", python_script))
  }
  
  # Prepare text input
  if (!is.null(text)) {
    # Use text directly
    temp_file <- tempfile(fileext = ".txt")
    writeLines(text, temp_file)
    input_file <- temp_file
    cleanup_temp <- TRUE
  } else if (!is.null(file_path)) {
    # Use file path
    if (!file.exists(file_path)) {
      stop(paste("File not found:", file_path))
    }
    input_file <- file_path
    cleanup_temp <- FALSE
  } else {
    stop("Either file_path or text must be provided")
  }
  
  # Create temporary Python script to call check_ai_score_only
  temp_py_script <- tempfile(fileext = ".py")
  py_code <- paste0("
import sys
from pathlib import Path
sys.path.insert(0, str(Path('", python_script, "').parent))
from check_ai_plagiarism import check_ai_score_only, read_file
import json

text = read_file('", input_file, "')
result = check_ai_score_only(text, fast_mode=", ifelse(fast_mode, "True", "False"), ")
print(json.dumps(result))
")
  
  writeLines(py_code, temp_py_script)
  
  # Call Python script
  tryCatch({
    python_output <- system(paste("python", shQuote(temp_py_script)), intern = TRUE, ignore.stderr = TRUE)
    
    # Parse JSON output
    if (length(python_output) > 0) {
      result_json <- paste(python_output, collapse = "\n")
      result <- jsonlite::fromJSON(result_json)
    } else {
      stop("Python script returned no output")
    }
    
    # Cleanup
    unlink(temp_py_script)
    if (cleanup_temp) {
      unlink(temp_file)
    }
    
    return(result)
    
  }, error = function(e) {
    # Cleanup on error
    unlink(temp_py_script)
    if (cleanup_temp) {
      unlink(temp_file)
    }
    stop(paste("Error calling Python script:", e$message))
  })
}


# Alternative function that reads text from file
check_ai_score_from_file <- function(file_path, fast_mode = TRUE) {
  """
  Check AI score from a text file.
  
  Args:
    file_path: Path to text file
    fast_mode: If TRUE, uses only fast methods
    
  Returns:
    List with score, recommendations, method, status
  """
  return(check_ai_score_fast(file_path = file_path, fast_mode = fast_mode))
}


# Alternative function that uses text directly
check_ai_score_from_text <- function(text, fast_mode = TRUE) {
  """
  Check AI score from text string.
  
  Args:
    text: Text to check (character vector)
    fast_mode: If TRUE, uses only fast methods
    
  Returns:
    List with score, recommendations, method, status
  """
  return(check_ai_score_fast(text = text, fast_mode = fast_mode))
}


# Example usage
if (!interactive()) {
  args <- commandArgs(trailingOnly = TRUE)
  
  if (length(args) == 0) {
    cat("Usage: Rscript check_ai_score_fast.R <file_path> [fast_mode]\n")
    cat("  file_path: Path to text file\n")
    cat("  fast_mode: TRUE or FALSE (default: TRUE)\n")
    quit(status = 1)
  }
  
  file_path <- args[1]
  fast_mode <- if (length(args) > 1) as.logical(args[2]) else TRUE
  
  result <- check_ai_score_fast(file_path = file_path, fast_mode = fast_mode)
  
  cat("AI Score Check Results:\n")
  cat("======================\n")
  cat(sprintf("AI Probability: %.1f%%\n", result$score * 100))
  cat(sprintf("Method: %s\n", result$method))
  
  if (!is.null(result$component_scores)) {
    cat("\nComponent Scores:\n")
    for (method in names(result$component_scores)) {
      cat(sprintf("  %s: %.1f%%\n", method, result$component_scores[[method]] * 100))
    }
  }
  
  if (!is.null(result$recommendations)) {
    cat("\nRecommendations:\n")
    for (rec in result$recommendations) {
      cat(sprintf("  • %s\n", rec))
    }
  }
  
  # Exit with appropriate code
  if (result$score >= 0.2) {
    quit(status = 1)  # High AI probability
  } else {
    quit(status = 0)  # Low AI probability
  }
}
