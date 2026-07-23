# ============================================================================
# agent_activation_middleware.R
# Middleware for automatic agent activation based on prompt and context
# 
# Usage:
#   source("behavior_rules/tools/agents/agent_activation_middleware.R")
#   result <- activate_agent_for_prompt("analiziraj podatke", context_files = c("data.csv"))
# ============================================================================

# Load agent auto-detection
script_dir <- dirname(sys.frame(1)$ofile)
if (file.exists(file.path(script_dir, "agent_auto_detection.R"))) {
  source(file.path(script_dir, "agent_auto_detection.R"))
} else {
  stop("agent_auto_detection.R not found. Please ensure it exists in behavior_rules/tools/agents/ directory.")
}

activate_agent_for_prompt <- function(prompt, context_files = NULL, open_files = NULL, 
                                      auto_confirm = FALSE, enable_writing_workflow = TRUE) {
  # Main function for activating agent based on prompt and context
  #
  # Args:
  #   prompt: User's prompt/query
  #   context_files: Vector of file paths in context
  #   open_files: Vector of open file paths
  #   auto_confirm: Logical, if TRUE auto-activates if confidence >= 0.7
  #   enable_writing_workflow: Logical, if TRUE enables integrated writing workflow for Academic Writing Specialist
  #
  # Returns:
  #   List with activation results
  
  # Detect agent
  detection_result <- detect_agent_from_prompt(prompt, context_files, open_files)
  
  # Determine if activation should proceed
  should_activate <- detection_result$confidence >= 0.7 || auto_confirm
  
  # Load agent rules if activation should proceed
  agent_rules <- NULL
  if (should_activate) {
    agent_rules <- load_agent_rules(detection_result$agent)
    
    # Special handling for Academic Writing Specialist: enable writing workflow
    if (detection_result$agent == "academic_writing_specialist" && enable_writing_workflow) {
      # Writing workflow will be automatically used when agent writes text
      # This is handled by the agent's rules and the write_with_ai_check function
      agent_rules$writing_workflow_enabled <- TRUE
    }
  }
  
  # Confirm activation if confidence is low
  needs_confirmation <- detection_result$confidence < 0.7 && !auto_confirm
  
  return(list(
    agent = detection_result$agent,
    confidence = detection_result$confidence,
    should_activate = should_activate,
    needs_confirmation = needs_confirmation,
    agent_rules = agent_rules,
    reasoning = detection_result$reasoning,
    triggers = detection_result$triggers
  ))
}

scan_context_for_triggers <- function(context_files = NULL, open_files = NULL, 
                                     prompt = NULL) {
  # Scans context (files and prompt) for agent activation triggers
  #
  # Args:
  #   context_files: Vector of file paths in context
  #   open_files: Vector of open file paths
  #   prompt: User prompt (optional)
  #
  # Returns:
  #   List with detected triggers and recommended agent
  
  all_files <- c(context_files, open_files)
  
  # File type triggers
  file_triggers <- list()
  if (!is.null(all_files)) {
    for (file in all_files) {
      file_lower <- tolower(file)
      
      # R files → Statistical Analysis Expert
      if (grepl("\\.r$|\\.rmd$", file_lower)) {
        file_triggers$statistical_analysis_expert <- 
          c(file_triggers$statistical_analysis_expert, file)
      }
      
      # Manuscript files → Academic Writing Specialist
      if (grepl("manuscript|paper|draft|\\.docx$|\\.doc$", file_lower)) {
        file_triggers$academic_writing_specialist <- 
          c(file_triggers$academic_writing_specialist, file)
      }
      
      # Data files → Statistical Analysis Expert or Medical Data Science Coder
      if (grepl("\\.csv$|\\.xlsx$|\\.xls$|\\.sav$", file_lower)) {
        file_triggers$statistical_analysis_expert <- 
          c(file_triggers$statistical_analysis_expert, file)
        file_triggers$medical_data_science_coder <- 
          c(file_triggers$medical_data_science_coder, file)
      }
      
      # Protocol files → Clinical Research Methodologist
      if (grepl("protocol|sap|design", file_lower)) {
        file_triggers$clinical_research_methodologist <- 
          c(file_triggers$clinical_research_methodologist, file)
      }
    }
  }
  
  # Prompt triggers (if provided)
  prompt_triggers <- list()
  if (!is.null(prompt)) {
    detection_result <- detect_agent_from_prompt(prompt, context_files, open_files)
    prompt_triggers[[detection_result$agent]] <- detection_result
  }
  
  # Combine triggers
  all_triggers <- unique(c(names(file_triggers), names(prompt_triggers)))
  
  # Determine recommended agent (most triggers)
  if (length(all_triggers) > 0) {
    trigger_counts <- table(c(names(file_triggers), names(prompt_triggers)))
    recommended_agent <- names(trigger_counts)[which.max(trigger_counts)]
  } else {
    recommended_agent <- "statistical_analysis_expert"  # Default
  }
  
  return(list(
    file_triggers = file_triggers,
    prompt_triggers = prompt_triggers,
    recommended_agent = recommended_agent,
    all_triggers = all_triggers
  ))
}

load_agent_rules <- function(agent_name) {
  # Loads rules for specific agent
  #
  # Args:
  #   agent_name: Name of agent (e.g., "statistical_analysis_expert")
  #
  # Returns:
  #   List with agent rules and configuration
  
  # Map agent names to rule files
  agent_rule_files <- list(
    statistical_analysis_expert = "behavior_rules/agents/07_statistical_analysis_expert.md",
    academic_writing_specialist = "behavior_rules/agents/08_academic_writing_specialist.md",
    clinical_decision_support = "behavior_rules/agents/01_clinical_decision_support.md",
    clinical_research_methodologist = "behavior_rules/agents/02_clinical_research_methodologist.md",
    medical_data_science_coder = "behavior_rules/agents/04_medical_data_science_coder.md",
    code_quality_assurance = "behavior_rules/agents/03_code_quality_assurance.md",
    prompt_engineering_specialist = "behavior_rules/agents/05_prompt_engineering_specialist.md",
    rules_roles_maintainer = "behavior_rules/agents/06_rules_roles_maintainer.md"
  )
  
  rule_file <- agent_rule_files[[agent_name]]
  
  if (is.null(rule_file)) {
    return(list(
      agent = agent_name,
      rules_loaded = FALSE,
      message = "Agent rule file not found"
    ))
  }
  
  # Check if rule file exists
  if (!file.exists(rule_file)) {
    # Try parent directory
    parent_rule <- file.path("..", rule_file)
    if (file.exists(parent_rule)) {
      rule_file <- parent_rule
    } else {
      return(list(
        agent = agent_name,
        rules_loaded = FALSE,
        message = paste0("Rule file not found: ", rule_file)
      ))
    }
  }
  
  # Load rules (simplified - in production would parse markdown)
  rules_content <- readLines(rule_file, warn = FALSE)
  
  # Special handling for Academic Writing Specialist: load writing workflow
  if (agent_name == "academic_writing_specialist") {
    # Load writing workflow modules
    workflow_file <- "behavior_rules/tools/writing/writing_workflow.R"
    if (file.exists(workflow_file)) {
      source(workflow_file)
    }
  }
  
  return(list(
    agent = agent_name,
    rules_loaded = TRUE,
    rule_file = rule_file,
    rules_content = rules_content,
    rules_length = length(rules_content)
  ))
}

confirm_agent_activation <- function(activation_result, user_response = NULL) {
  # Confirms agent activation with user (if confidence is low)
  #
  # Args:
  #   activation_result: Result from activate_agent_for_prompt()
  #   user_response: User's response ("yes", "no", or NULL for prompt)
  #
  # Returns:
  #   List with confirmation result
  
  if (!activation_result$needs_confirmation) {
    return(list(
      confirmed = TRUE,
      message = "High confidence activation, no confirmation needed"
    ))
  }
  
  # If user response provided, use it
  if (!is.null(user_response)) {
    confirmed <- tolower(user_response) %in% c("yes", "y", "da", "ok", "confirm")
    return(list(
      confirmed = confirmed,
      message = if (confirmed) {
        paste0("Agent ", activation_result$agent, " activated")
      } else {
        "Activation cancelled by user"
      }
    ))
  }
  
  # Otherwise, return prompt for user
  agent_display <- format_agent_name(activation_result$agent)
  
  return(list(
    confirmed = FALSE,
    needs_user_input = TRUE,
    prompt = paste0(
      "Detected agent: ", agent_display, 
      " (confidence: ", round(activation_result$confidence * 100), "%)\n",
      "Reasoning: ", activation_result$reasoning, "\n",
      "Activate this agent? (yes/no)"
    )
  ))
}

# Helper function to format agent name (from agent_auto_detection.R)
if (!exists("format_agent_name")) {
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
}

# Example usage
if (FALSE) {
  # Activate agent for prompt
  result <- activate_agent_for_prompt("analiziraj podatke i napravi regresijski model")
  
  # Scan context
  triggers <- scan_context_for_triggers(
    context_files = c("data.csv", "analysis.R"),
    prompt = "analiziraj podatke"
  )
  
  # Load agent rules
  rules <- load_agent_rules("statistical_analysis_expert")
  
  # Confirm activation
  if (result$needs_confirmation) {
    confirmation <- confirm_agent_activation(result, user_response = "yes")
  }
}
