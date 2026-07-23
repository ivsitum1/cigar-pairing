# Integrated Writing Workflow with AI Score Check (R)
#
# This module implements the complete writing workflow:
# Write → Real-time Check → AI Score Check → Auto-Revise → Re-check
# Automatically iterates until AI score falls below 20% or max iterations reached.
#
# Usage:
#   source("behavior_rules/tools/writing/writing_workflow.R")
#   result <- write_with_ai_check(
#     initial_text = "Your text here",
#     target_ai_score = 0.20,
#     max_iterations = 5
#   )

# Load required modules
source(file.path(dirname(sys.frame(1)$ofile), "writing_realtime_check.R"))
source(file.path(dirname(sys.frame(1)$ofile), "writing_auto_revise.R"))
source(file.path(dirname(sys.frame(1)$ofile), "writing_feedback.R"))

# Load check_ai_score_fast if available (now in parent tools directory)
tools_dir <- dirname(dirname(sys.frame(1)$ofile))
if (file.exists(file.path(tools_dir, "check_ai_score_fast.R"))) {
  source(file.path(tools_dir, "check_ai_score_fast.R"))
} else {
  # Fallback function
  check_ai_score_fast <- function(text, fast_mode = TRUE) {
    return(list(score = 0.0, status = "error", message = "check_ai_score_fast not available"))
  }
}


write_with_ai_check <- function(initial_text, target_ai_score = 0.20, max_iterations = 5, 
                                fast_mode = TRUE, show_progress = TRUE) {
  """
  Complete writing workflow with automatic AI score checking and revision.
  
  Args:
    initial_text: Initial text to process (character vector)
    target_ai_score: Target AI score threshold (default: 0.20 = 20%, numeric)
    max_iterations: Maximum number of revision iterations (integer)
    fast_mode: Use fast AI detection methods (logical)
    show_progress: Display progress messages (logical)
  
  Returns:
    List with:
    - final_text: Revised text
    - final_score: Final AI score
    - iterations: Number of iterations performed
    - revision_history: List of revisions with scores
    - success: Whether target score was achieved
  """
  current_text <- initial_text
  revision_history <- list()
  
  if (show_progress) {
    cat(rep("=", 60), "\n", sep = "")
    cat("INTEGRATED WRITING WORKFLOW\n")
    cat(rep("=", 60), "\n", sep = "")
    cat(sprintf("Target AI Score: < %.0f%%\n", target_ai_score * 100))
    cat(sprintf("Max Iterations: %d\n", max_iterations))
    cat("\n")
  }
  
  # Step 1: Real-time check for banned words and AI phrases
  if (show_progress) {
    cat("Step 1: Real-time banned words and AI phrase check...\n")
  }
  
  realtime_issues <- check_all_issues(current_text)
  has_issues <- length(realtime_issues$banned_words) > 0 || 
                length(realtime_issues$ai_phrases) > 0 || 
                length(realtime_issues$sentence_patterns) > 0
  
  if (has_issues) {
    if (show_progress) {
      cat("⚠️  Issues detected during real-time check:\n")
      all_issues <- c(realtime_issues$banned_words, 
                     realtime_issues$ai_phrases, 
                     realtime_issues$sentence_patterns)
      cat(format_issues_for_display(all_issues), "\n")
    }
  } else {
    if (show_progress) {
      cat("✓ No issues detected in real-time check.\n")
    }
  }
  cat("\n")
  
  # Step 2: Initial AI score check
  if (show_progress) {
    cat("Step 2: Initial AI score check...\n")
  }
  
  ai_result <- check_ai_score_fast(current_text, fast_mode = fast_mode)
  current_score <- if (!is.null(ai_result$score)) ai_result$score else 1.0
  
  revision_history[[length(revision_history) + 1]] <- list(
    iteration = 0,
    score = current_score,
    text = current_text,
    changes = "Initial text"
  )
  
  if (show_progress) {
    cat(sprintf("Initial AI Score: %.1f%%\n", current_score * 100))
    cat("\n")
  }
  
  # Check if already below target
  if (current_score < target_ai_score) {
    if (show_progress) {
      cat(sprintf("✓ Target achieved! AI score (%.1f%%) is below threshold (%.0f%%)\n", 
                  current_score * 100, target_ai_score * 100))
    }
    return(list(
      final_text = current_text,
      final_score = current_score,
      iterations = 0,
      revision_history = revision_history,
      success = TRUE
    ))
  }
  
  # Step 3: Iterative revision
  if (show_progress) {
    cat("Step 3: Starting iterative revision...\n")
    cat("\n")
  }
  
  for (iteration in seq_len(max_iterations)) {
    if (show_progress) {
      cat(sprintf("Iteration %d/%d:\n", iteration, max_iterations))
      cat(sprintf("  Current AI Score: %.1f%%\n", current_score * 100))
    }
    
    # Identify issues
    issues <- identify_ai_issues(current_text)
    
    # Auto-revise
    revise_result <- auto_revise_text(
      current_text,
      ai_score = current_score,
      max_iterations = 1  # One iteration per cycle
    )
    revised_text <- revise_result$revised_text
    
    if (revised_text == current_text) {
      if (show_progress) {
        cat("  No more changes possible. Stopping.\n")
      }
      break
    }
    
    # Re-check AI score
    ai_result <- check_ai_score_fast(revised_text, fast_mode = fast_mode)
    new_score <- if (!is.null(ai_result$score)) ai_result$score else current_score
    
    revision_history[[length(revision_history) + 1]] <- list(
      iteration = iteration,
      score = new_score,
      text = revised_text,
      changes = revise_result$revision_info$changes_made
    )
    
    if (show_progress) {
      cat(sprintf("  New AI Score: %.1f%%\n", new_score * 100))
      if (new_score < current_score) {
        improvement <- current_score - new_score
        cat(sprintf("  ✓ Improved by %.1f%%\n", improvement * 100))
      } else if (new_score > current_score) {
        degradation <- new_score - current_score
        cat(sprintf("  ⚠️  Worsened by %.1f%%\n", degradation * 100))
      } else {
        cat("  → No change\n")
      }
      cat("\n")
    }
    
    current_text <- revised_text
    current_score <- new_score
    
    # Check if target achieved
    if (current_score < target_ai_score) {
      if (show_progress) {
        cat(sprintf("✓ Target achieved! AI score (%.1f%%) is below threshold (%.0f%%)\n", 
                    current_score * 100, target_ai_score * 100))
      }
      return(list(
        final_text = current_text,
        final_score = current_score,
        iterations = iteration,
        revision_history = revision_history,
        success = TRUE
      ))
    }
  }
  
  # Max iterations reached
  if (show_progress) {
    cat(sprintf("⚠️  Max iterations reached. Final AI Score: %.1f%%\n", current_score * 100))
    if (current_score >= target_ai_score) {
      cat(sprintf("   Target (%.0f%%) not achieved, but improvements were made.\n", 
                  target_ai_score * 100))
    }
  }
  
  return(list(
    final_text = current_text,
    final_score = current_score,
    iterations = max_iterations,
    revision_history = revision_history,
    success = current_score < target_ai_score
  ))
}


display_workflow_summary <- function(result) {
  """
  Display a summary of the workflow results.
  
  Args:
    result: Result list from write_with_ai_check()
  """
  cat(rep("=", 60), "\n", sep = "")
  cat("WORKFLOW SUMMARY\n")
  cat(rep("=", 60), "\n", sep = "")
  cat(sprintf("Final AI Score: %.1f%%\n", result$final_score * 100))
  cat(sprintf("Iterations: %d\n", result$iterations))
  cat(sprintf("Success: %s\n", if (result$success) "✓ Yes" else "✗ No"))
  cat("\n")
  
  if (length(result$revision_history) > 0) {
    cat("Revision History:\n")
    for (entry in result$revision_history) {
      cat(sprintf("  Iteration %d: %.1f%%\n", entry$iteration, entry$score * 100))
      if (!is.null(entry$changes) && length(entry$changes) > 0) {
        cat(sprintf("    Changes: %d modification(s)\n", length(entry$changes)))
      }
    }
  }
  cat(rep("=", 60), "\n", sep = "")
}


# Example usage (when run directly)
if (!interactive()) {
  sample_text <- "
  This article will discuss the intricate complexities of the research.
  It is important to note that we delved into the realm of comprehensive analysis.
  The findings aren't just significant, they're pivotal to understanding the landscape.
  The comprehensive study showcases the multifaceted nature of the problem.
  "
  
  result <- write_with_ai_check(
    initial_text = sample_text,
    target_ai_score = 0.20,
    max_iterations = 5,
    fast_mode = TRUE,
    show_progress = TRUE
  )
  
  cat("\n")
  display_workflow_summary(result)
}
