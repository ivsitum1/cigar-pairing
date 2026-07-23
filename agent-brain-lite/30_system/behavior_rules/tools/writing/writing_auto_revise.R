# Auto-Revision Engine for AI-Generated Text (R)
#
# This module automatically revises text to reduce AI detection scores by:
# - Replacing banned words with suggestions
# - Varying sentence beginnings and lengths
# - Eliminating AI phrases
# - Improving paragraph structure
#
# Usage:
#   source("behavior_rules/tools/writing/writing_auto_revise.R")
#   result <- auto_revise_text(text, ai_score = 0.75)

source(file.path(dirname(sys.frame(1)$ofile), "writing_realtime_check.R"))

identify_ai_issues <- function(text) {
  """
  Identify all AI-related issues in the text.
  
  Args:
    text: Text to analyze (character vector)
    
  Returns:
    List with categorized issues
  """
  return(list(
    banned_words = check_banned_words_realtime(text),
    ai_phrases = check_ai_phrases(text),
    sentence_patterns = analyze_sentence_patterns(text)
  ))
}


apply_fixes <- function(text, issues) {
  """
  Apply fixes to the text based on identified issues.
  
  Args:
    text: Original text (character vector)
    issues: List of issues from identify_ai_issues()
    
  Returns:
    List with revised_text and changes_made
  """
  revised_text <- text
  lines <- strsplit(revised_text, "\n")[[1]]
  changes_made <- character()
  
  # Fix banned words
  for (issue in issues$banned_words) {
    line_num <- issue$location[1]
    if (line_num <= length(lines)) {
      line <- lines[line_num]
      word <- issue$text
      
      # Get replacement suggestions
      replacements <- suggest_replacements(word)
      if (length(replacements) > 0) {
        # Use first suggestion
        replacement <- replacements[1]
        
        # Replace word (case-insensitive, whole word only)
        pattern <- paste0("\\b", gsub("([.])", "\\\\\\1", word), "\\b")
        if (grepl(pattern, line, ignore.case = TRUE)) {
          lines[line_num] <- gsub(pattern, replacement, line, ignore.case = TRUE)
          changes_made <- c(changes_made, paste0("Replaced '", word, "' with '", replacement, "'"))
        }
      }
    }
  }
  
  # Fix AI phrases
  for (issue in issues$ai_phrases) {
    line_num <- issue$location[1]
    if (line_num <= length(lines)) {
      line <- lines[line_num]
      phrase <- issue$text
      suggestion <- issue$suggestion
      
      # Remove or replace phrase
      if (grepl("remove", suggestion, ignore.case = TRUE) || 
          grepl("state directly", suggestion, ignore.case = TRUE)) {
        # Remove the phrase
        pattern <- gsub("([.])", "\\\\\\1", phrase)
        lines[line_num] <- gsub(pattern, "", line, ignore.case = TRUE)
        changes_made <- c(changes_made, paste0("Removed phrase: '", phrase, "'"))
      } else {
        # Replace with suggestion
        pattern <- gsub("([.])", "\\\\\\1", phrase)
        replacement <- strsplit(suggestion, " or ")[[1]][1]  # Use first option
        lines[line_num] <- gsub(pattern, replacement, line, ignore.case = TRUE)
        changes_made <- c(changes_made, paste0("Replaced phrase '", phrase, "' with '", replacement, "'"))
      }
    }
  }
  
  # Fix sentence patterns
  for (issue in issues$sentence_patterns) {
    line_num <- issue$location[1]
    if (line_num <= length(lines)) {
      line <- lines[line_num]
      suggestion <- issue$suggestion
      
      # Handle different pattern types
      if (grepl("negation reframe", issue$text, ignore.case = TRUE)) {
        # Split negation reframe: "X isn't just Y, it's Z" -> "X is Y. It also includes Z."
        pattern <- "(.+?)\\s+isn't\\s+just\\s+(.+?),\\s+it's\\s+(.+?)"
        match <- regmatches(line, regexpr(pattern, line, ignore.case = TRUE))
        if (length(match) > 0) {
          # Extract parts (simplified - full implementation would use regex groups)
          new_line <- gsub(pattern, "\\1 is \\2. It also includes \\3.", line, ignore.case = TRUE)
          lines[line_num] <- new_line
          changes_made <- c(changes_made, "Fixed negation reframe pattern")
        }
      } else if (grepl("generic intro", issue$text, ignore.case = TRUE)) {
        # Remove generic intro
        pattern <- "this\\s+article\\s+will\\s+discuss\\s*"
        lines[line_num] <- gsub(pattern, "", line, ignore.case = TRUE)
        changes_made <- c(changes_made, "Removed generic intro pattern")
      } else if (grepl("generic sign-off", issue$text, ignore.case = TRUE)) {
        # Remove generic sign-off
        pattern <- "in\\s+conclusion,\\s+this\\s+article\\s+shows\\s*"
        lines[line_num] <- gsub(pattern, "", line, ignore.case = TRUE)
        changes_made <- c(changes_made, "Removed generic sign-off pattern")
      } else if (grepl("nominalization", issue$text, ignore.case = TRUE)) {
        # Fix nominalizations
        pattern <- "lead\\s+to\\s+an\\s+increase\\s+in"
        lines[line_num] <- gsub(pattern, "increase", line, ignore.case = TRUE)
        pattern <- "result\\s+in\\s+a\\s+decrease\\s+in"
        lines[line_num] <- gsub(pattern, "decrease", line, ignore.case = TRUE)
        changes_made <- c(changes_made, "Fixed nominalization")
      }
    }
  }
  
  revised_text <- paste(lines, collapse = "\n")
  
  return(list(revised_text = revised_text, changes_made = changes_made))
}


vary_sentence_beginnings <- function(text) {
  """
  Vary sentence beginnings to avoid repetitive patterns.
  
  Args:
    text: Text to revise (character vector)
    
  Returns:
    Text with varied sentence beginnings
  """
  # Simplified implementation - full version would require more sophisticated parsing
  return(text)
}


vary_sentence_lengths <- function(text) {
  """
  Vary sentence lengths to avoid uniform mid-length sentences.
  
  Args:
    text: Text to revise (character vector)
    
  Returns:
    Text with varied sentence lengths
  """
  # Simplified implementation - full version would require more sophisticated parsing
  return(text)
}


improve_paragraph_structure <- function(text) {
  """
  Improve paragraph structure by varying paragraph lengths.
  
  Args:
    text: Text to revise (character vector)
    
  Returns:
    Text with improved paragraph structure
  """
  # Simplified implementation - full version would require more sophisticated parsing
  return(text)
}


auto_revise_text <- function(text, ai_score = NULL, max_iterations = 3) {
  """
  Automatically revise text to reduce AI detection score.
  
  Args:
    text: Text to revise (character vector)
    ai_score: Current AI score (if known, numeric)
    max_iterations: Maximum number of revision iterations (integer)
  
  Returns:
    List with revised_text and revision_info
  """
  revision_info <- list(
    iterations = 0,
    changes_made = character(),
    final_score = NULL
  )
  
  current_text <- text
  
  for (iteration in seq_len(max_iterations)) {
    revision_info$iterations <- iteration
    
    # Identify issues
    issues <- identify_ai_issues(current_text)
    
    # Apply fixes
    fix_result <- apply_fixes(current_text, issues)
    revised_text <- fix_result$revised_text
    revision_info$changes_made <- c(revision_info$changes_made, fix_result$changes_made)
    
    # Apply additional improvements
    revised_text <- vary_sentence_beginnings(revised_text)
    revised_text <- vary_sentence_lengths(revised_text)
    revised_text <- improve_paragraph_structure(revised_text)
    
    # Check if we made progress
    if (revised_text == current_text) {
      # No more changes possible
      break
    }
    
    current_text <- revised_text
  }
  
  revision_info$final_text <- current_text
  
  return(list(revised_text = current_text, revision_info = revision_info))
}


# Example usage (when run directly)
if (!interactive()) {
  sample_text <- "
  This article will discuss the intricate complexities of the research.
  It is important to note that we delved into the realm of comprehensive analysis.
  The findings aren't just significant, they're pivotal to understanding the landscape.
  The comprehensive study showcases the multifaceted nature of the problem.
  "
  
  cat("Original text:\n")
  cat(sample_text)
  cat("\n", rep("=", 60), "\n", sep = "")
  
  result <- auto_revise_text(sample_text, ai_score = 0.75)
  
  cat("\nRevised text:\n")
  cat(result$revised_text)
  cat("\n", rep("=", 60), "\n", sep = "")
  cat("\nRevision info:\n")
  cat(sprintf("  Iterations: %d\n", result$revision_info$iterations))
  cat(sprintf("  Changes made: %d\n", length(result$revision_info$changes_made)))
  for (change in result$revision_info$changes_made) {
    cat(sprintf("    - %s\n", change))
  }
}
