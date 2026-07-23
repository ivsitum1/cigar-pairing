# Real-Time Banned Words and AI Phrase Checker
#
# This module provides real-time checking of banned words, AI phrases, and sentence patterns
# during text writing. It identifies problematic content and provides suggestions for replacements.
#
# Usage:
#   source("behavior_rules/tools/writing/writing_realtime_check.R")
#   issues <- check_banned_words_realtime(text)
#   ai_phrases <- check_ai_phrases(text)
#   patterns <- analyze_sentence_patterns(text)

# Banned words and their replacements
BANNED_WORDS <- list(
  "delve" = c("explore", "examine", "investigate"),
  "delves" = c("explores", "examines", "investigates"),
  "delving" = c("exploring", "examining", "investigating"),
  "intricate" = c("complex", "detailed", "sophisticated"),
  "intricacies" = c("complexities", "details"),
  "comprehensive" = c("complete", "thorough", "extensive"),
  "pivotal" = c("important", "key", "critical"),
  "crucial" = c("important", "essential", "vital"),
  "tapestry" = c("combination", "mix", "blend"),
  "realm" = c("area", "field", "domain"),
  "landscape" = c("situation", "context", "environment"),
  "multifaceted" = c("complex", "varied", "diverse"),
  "nuanced" = c("subtle", "refined", "sophisticated"),
  "showcasing" = c("showing", "demonstrating", "displaying"),
  "underscores" = c("highlights", "emphasizes", "shows"),
  "vibrant" = c("active", "dynamic", "energetic"),
  "testament" = c("evidence", "proof", "demonstration"),
  "revolutionize" = c("transform", "change", "improve"),
  "unlock" = c("reveal", "discover", "enable")
)

# AI phrases and their replacements
AI_PHRASES <- list(
  "it is important to note that" = "Remove or state directly",
  "in the realm of" = "in",
  "navigating the complexities" = "addressing",
  "at its core" = "essentially or fundamentally",
  "to put it simply" = "simply or remove",
  "key takeaway" = "important point or main finding",
  "a significant aspect is" = "an important point is or remove",
  "at the end of the day" = "ultimately or finally",
  "it is worth mentioning" = "note that or remove",
  "in this day and age" = "currently or now",
  "it serves as" = "it is",
  "it stands as" = "it is",
  "it features" = "it has or it includes"
)

# Banned sentence patterns
BANNED_PATTERNS <- list(
  list(
    pattern = "(.+?)\\s+isn't\\s+just\\s+(.+?),\\s+it's\\s+(.+?)",
    description = "Negation reframe pattern",
    suggestion = "Split into separate statements"
  ),
  list(
    pattern = "this\\s+article\\s+will\\s+discuss",
    description = "Generic intro pattern",
    suggestion = "State directly without meta-commentary"
  ),
  list(
    pattern = "in\\s+conclusion,\\s+this\\s+article\\s+shows",
    description = "Generic sign-off pattern",
    suggestion = "State conclusion directly"
  )
)


check_banned_words_realtime <- function(text) {
  """
  Check for banned words in the text and provide suggestions.
  
  Args:
    text: The text to check (character vector)
    
  Returns:
    List of issues with locations and suggestions
  """
  issues <- list()
  lines <- strsplit(text, "\n")[[1]]
  
  for (line_num in seq_along(lines)) {
    line <- tolower(lines[line_num])
    words <- strsplit(line, "\\W+")[[1]]
    words <- words[words != ""]  # Remove empty strings
    
    for (word_pos in seq_along(words)) {
      word <- words[word_pos]
      if (word %in% names(BANNED_WORDS)) {
        suggestions <- paste(BANNED_WORDS[[word]], collapse = ", ")
        issues[[length(issues) + 1]] <- list(
          issue_type = "banned_word",
          location = c(line_num, word_pos),
          text = word,
          suggestion = paste("Replace with:", suggestions),
          severity = "medium"
        )
      }
    }
  }
  
  return(issues)
}


check_ai_phrases <- function(text) {
  """
  Check for AI phrases in the text.
  
  Args:
    text: The text to check (character vector)
    
  Returns:
    List of issues with locations and suggestions
  """
  issues <- list()
  lines <- strsplit(text, "\n")[[1]]
  
  for (line_num in seq_along(lines)) {
    line_lower <- tolower(lines[line_num])
    
    for (phrase in names(AI_PHRASES)) {
      if (grepl(phrase, line_lower, ignore.case = TRUE)) {
        pos <- regexpr(phrase, line_lower, ignore.case = TRUE)[1]
        issues[[length(issues) + 1]] <- list(
          issue_type = "ai_phrase",
          location = c(line_num, pos),
          text = phrase,
          suggestion = AI_PHRASES[[phrase]],
          severity = "high"
        )
      }
    }
  }
  
  return(issues)
}


analyze_sentence_patterns <- function(text) {
  """
  Analyze sentence patterns for AI-favored structures.
  
  Args:
    text: The text to analyze (character vector)
    
  Returns:
    List of issues with detected patterns
  """
  issues <- list()
  lines <- strsplit(text, "\n")[[1]]
  
  for (line_num in seq_along(lines)) {
    line_lower <- tolower(lines[line_num])
    
    # Check for banned patterns
    for (pattern_info in BANNED_PATTERNS) {
      if (grepl(pattern_info$pattern, line_lower, ignore.case = TRUE)) {
        pos <- regexpr(pattern_info$pattern, line_lower, ignore.case = TRUE)[1]
        issues[[length(issues) + 1]] <- list(
          issue_type = "sentence_pattern",
          location = c(line_num, pos),
          text = pattern_info$description,
          suggestion = pattern_info$suggestion,
          severity = "high"
        )
      }
    }
    
    # Check for rule of three (three-item lists)
    three_item_pattern <- "(\\w+),\\s+(\\w+),\\s+and\\s+(\\w+)"
    matches <- gregexpr(three_item_pattern, line_lower, ignore.case = TRUE)[[1]]
    if (length(matches) > 2 && matches[1] != -1) {
      issues[[length(issues) + 1]] <- list(
        issue_type = "repetitive_structure",
        location = c(line_num, 0),
        text = "Multiple three-item lists",
        suggestion = "Vary list lengths (2, 4, 5 items when appropriate)",
        severity = "low"
      )
    }
    
    # Check for excessive participial clauses
    participial_pattern <- "(\\w+ing\\s+\\w+,\\s+){2,}"
    if (grepl(participial_pattern, line_lower)) {
      issues[[length(issues) + 1]] <- list(
        issue_type = "sentence_pattern",
        location = c(line_num, 0),
        text = "Excessive participial clauses",
        suggestion = "Split into simpler sentences or use relative clauses",
        severity = "medium"
      )
    }
    
    # Check for nominalizations
    nominalization_pattern <- "lead\\s+to\\s+an\\s+increase\\s+in|result\\s+in\\s+a\\s+decrease\\s+in"
    if (grepl(nominalization_pattern, line_lower)) {
      issues[[length(issues) + 1]] <- list(
        issue_type = "sentence_pattern",
        location = c(line_num, 0),
        text = "Nominalization detected",
        suggestion = "Use verb forms instead (e.g., 'increase' instead of 'lead to an increase in')",
        severity = "medium"
      )
    }
  }
  
  return(issues)
}


suggest_replacements <- function(word) {
  """
  Get replacement suggestions for a banned word.
  
  Args:
    word: The word to find replacements for
    
  Returns:
    Character vector of suggested replacements
  """
  word_lower <- tolower(word)
  if (word_lower %in% names(BANNED_WORDS)) {
    return(BANNED_WORDS[[word_lower]])
  }
  return(character(0))
}


check_all_issues <- function(text) {
  """
  Check all types of issues in the text.
  
  Args:
    text: The text to check (character vector)
    
  Returns:
    List with issue types as keys and lists of issues as values
  """
  return(list(
    banned_words = check_banned_words_realtime(text),
    ai_phrases = check_ai_phrases(text),
    sentence_patterns = analyze_sentence_patterns(text)
  ))
}


format_issues_for_display <- function(issues) {
  """
  Format issues for display to the user.
  
  Args:
    issues: List of issue objects
    
  Returns:
    Character vector with formatted warnings and suggestions
  """
  if (length(issues) == 0) {
    return("No issues detected.")
  }
  
  output <- character()
  for (issue in issues) {
    line_num <- issue$location[1]
    pos <- issue$location[2]
    issue_type_formatted <- gsub("_", " ", issue$issue_type)
    issue_type_formatted <- paste(toupper(substring(issue_type_formatted, 1, 1)), 
                                  substring(issue_type_formatted, 2), sep = "")
    
    output <- c(output, 
                paste0("⚠️ WARNING: ", issue_type_formatted),
                paste0("  Location: Line ", line_num, ", position ", pos),
                paste0("  Text: \"", issue$text, "\""),
                paste0("  Suggestion: ", issue$suggestion),
                paste0("  Severity: ", issue$severity),
                "")
  }
  
  return(paste(output, collapse = "\n"))
}


# Example usage (when run directly)
if (!interactive()) {
  sample_text <- "
  This article will discuss the intricate complexities of the research.
  It is important to note that we delved into the realm of comprehensive analysis.
  The findings aren't just significant, they're pivotal to understanding the landscape.
  "
  
  all_issues <- check_all_issues(sample_text)
  for (issue_type in names(all_issues)) {
    issues <- all_issues[[issue_type]]
    if (length(issues) > 0) {
      cat("\n", toupper(issue_type), ":\n", sep = "")
      cat(format_issues_for_display(issues), "\n")
    }
  }
}
