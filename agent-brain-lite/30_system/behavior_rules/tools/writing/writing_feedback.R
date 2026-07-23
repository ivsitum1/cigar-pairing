# Real-Time Feedback System for Writing (R)
#
# This module provides real-time feedback during writing, including:
# - Formatting warnings and suggestions
# - Displaying issues in a user-friendly format
# - Providing actionable recommendations
#
# Usage:
#   source("behavior_rules/tools/writing/writing_feedback.R")
#   feedback <- provide_realtime_feedback(text)
#   cat(format_warnings(feedback))

source(file.path(dirname(sys.frame(1)$ofile), "writing_realtime_check.R"))

format_warnings <- function(issues) {
  """
  Format warnings for display to the user.
  
  Args:
    issues: List of issues from check_all_issues()
    
  Returns:
    Character vector with formatted warnings
  """
  if (length(issues$banned_words) == 0 && 
      length(issues$ai_phrases) == 0 && 
      length(issues$sentence_patterns) == 0) {
    return("✓ No issues detected. Text looks good!")
  }
  
  output <- character()
  total_issues <- length(issues$banned_words) + 
                  length(issues$ai_phrases) + 
                  length(issues$sentence_patterns)
  
  output <- c(output, paste0("⚠️  ", total_issues, " issue(s) detected:\n"))
  
  # Banned words
  if (length(issues$banned_words) > 0) {
    output <- c(output, "📝 BANNED WORDS:")
    for (issue in issues$banned_words) {
      line_num <- issue$location[1]
      pos <- issue$location[2]
      output <- c(output, 
                  paste0("  ⚠️  Line ", line_num, ", position ", pos, ": \"", issue$text, "\""),
                  paste0("     → ", issue$suggestion))
    }
    output <- c(output, "")
  }
  
  # AI phrases
  if (length(issues$ai_phrases) > 0) {
    output <- c(output, "💬 AI PHRASES:")
    for (issue in issues$ai_phrases) {
      line_num <- issue$location[1]
      pos <- issue$location[2]
      output <- c(output, 
                  paste0("  ⚠️  Line ", line_num, ", position ", pos, ": \"", issue$text, "\""),
                  paste0("     → ", issue$suggestion))
    }
    output <- c(output, "")
  }
  
  # Sentence patterns
  if (length(issues$sentence_patterns) > 0) {
    output <- c(output, "📐 SENTENCE PATTERNS:")
    for (issue in issues$sentence_patterns) {
      line_num <- issue$location[1]
      pos <- issue$location[2]
      output <- c(output, 
                  paste0("  ⚠️  Line ", line_num, ", position ", pos, ": ", issue$text),
                  paste0("     → ", issue$suggestion))
    }
    output <- c(output, "")
  }
  
  return(paste(output, collapse = "\n"))
}


format_suggestions <- function(issues, max_suggestions = 5) {
  """
  Format suggestions for improvement.
  
  Args:
    issues: List of issues from check_all_issues()
    max_suggestions: Maximum number of suggestions to show (integer)
    
  Returns:
    Character vector with formatted suggestions
  """
  if (length(issues$banned_words) == 0 && 
      length(issues$ai_phrases) == 0 && 
      length(issues$sentence_patterns) == 0) {
    return("No suggestions needed. Text is already well-written!")
  }
  
  # Combine all issues
  all_issues <- c(issues$banned_words, issues$ai_phrases, issues$sentence_patterns)
  
  # Sort by severity (high > medium > low)
  severity_order <- c("high" = 3, "medium" = 2, "low" = 1)
  all_issues <- all_issues[order(sapply(all_issues, function(x) {
    severity_order[x$severity]
  }), decreasing = TRUE)]
  
  # Get top suggestions
  top_issues <- all_issues[1:min(max_suggestions, length(all_issues))]
  
  output <- c("💡 TOP SUGGESTIONS FOR IMPROVEMENT:\n")
  
  for (i in seq_along(top_issues)) {
    issue <- top_issues[[i]]
    line_num <- issue$location[1]
    output <- c(output,
                paste0(i, ". ", issue$text, " (Line ", line_num, ")"),
                paste0("   → ", issue$suggestion),
                "")
  }
  
  if (length(all_issues) > max_suggestions) {
    output <- c(output, paste0("... and ", length(all_issues) - max_suggestions, " more issue(s)"))
  }
  
  return(paste(output, collapse = "\n"))
}


provide_realtime_feedback <- function(text) {
  """
  Provide real-time feedback on the text.
  
  Args:
    text: Text to check (character vector)
    
  Returns:
    List with issues, warnings, and suggestions
  """
  issues <- check_all_issues(text)
  
  warnings <- format_warnings(issues)
  suggestions <- format_suggestions(issues)
  
  # Calculate summary statistics
  total_issues <- length(issues$banned_words) + 
                  length(issues$ai_phrases) + 
                  length(issues$sentence_patterns)
  
  high_severity <- sum(sapply(c(issues$banned_words, issues$ai_phrases, issues$sentence_patterns), 
                              function(x) x$severity == "high"))
  medium_severity <- sum(sapply(c(issues$banned_words, issues$ai_phrases, issues$sentence_patterns), 
                                function(x) x$severity == "medium"))
  low_severity <- sum(sapply(c(issues$banned_words, issues$ai_phrases, issues$sentence_patterns), 
                             function(x) x$severity == "low"))
  
  return(list(
    issues = issues,
    warnings = warnings,
    suggestions = suggestions,
    summary = list(
      total_issues = total_issues,
      high_severity = high_severity,
      medium_severity = medium_severity,
      low_severity = low_severity
    )
  ))
}


display_feedback <- function(feedback, show_summary = TRUE) {
  """
  Display feedback in a formatted way.
  
  Args:
    feedback: Feedback list from provide_realtime_feedback()
    show_summary: Whether to show summary statistics (logical)
  """
  cat(rep("=", 60), "\n", sep = "")
  cat("REAL-TIME WRITING FEEDBACK\n")
  cat(rep("=", 60), "\n", sep = "")
  cat("\n")
  
  if (show_summary) {
    summary <- feedback$summary
    cat(sprintf("Total Issues: %d\n", summary$total_issues))
    cat(sprintf("  - High severity: %d\n", summary$high_severity))
    cat(sprintf("  - Medium severity: %d\n", summary$medium_severity))
    cat(sprintf("  - Low severity: %d\n", summary$low_severity))
    cat("\n")
  }
  
  cat(feedback$warnings, "\n")
  cat("\n")
  cat(feedback$suggestions, "\n")
  cat(rep("=", 60), "\n", sep = "")
}


# Example usage (when run directly)
if (!interactive()) {
  sample_text <- "
  This article will discuss the intricate complexities of the research.
  It is important to note that we delved into the realm of comprehensive analysis.
  The findings aren't just significant, they're pivotal to understanding the landscape.
  "
  
  feedback <- provide_realtime_feedback(sample_text)
  display_feedback(feedback)
}
