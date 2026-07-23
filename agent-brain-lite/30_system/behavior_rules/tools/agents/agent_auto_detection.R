# ============================================================================
# agent_auto_detection.R
# Automatic agent detection from user prompts and context
# 
# Usage:
#   source("behavior_rules/tools/agents/agent_auto_detection.R")
#   result <- detect_agent_from_prompt("analiziraj podatke", context_files = c("data.csv"))
# ============================================================================

detect_agent_from_prompt <- function(prompt, context_files = NULL, open_files = NULL) {
  # Detects the most appropriate agent based on user prompt and context.
  #
  # Args:
  #   prompt: User's prompt/query (character)
  #   context_files: Vector of file paths in context (optional)
  #   open_files: Vector of open file paths (optional)
  #
  # Returns:
  #   List with:
  #     - agent: Recommended agent name
  #     - confidence: Confidence score (0-1)
  #     - triggers: Vector of matched triggers
  #     - reasoning: Brief explanation
  
  prompt_lower <- tolower(prompt)
  all_files <- c(context_files, open_files)
  
  # Agent trigger definitions (from 15_agent_roles.md)
  agent_triggers <- list(
    statistical_analysis_expert = list(
      keywords = c("analiz", "model", "regres", "test", "distribuc", "p-vrijednost", 
                   "p-value", "ci", "anova", "bayes", "statist", "hipotez", "efekt",
                   "meta-analiz", "meta-analysis", "survival", "cox", "kaplan",
                   "power", "sample size", "imputac", "missing data", "bootstrap",
                   "flexplot", "eda", "exploratorn"),
      file_patterns = c("\\.r$", "\\.rmd$", "\\.rdata$", "\\.rds$"),
      file_keywords = c("analysis", "statistic", "model", "regression")
    ),
    academic_writing_specialist = list(
      keywords = c("piši", "write", "draft", "manuscript", "sekcija", "section",
                   "abstract", "discussion", "introduction", "methods", "results",
                   "revise", "improve", "rewrite", "natural", "human-like",
                   "prisma", "grade", "reporting", "citation", "reference"),
      file_patterns = c("manuscript", "paper", "draft", "\\.docx$", "\\.doc$"),
      file_keywords = c("manuscript", "paper", "draft", "abstract", "introduction")
    ),
    clinical_decision_support = list(
      keywords = c("pacijent", "patient", "kliničk", "clinical", "diagnos",
                   "treatment", "therapy", "drug", "disease", "symptom",
                   "anesthesia", "intensive care", "icu", "guideline", "protocol",
                   "dosing", "risk", "assessment", "sbar", "differential"),
      file_patterns = c("protocol", "guideline", "clinical"),
      file_keywords = c("clinical", "patient", "protocol", "guideline", "icu")
    ),
    clinical_research_methodologist = list(
      keywords = c("dizajn", "design", "protokol", "protocol", "metodolog",
                   "methodology", "sample size", "randomiz", "randomization",
                   "rct", "cohort", "case-control", "consort", "strobe",
                   "power", "allocation", "blinding", "ethics"),
      file_patterns = c("protocol", "sap", "design"),
      file_keywords = c("protocol", "design", "methodology", "sap", "consort")
    ),
    medical_data_science_coder = list(
      keywords = c("code", "script", "function", "package", "install",
                   "programming", "implement", "create script", "write code",
                   "r script", "python", "data manipulation", "visualization",
                   "performance", "optimization", "debug", "error"),
      file_patterns = c("\\.r$", "\\.py$", "\\.rmd$"),
      file_keywords = c("script", "code", "function", "utils")
    ),
    code_quality_assurance = list(
      keywords = c("provjeri", "check", "review", "verify", "kvaliteta", "quality",
                   "test", "validate", "error", "bug", "fix", "correct",
                   "reproducibility", "best practice", "standard"),
      file_patterns = c("\\.r$", "\\.py$", "\\.rmd$"),
      file_keywords = c("test", "check", "validate", "quality")
    ),
    prompt_engineering_specialist = list(
      keywords = c("prompt", "optimize", "improve", "efficiency", "token",
                   "context", "cursor", "ai interaction", "template"),
      file_patterns = NULL,
      file_keywords = NULL
    ),
    rules_roles_maintainer = list(
      keywords = c("rule", "role", "system", "consistency", "conflict",
                   "maintain", "update", "documentation", "version"),
      file_patterns = c("behavior_rules", "agent", "rule"),
      file_keywords = c("rule", "role", "system", "maintain")
    )
  )
  
  # Score each agent
  agent_scores <- list()
  matched_triggers <- list()
  
  for (agent_name in names(agent_triggers)) {
    triggers <- agent_triggers[[agent_name]]
    score <- 0
    matched <- c()
    
    # Check keywords in prompt
    keyword_matches <- sum(sapply(triggers$keywords, function(kw) {
      grepl(kw, prompt_lower, fixed = TRUE) || grepl(kw, prompt_lower)
    }))
    if (keyword_matches > 0) {
      score <- score + keyword_matches * 0.3
      matched <- c(matched, paste0("keywords:", keyword_matches))
    }
    
    # Check file patterns
    if (!is.null(all_files) && length(all_files) > 0) {
      file_matches <- sum(sapply(all_files, function(f) {
        any(sapply(triggers$file_patterns, function(pattern) {
          grepl(pattern, tolower(f), ignore.case = TRUE)
        }))
      }))
      if (file_matches > 0) {
        score <- score + file_matches * 0.4
        matched <- c(matched, paste0("file_patterns:", file_matches))
      }
      
      # Check file keywords
      file_keyword_matches <- sum(sapply(all_files, function(f) {
        any(sapply(triggers$file_keywords, function(kw) {
          grepl(kw, tolower(f), ignore.case = TRUE)
        }))
      }))
      if (file_keyword_matches > 0) {
        score <- score + file_keyword_matches * 0.3
        matched <- c(matched, paste0("file_keywords:", file_keyword_matches))
      }
    }
    
    agent_scores[[agent_name]] <- score
    matched_triggers[[agent_name]] <- matched
  }
  
  # Find best agent
  best_agent <- names(agent_scores)[which.max(unlist(agent_scores))]
  best_score <- max(unlist(agent_scores))
  
  # Normalize confidence (0-1 scale)
  # If score > 1, cap at 1; otherwise use score as confidence
  confidence <- min(1.0, best_score)
  
  # If confidence is very low, default to general agent
  if (confidence < 0.2) {
    best_agent <- "statistical_analysis_expert"  # Default fallback
    confidence <- 0.2
  }
  
  # Generate reasoning
  reasoning <- paste0(
    "Detected agent: ", best_agent, 
    " (confidence: ", round(confidence * 100), "%)",
    if (length(matched_triggers[[best_agent]]) > 0) {
      paste0(" | Triggers: ", paste(matched_triggers[[best_agent]], collapse = ", "))
    } else {
      " | No specific triggers matched, using default"
    }
  )
  
  return(list(
    agent = best_agent,
    confidence = confidence,
    triggers = matched_triggers[[best_agent]],
    reasoning = reasoning,
    all_scores = agent_scores
  ))
}

# Helper function to format agent name for display
format_agent_name <- function(agent_name) {
  agent_display_names <- list(
    statistical_analysis_expert = "Statistical Analysis Expert",
    academic_writing_specialist = "Academic Writing Specialist",
    clinical_decision_support = "Clinical Decision Support Agent",
    clinical_research_methodologist = "Clinical Research Methodologist",
    medical_data_science_coder = "Medical Data Science Coder",
    code_quality_assurance = "Code Quality Assurance Agent",
    prompt_engineering_specialist = "Prompt Engineering Specialist",
    rules_roles_maintainer = "Rules & Roles System Maintainer"
  )
  
  if (agent_name %in% names(agent_display_names)) {
    return(agent_display_names[[agent_name]])
  }
  return(agent_name)
}

# Example usage
if (FALSE) {
  # Test cases
  detect_agent_from_prompt("analiziraj podatke i napravi regresijski model")
  detect_agent_from_prompt("piši introduction sekciju za manuscript")
  detect_agent_from_prompt("provjeri kvalitetu koda u analysis.R")
  detect_agent_from_prompt("kako dizajnirati RCT protokol?")
}
