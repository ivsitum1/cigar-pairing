#!/usr/bin/env python3
"""
Real-Time Banned Words and AI Phrase Checker

This module provides real-time checking of banned words, AI phrases, and sentence patterns
during text writing. It identifies problematic content and provides suggestions for replacements.

Usage:
    from writing_realtime_check import check_banned_words_realtime, check_ai_phrases, analyze_sentence_patterns
    
    issues = check_banned_words_realtime(text)
    ai_phrases = check_ai_phrases(text)
    patterns = analyze_sentence_patterns(text)
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class IssueType(Enum):
    """Types of issues that can be detected."""
    BANNED_WORD = "banned_word"
    AI_PHRASE = "ai_phrase"
    SENTENCE_PATTERN = "sentence_pattern"
    REPETITIVE_STRUCTURE = "repetitive_structure"
    STYLE_RULE = "style_rule"
    PASSIVE_VOICE = "passive_voice"
    WEAK_VERB = "weak_verb"
    NOMINALIZATION = "nominalization"
    REDUNDANT_PHRASE = "redundant_phrase"
    ADVERB_ISSUE = "adverb_issue"
    GRAMMAR_ISSUE = "grammar_issue"
    LATEX_ISSUE = "latex_issue"
    OXFORD_COMMA = "oxford_comma"
    ARTICLE_ISSUE = "article_issue"


@dataclass
class Issue:
    """Represents a detected issue in the text."""
    issue_type: IssueType
    location: Tuple[int, int]  # (line_number, word_position)
    text: str
    suggestion: str
    severity: str  # "low", "medium", "high"


# Banned words and their replacements
BANNED_WORDS = {
    "delve": ["explore", "examine", "investigate"],
    "delves": ["explores", "examines", "investigates"],
    "delving": ["exploring", "examining", "investigating"],
    "intricate": ["complex", "detailed", "sophisticated"],
    "intricacies": ["complexities", "details"],
    "comprehensive": ["complete", "thorough", "extensive"],
    "pivotal": ["important", "key", "critical"],
    "crucial": ["important", "essential", "vital"],
    "tapestry": ["combination", "mix", "blend"],
    "realm": ["area", "field", "domain"],
    "landscape": ["situation", "context", "environment"],
    "multifaceted": ["complex", "varied", "diverse"],
    "nuanced": ["subtle", "refined", "sophisticated"],
    "showcasing": ["showing", "demonstrating", "displaying"],
    "underscores": ["highlights", "emphasizes", "shows"],
    "vibrant": ["active", "dynamic", "energetic"],
    "testament": ["evidence", "proof", "demonstration"],
    "revolutionize": ["transform", "change", "improve"],
    "unlock": ["reveal", "discover", "enable"],
}

# AI phrases and their replacements
AI_PHRASES = {
    r"it\s+is\s+important\s+to\s+note\s+that": "Remove or state directly",
    r"in\s+the\s+realm\s+of": "in",
    r"navigating\s+the\s+complexities": "addressing",
    r"at\s+its\s+core": "essentially or fundamentally",
    r"to\s+put\s+it\s+simply": "simply or remove",
    r"key\s+takeaway": "important point or main finding",
    r"a\s+significant\s+aspect\s+is": "an important point is or remove",
    r"at\s+the\s+end\s+of\s+the\s+day": "ultimately" or "finally",
    r"it\s+is\s+worth\s+mentioning": "note that or remove",
    r"in\s+this\s+day\s+and\s+age": "currently" or "now",
    r"it\s+serves\s+as": "it is",
    r"it\s+stands\s+as": "it is",
    r"it\s+features": "it has" or "it includes",
}

# Banned sentence patterns
BANNED_PATTERNS = [
    {
        "pattern": r"(.+?)\s+isn't\s+just\s+(.+?),\s+it's\s+(.+?)",
        "description": "Negation reframe pattern",
        "suggestion": "Split into separate statements"
    },
    {
        "pattern": r"this\s+article\s+will\s+discuss",
        "description": "Generic intro pattern",
        "suggestion": "State directly without meta-commentary"
    },
    {
        "pattern": r"in\s+conclusion,\s+this\s+article\s+shows",
        "description": "Generic sign-off pattern",
        "suggestion": "State conclusion directly"
    },
]

# Style rules from vim-angry-reviewer
# Patterns that should be avoided or improved
STYLE_PATTERNS = {
    # Hype words
    "excellent agreement": "Usually, the agreement is not so excellent. Consider replacing with 'good agreement' or better yet, quantify the agreement.",
    "excellent fit": "Often, the fit is not so excellent. Consider quantifying the fit.",
    "comprehensive review": "Consider if the review is really 'comprehensive'. More often than not it is hype.",
    "outstanding": "The word 'outstanding' might be considered hype. Consider alternatives, e.g. 'remarkable'.",
    "groundbreaking": "The word 'groundbreaking' might be considered hype. Consider alternatives, e.g. 'remarkable'.",
    "ground breaking": "The word 'groundbreaking' might be considered hype. Consider alternatives, e.g. 'remarkable'.",
    "new ": "If the word 'new' refers to results or methods, editors often dislike such claims. Consider explaining novelty differently.",
    "novel ": "If the word 'novel' refers to results or methods, editors often dislike such claims. Consider explaining novelty differently.",
    " prove ": "Phrases about 'prove' should be considered with caution. Strict proof is possible only in math. Consider replacing with 'evidence', 'demonstration', 'confirmation'.",
    " proved ": "Phrases about 'prove' should be considered with caution. Consider replacing with 'evidence', 'demonstration', 'confirmation'.",
    " proof ": "Phrases about 'proof' should be considered with caution. Consider replacing with 'evidence', 'demonstration', 'confirmation'.",
    " proves ": "Phrases about 'proves' should be considered with caution. Consider replacing with verbs like 'evidence', 'demonstrate', 'confirm'.",
    "certainly": "Consider if this sentence needs the word 'certainly'. According to The Elements of Style, it's often a mannerism.",
    " fact ": "Check if the word 'fact' is actually applied to a fact. Use only for matters capable of direct verification.",
    "highly": "The word 'highly' rarely contributes to better understanding. Consider removing it or quantifying it.",
    "greatly": "The word 'greatly' rarely contributes to better understanding. Consider removing it or quantifying it.",
    "literally": "The word 'literally' is often misused to support an exaggeration, which is hardly appropriate for scientific papers.",
    "respectively": "Consider if 'respectively' is necessary. In clear cases, you can omit it.",
    "correspondingly": "Consider if 'correspondingly' is necessary. In clear cases, you can omit it.",
    "best": "If the word 'best' serves here to qualify results or methods, it will be considered hype and should be avoided.",
    "It is known": "Phrases like 'It is known' should be avoided. Often, it is not actually known to the readers. Just state the fact and supply a reference.",
    "it is known": "Phrases like 'it is known' should be avoided. Often, it is not actually known to the readers. Just state the fact and supply a reference.",
    "are well known": "Phrases with 'are well known' are considered arrogant. Usually, it is not so well known to the reader. Consider removing it or supplying references.",
    "is well known": "Phrases with 'is well known' are considered arrogant. Usually, it is not so well known to the reader. Consider removing it or supplying references.",
    "the first time": "If 'the first time' refers to findings, try to find a better way to claim novelty because such expressions are often considered hype.",
    "the very first time": "If 'the very first time' refers to findings, try to find a better way to claim novelty because such expressions are often considered hype.",
    
    # Questionable patterns
    "attracted attention": "Attracted attention is not necessarily a good motivation for research. Consider a stronger motivation.",
    "One of the most": "Consider rewriting it without 'One of the most'. According to the Elements of Style, it is threadbare and forcible-feeble.",
    "one of the most": "Consider rewriting it without 'one of the most'. According to the Elements of Style, it is threadbare and forcible-feeble.",
    "This shows": "It might be unclear what 'This' points to if the previous phrase was complicated. Rewrite with a more specific subject.",
    "This demonstrates": "It might be unclear what 'This' points to if previous phrase was complicated. Rewrite with a more specific subject.",
    "This proves": "It might be unclear what 'This' points to if the previous phrase was complicated. Rewrite with a more specific subject.",
    "This is": "It might be unclear what 'This is' points to if the previous phrase was complicated. Rewrite with a more specific subject.",
    "This leads": "It might be unclear what 'This leads' points to if the previous phrase was complicated. Rewrite with a more specific subject.",
    "et al ": "Needs a period after 'et al'. For example 'Alferov et al. showed'.",
    
    # Zombie nouns (nominalizations)
    "made a decision": "Rewrite using the verb 'decided' instead of zombie noun 'decision'.",
    "make a decision": "Rewrite using the verb 'decide' instead of zombie noun 'decision'.",
    "performed the measurement": "Rewrite using the verb 'measured' instead of zombie noun 'measurement'.",
    "made the measurement": "Rewrite using the verb 'measured' instead of zombie noun 'measurement'.",
    "make the measurement": "Rewrite using the verb 'measure' instead of zombie noun 'measurement'.",
    "take into consideration": "Rewrite using the verb 'consider' instead of zombie noun 'consideration'.",
    "is in agreement": "Rewrite using the verb 'agrees' instead of zombie noun 'agreement'.",
    "is in good agreement": "Rewrite using the verb 'agrees' instead of zombie noun 'agreement'.",
    "are in agreement": "Rewrite using the verb 'agree' instead of zombie noun 'agreement'.",
    "are in good agreement": "Rewrite using the verb 'agree' instead of zombie noun 'agreement'.",
    "was in agreement": "Rewrite using the verb 'agreed' instead of zombie noun 'agreement'.",
    "is an indication of": "Rewrite using the verb 'indicate' instead of zombie noun 'indication'.",
    "have a tendency": "Rewrite using the verb 'tend' instead of zombie noun 'tendency'.",
    "has a tendency": "Rewrite using the verb 'tends' instead of zombie noun 'tendency'.",
    "indications of": "Rewrite using the verb 'indicate' instead of zombie noun 'indications'.",
    "indication of": "Rewrite using the verb 'indicate' instead of zombie noun 'indication'.",
    "suggestive of": "Rewrite using the verb 'suggest' instead of construction with 'suggestive of'.",
    "indicative of": "Rewrite using the verb 'indicate' instead of construction with 'indicative of'.",
    
    # Inconcise expressions
    " is known to ": "Try rewriting without vague 'is known to', e.g. rewrite 'A is known to cause B' as 'A causes B'.",
    " are known to ": "Try rewriting without vague 'are known to', e.g. rewrite 'A are known to cause B' as 'A causes B'.",
    "a variety of": "Replace 'a variety of' with shorter 'various'.",
    "by means of": "Usually, 'by means of' can be replaced with shorter 'by' or 'using'.",
    "It is important to note": "Consider replacing long 'It is important to note' with just 'Note'.",
    "In this work": "You may replace 'In this work' with shorter 'Here' or just start with 'We show that'.",
    "In this article": "You may replace 'In this article' with just 'Here, ...' or just start with 'We show that'.",
    "In this paper": "You may replace 'In this paper' with just 'Here, ...' or just start with 'We show that'.",
    "In recent years": "Consider replacing 'In recent years' with shorter 'Recently' or more specific 'Since 1999'.",
    "make it possible": "Consider replacing 'make it possible' with shorter 'enable'.",
    "makes it possible": "Consider replacing 'makes it possible' with shorter 'enables'.",
    "in a reliable manner": "Consider replacing 'in a reliable manner' with shorter 'reliably'.",
    "Consequently": "Consider replacing 'Consequently' with shorter 'Thus' or 'Hence'.",
    "therefore": "Consider replacing 'therefore' with shorter 'thus' or 'hence'.",
    "Nevertheless": "You may consider replacing 'Nevertheless' with shorter 'Yet' or 'But'.",
    "In addition,": "You may consider replacing 'In addition' with shorter 'Also'.",
    "For this reason": "Consider replacing 'For this reason' with shorter 'Thus' or 'Hence'.",
    "For these reasons": "Consider replacing 'For these reasons' with shorter 'Thus' or 'Hence'.",
    "Similarly,": "Consider replacing 'Similarly' with 'Likewise'.",
    "In contrast to": "Consider replacing 'In contrast to' with shorter 'Unlike'.",
    "In contrast with": "Consider replacing 'In contrast with' with shorter 'Unlike'.",
    "In order to": "Consider shortening 'In order to' as just 'To'.",
    "in order to": "Consider shortening 'in order to' as just 'to'.",
    "utilize": "Replace 'utilize' with simple 'use'.",
    "utilise": "Replace 'utilise' with simple 'use'.",
    "utilization": "Replace 'utilization' with simple 'use'.",
    "utilisation": "Replace 'utilisation' with simple 'use'.",
    "elevated temperature": "Replace 'elevated' with simpler 'higher'.",
    "on the other hand": "In some cases, you may replace 'on the other hand' with shorter 'however' or 'but'.",
    "On the other hand": "In some cases, you may replace 'On the other hand' with shorter 'However' or 'But'.",
    "for the purpose of": "Consider replacing 'for the purpose of' with shorter 'for'.",
    "For the purpose of": "Consider replacing 'For the purpose of' with shorter 'For'.",
    "prior to": "Consider replacing 'prior to' with simple 'before'.",
    "Prior to": "Consider replacing 'Prior to' with simple 'Before'.",
    "subsequent to": "Consider replacing 'subsequent to' with simple 'after'.",
    "facilitate": "Replace 'facilitate' with simple 'help'. According to The Craft Of Scientific Writing: 'Words such as facilitate are pretentious'.",
    "methodology": "Consider replacing 'methodology' with shorter 'method'.",
    "subsequent": "Consider replacing 'subsequent' with shorter 'later'.",
    "modify": "Consider replacing 'modify' with simpler 'change'.",
    "component": "Consider replacing 'component' with simpler 'part'.",
    "indication": "Consider replacing word 'indication' with simpler 'sign'.",
    
    # Empty adjectives
    "detailed": "Consider if adjective 'detailed' really adds anything here.",
    "fundamental": "Consider if adjective 'fundamental' really adds anything here.",
    
    # Overused words
    "clearly": "The word 'clearly' is clearly overused in science and often points to things that clearly are not so clear. Consider removing it.",
    " clear ": "The word 'clear' is overused in science and often points to things that actually are not so clear. Consider if it is necessary here.",
    "clearly demonstrate": "According to The Craft Of Scientific Writing: 'When someone uses clearly demonstrate more often than not those results do not clearly demonstrate anything at all'.",
    "unambiguous": "According to The Craft Of Scientific Writing: 'The word unambiguous is arrogant; it defies the reader to question the figure'.",
    "obviously": "The word 'obviously' is often misused in science and might describe something that is not so obvious. Consider removing it.",
    "Obviously": "The word 'Obviously' is often misused in science and might describe something that is not so obvious. Consider removing it.",
    "Basically": "The word 'Basically' is basically not very appropriate for academic writing. Consider removing it.",
    "basically": "The word 'basically' is basically not very appropriate for academic writing. Consider removing it.",
    "obvious ": "The word 'obvious' is often misused in science and might describe something that is not so obvious. Consider removing it.",
    "strongly": "The word 'strongly' is often strongly misused to describe not so strong things. Consider removing it and expressing the strength quantitatively.",
    "strong ": "The word 'strong' is often misused to describe not so strong things. Consider if the usage here is appropriate.",
    "significantly": "The word 'significantly' is often significantly misused and vague. It might mean statistically significant or significant to the author. State significance quantitatively.",
    "significant ": "The word 'significant' is often misused and vague. It might mean statistically significant or significant to the author. State significance quantitatively.",
    
    # Passive voice patterns
    "has been observed": "Consider rewriting the sentence with 'has been observed' in active voice, e.g. 'we observed that'.",
    "have been observed": "Consider rewriting the sentence with 'have been observed' in active voice, e.g. 'we observed that'.",
    "have been demonstrated": "Consider rewriting the sentence with 'have been demonstrated' in active voice, e.g. 'we demonstrated that'.",
    "has been demonstrated": "Consider rewriting the sentence with 'has been demonstrated' in active voice, e.g. 'we demonstrated that'.",
    "has been shown": "Consider rewriting the sentence with 'has been shown' in active voice, e.g. 'we showed that'.",
    "have been shown": "Consider rewriting the sentence with 'have been shown' in active voice, e.g. 'we showed that'.",
    "have been investigated": "Consider rewriting the sentence with 'have been investigated' in active voice, e.g. 'researchers investigated the effect'.",
    "has been investigated": "Consider rewriting the sentence with 'has been investigated' in active voice, e.g. 'researchers investigated the effect'.",
    "have been studied": "Consider rewriting the sentence with 'have been studied' in active voice, e.g. 'researchers studied the effect'.",
    "has been studied": "Consider rewriting the sentence with 'has been studied' in active voice, e.g. 'researchers studied the effect'.",
    "was observed": "Consider rewriting the sentence with 'was observed' in active voice, e.g. 'we observed that'.",
    "were observed": "Consider rewriting the sentence with 'were observed' in active voice, e.g. 'we observed that'.",
    "were demonstrated": "Consider rewriting the sentence with 'were demonstrated' in active voice, e.g. 'we demonstrated that'.",
    "was demonstrated": "Consider rewriting the sentence with 'was demonstrated' in active voice, e.g. 'we demonstrated that'.",
    "was shown": "Consider rewriting the sentence with 'was shown' in active voice, e.g. 'we showed that'.",
    "were shown": "Consider rewriting the sentence with 'were shown' in active voice, e.g. 'we showed that'.",
    "were investigated": "Consider rewriting the sentence with 'were investigated' in active voice, e.g. 'researchers investigated the effect'.",
    "was investigated": "Consider rewriting the sentence with 'was investigated' in active voice, e.g. 'researchers investigated the effect'.",
    "were studied": "Consider rewriting the sentence with 'were studied' in active voice, e.g. 'researchers studied the effect'.",
    "was studied": "Consider rewriting the sentence with 'was studied' in active voice, e.g. 'researchers studied the effect'.",
    
    # Inappropriate language
    "it's": "If you mean 'it is', it is better just to write 'it is'. Otherwise, it might need to be corrected as 'its'.",
    "kind of": "Consider kind of replacing 'kind of' with 'rather' or kind of avoiding it completely.",
    "pretty much": "Consider pretty much deleting 'pretty much'.",
    " and so on.": "Try to rewrite without '...and so on'. It might be too informal and vague.",
    " and so forth": "Try to rewrite without '...and so forth'. It might be too informal and vague.",
    "sort of": "Consider sort of replacing 'sort of' with 'rather' or sort of avoiding it completely.",
    " very ": "Consider if the word 'very' is very very necessary. If the emphasis is required, use words strong in themselves or quantify the statement.",
    " these days.": "These days we consider 'these days' too informal. Consider omitting or using 'recently'.",
    "don't": "Most academic journals prefer 'do not' instead of 'don't'.",
    "isn't": "Most academic journals prefer 'is not' instead of 'isn't'.",
    "wasn't": "Most academic journals prefer 'was not' instead of 'wasn't'.",
    "doesn't": "Most academic journals prefer 'does not' instead of 'doesn't'.",
    "wouldn't": "Most academic journals prefer 'would not' instead of 'wouldn't'.",
    "shouldn't": "Most academic journals prefer 'should not' instead of 'shouldn't'.",
    "it is": "Avoid constructions with 'it is' since they obscure the main subject and action of a sentence.",
    "there is": "Avoid constructions with 'there is' since they obscure the main subject and action of a sentence.",
    "there are": "Avoid constructions with 'there are' since they obscure the main subject and action of a sentence.",
    "It is": "Avoid constructions with 'It is' since they obscure the main subject and action of a sentence.",
    "There is": "Avoid constructions with 'There is' since they obscure the main subject and action of a sentence.",
    "There are": "Avoid constructions with 'There are' since they obscure the main subject and action of a sentence.",
    "Actually": "The word 'Actually' might actually be unnecessary.",
    "actually": "The word 'actually' might actually be unnecessary.",
    "really": "The word 'really' might be really unnecessary.",
    "a bit ": "Consider replacing informal 'a bit' with a bit more formal 'somewhat' or removing it completely.",
    "a lot of": "Consider replacing 'a lot of' with 'many' or 'several', or just give the exact number.",
    "A lot of": "Consider replacing 'A lot of' with 'Many' or 'Several', or just give the exact number.",
    "You ": "Using 'You' might be inappropriate in academic writing. Consider using 'One', e.g. 'One can see...'.",
    "you ": "Using 'you' might be inappropriate in academic writing. Consider using 'One', e.g. 'One can see...'.",
    "And ": "Instead of starting this sentence with 'And' try just removing it.",
    " thing": "The word 'thing' is rather vague, try to be more specific.",
    "Firstly": "In modern English 'First' is preferred to 'Firstly'.",
    "firstly": "In modern English 'first' is preferred to 'firstly'.",
    "Secondly": "In modern English 'Second' is preferred to 'Secondly'.",
    "secondly": "In modern English 'second' is preferred to 'secondly'.",
    "So,": "Beginning with 'So' might seem so informal. So, consider replacing it with 'Thus,'.",
    "So ": "Beginning with 'So' might seem so informal. So, consider replacing it with 'Thus'.",
    "By the way": "'By the way' might seem too informal.",
    "stand for": "'stand for' might seem too informal. Consider 'represent'.",
    "stands for": "'stands for' might seem too informal. Consider 'represents'.",
    "leave out": "'leave out' might seem too informal. Consider 'omit'.",
    "think about": "'think about' might seem too informal. Consider 'consider'.",
    "point out": "'point out' might seem too informal. Consider 'indicate'.",
}

# Very + adjective patterns (should use stronger words)
VERY_PATTERNS = {
    "very precise": "precise, exact, unimpeachable, perfect, flawless",
    "very basic": "rudimentary, primary, fundamental, simple",
    "very capable": "efficient, proficient, skillful",
    "very clean": "spotless, immaculate, stainless",
    "very clear": "transparent, sheer, translucent",
    "very competitive": "ambitious, driven, cutthroat",
    "very confident": "self-assured, self-reliant, secure",
    "very consistent": "constant, unfailing, uniform, same",
    "very critical": "vital, crucial, essential, indispensable, integral",
    "very dangerous": "perilous, precarious, unsafe",
    "very dark": "black, inky, ebony, sooty",
    "very deep": "abysmal, bottomless, vast",
    "very delicate": "subtle, slight, fragile, frail",
    "very different": "unusual, distinctive, atypical, dissimilar",
    "very difficult": "complicated, complex, demanding",
    "very easy": "effortless, uncomplicated, unchallenging, simple",
    "very fast": "rapid, swift, fleet, blistering",
    "very first": "first",
    "very few": "meager, scarce, scant, limited, negligible",
    "very good": "superb, superior, excellent",
    "very important": "crucial, vital, essential, paramount, imperative",
    "very impressive": "extraordinary, remarkable",
    "very interesting": "fascinating, remarkable, intriguing, compelling",
    "very large": "huge, giant",
    "very long": "extended, extensive, interminable, protracted",
    "very new": "innovative, fresh, original, cutting-edge",
    "very obvious": "apparent, evident, plain, visible",
    "very reasonable": "equitable, judicious, sensible, practical, fair",
    "very recent": "the latest, current, fresh, up-to-date",
    "very rough": "coarse, jagged, rugged, craggy, gritty, broken",
    "very severe": "acute, grave, critical, serious, brutal, relentless",
    "very significant": "key, notable, substantial, noteworthy, momentous, major, vital",
    "very similar": "alike, akin, analogous, comparable, equivalent",
    "very simple": "basic, easy, straightforward, effortless, uncomplicated",
    "very small": "tiny, minuscule, infinitesimal, microscopic, petite",
    "very smooth": "flat, glassy, polished, level, even, unblemished",
    "very specific": "precise, exact, explicit, definite, unambiguous",
    "very strange": "weird, eerie, bizarre, uncanny, peculiar, odd",
    "very strict": "stern, austere, severe, rigorous, harsh, rigid",
    "very substantial": "considerable, significant, extensive, ample",
    "very unlikely": "improbable, implausible, doubtful, dubious",
    "very unusual": "abnormal, extraordinary, uncommon, unique",
    "very visible": "conspicuous, exposed, obvious, prominent",
    "very weak": "feeble, frail, delicate, debilitated, fragile",
    "very wide": "vast, expansive, sweeping, boundless",
    "very afraid": "terrified",
    "very often": "frequently",
    "very old": "ancient",
    "very open": "transparent",
    "very perfect": "flawless",
    "very powerful": "compelling",
    "very quick": "rapid",
    "very quiet": "hushed",
    "very serious": "grave",
    "very shiny": "gleaming",
    "very short": "brief",
}

# Redundant phrases
REDUNDANT_PATTERNS = {
    "PM in the afternoon": "PM",
    "AM in the morning": "AM",
    "necessary requirements": "requirements",
    "necessary requirement ": "requirement",
    "smaller in size": "smaller",
    "future candidate": "candidate",
    "larger in size": "larger",
    "bigger in size": "bigger",
    "most unique": "unique",
    "resultant effect": "result",
    "end result": "result",
    "pooled together": "pooled",
    "assemble together": "assemble",
    "fewer in number": "fewer",
    "exactly the same": "the same",
    "revert back": "revert",
    "reverted back": "reverted",
    "shorter in length": "shorter",
    "longer in length": "longer",
    "summarize briefly": "summarize",
    "briefly summarize": "summarize",
    "a total of": "ten samples",
    "A total of": "Ten samples",
    "close proximity": "proximity",
    "each and every": "each",
    "Each and every": "Each",
    "already exist": "exist",
    "alternative choice": "choice",
    "basic fundamentals": "fundamentals",
    "continue to remain": "remain",
    "continues to remain": "remains",
    "empty space": "space",
    "introduce a new": "introduce",
    "introduced a new": "introduced",
    "mix together": "mix",
    "never before": "never",
    "period of time": "period",
    "separate entities": "entities",
    "still persist": "persist",
    "return back": "return",
    "returned back": "returned",
    "true fact": "fact",
    "repeated again": "repeated",
    "repeating again": "repeated",
    "repeat again": "repeated",
    "already has been": "has been",
    "already have been": "have been",
    "join together": "join",
    "joined together": "join",
    "might possibly": "might",
    "might perhaps": "might",
    "must necessarily": "must",
    "must inevitably": "must",
    "previous experience": "experience",
    "prior experience": "experience",
    "past experience": "experience",
    "first conceived": "conceived",
    "actual fact": "fact",
    "advance forward": "advance",
    "add an additional": "add",
    "added bonus": "bonus",
    "all-time record": "record",
    "and etc.": "etc.",
    "anonymous stranger": "stranger",
    "annual anniversary": "anniversary",
    "ask the question": "ask",
    "ATM machine": "ATM",
    "bald-headed": "bald",
    "best ever": "best",
    "brief in duration": "brief",
    "careful scrutiny": "scrutiny",
    "cash money": "cash",
    "classify into groups": "classify",
    "commute back and forth": "commute",
    "compete with each other": "compete",
    "component part": "part",
    "confused state": "confused",
    "crisis situation": "crisis",
    "current trend": "trend",
    "depreciate in value": "depreciate",
    "depreciates in value": "depreciates",
    "depreciated in value": "depreciated",
    "desirable benefit": "benefit",
    "disappear from sight": "disappear",
    "disappeared from sight": "disappeared",
    "earlier in time": "",
    "eliminate altogether": "eliminate",
    "emergency situation": "emergency",
    "enclosed herein": "enclosed",
    "enter in ": "enter",
    "entirely eliminate": "eliminate",
    "equal to one another": "equal",
    "equals to one another": "equal",
    "eradicate completely": "eradicate",
    "estimated at about": "estimated at",
    "evolve over time": "evolve",
    "exact same": "same",
    "face mask": "mask",
    "few in number": "few",
    "first and foremost": "first",
    "First and foremost": "First",
    "first of all": "first",
    "First of all": "First",
    "fly through the air": "fly",
    "follow after": "follow",
    "foreign imports": "imports",
    "free gift": "gift",
    "full satisfaction": "satisfaction",
    "general public": "public",
    "GRE exam": "GRE",
    "grow in size": "grow",
    "harmful injuries": "injuries",
    "harmful injury": "injury",
    "HIV virus": "HIV",
    "hollow tube": "tube",
    "incredible to believe": "incredible",
    "integrate with each other": "integrate",
    "integrated with each other": "integrated",
    "irregardless": "regardless",
    "joint collaboration": "collaboration",
    "knowledgeable expert": "expert",
    "lag behind": "lag",
    "LCD display": "LCD",
    "little baby": "baby",
    "local resident": "resident",
    "look back in retrospect": "look back",
    "manually by hand": "manually",
    "meet with each other": "meet",
    "mental telepathy": "telepathy",
    "mutual cooperation": "cooperation",
    "mutually interdependent": "interdependent",
    "mutual respect for each other": "mutual respect",
    "natural instinct": "instinct",
    "none at all": "none",
    "nostalgia for the past": "nostalgia",
    "now pending": "pending",
    "oral conversation": "conversation",
    "outside in the yard": "in the yard",
    "outside of": "outside",
    "over exaggerate": "exaggerate",
    "pair of twins": "twins",
    "palm of the hand": "palm",
    "penetrate into": "penetrate",
    "pick and choose": "choose",
    "polar opposites": "opposites",
    "postpone until later": "postpone",
    "previously listed above": "listed above",
    "proceed ahead": "proceed",
    "pursue after": "pursue",
    "RAM memory": "RAM",
    "recur again": "recur",
    "recurred again": "recurred",
    "regular routine": "routine",
    "round in shape": "round",
    "same exact": "same",
    "sand dune": "dune",
    "scrutinize in detail": "scrutinize",
    "scrutinized in detail": "scrutinized",
    "separated apart from each other": "separated",
    "serious danger": "danger",
    "shiny in appearance": "shiny",
    "spell out in detail": "spell out",
    "start off": "start",
    "sudden impulse": "impulse",
    "sum total": "sum",
    "surrounded on all sides": "surrounded",
    "time period": "period",
    "tiny bit": "bit",
    "total destruction": "destruction",
    "truly sincere": "sincere",
    "two equal halves": "halves",
    "ultimate goal": "goal",
    "undergraduate student": "undergraduate",
    "underground subway": "subway",
    "universal panacea": "panacea",
    "unnamed anonymous": "anonymous",
    "usual custom": "custom",
    "very unique": "unique",
    "visible to the eye": "visible",
    "warn in advance": "warn",
    "whether or not": "whether",
    "completely eliminate": "eliminate",
    "completely fill": "fill",
    "advance planning": "planning",
    "absolutely essential": "essential",
    "absolutely necessary": "necessary",
    "unexpected surprise": "surprise",
    "fall down": "fall",
    "add up": "add",
    "heat up": "heat",
    "rise up": "rise",
    "open up": "open",
    "circle around": "circle",
    "final conclusion": "conclusion",
    "final outcome": "outcome",
    "cancel out": "cancel",
    "canceled out": "canceled",
    "cancels out": "cancels",
    "future plan": "plan",
    "frozen ice": "ice",
    "empty hole": "hole",
    "major breakthrough": "breakthrough",
    "reflect back": "reflect",
    "reflects back": "reflects",
    "reflected back": "reflected",
    "personal friend": "friend",
    "personal opinion": "opinion",
    "soft in texture": "soft",
    "soft to the touch": "soft",
    "weather conditions": "weather",
    "weather situation": "weather",
    "introduced for the first time": "introduced",
    "introduce for the first time": "introduce",
    "plan ahead": "plan",
    "plan in advance": "plan",
}

# Negative patterns (should use positive alternatives)
NEGATIVE_PATTERNS = {
    "not able": "unable",
    "not different": "alike",
    "did not accept": "rejected",
    "does not accept": "rejects",
    "do not accept": "reject",
    "did not consider": "ignored",
    "have not considered": "ignored",
    "has not considered": "ignored",
    "do not considered": "ignore",
    "do not allow": "prevent",
    "did not allow": "prevented",
    "does not allow": "prevents",
    "does not have": "lacks",
    "do not have": "lack",
    "did not have": "lacked",
    "non symmetric": "asymmetric",
    "non-symmetric": "asymmetric",
    "not symmetric": "asymmetric",
    "non polarized": "unpolarized",
    "not important": "unimportant",
    "not known": "unknown",
    "not significant": "negligible",
}

# Absolute words (should be used with caution)
ABSOLUTE_PATTERNS = {
    " never ": "According to Craft of Scientific Writing: 'Never is a frightening word because it invites the readers to think of exceptions'. Consider alternatives: 'rarely', 'seldom', 'remains unclear', 'remains challenging'.",
    "always": "According to Craft of Scientific Writing: 'Always is a frightening word because it invites the readers to think of exceptions. You should go in fear of absolutes'.",
}

# Complex words (should use simpler synonyms)
COMPLEX_WORDS = {
    "elucidate": "explain",
    "diminish": "decrease",
    "establish": "set",
    "depict": "show",
    "comprehensive": "detailed",
    "eliminate": "remove",
    "terminate": "finish",
    "discontinue": "stop",
    "immense": "great",
    "profound": "deep",
    "extensive": "wide",
    "substantial": "large",
    "essential": "important",
    "foremost": "above all",
    "prominent": "well known",
    "distinguished": "well known",
    "override": "cancel",
    "assess": "evaluate",
    "indistinguishable": "identical",
    "laborious": "difficult",
    "intricate": "complex",
    "elaborate": "design",
    "convoluted": "complex",
    "sophisticated": "complex",
    "adjacent": "near",
    "conceal": "hide",
    "acquire": "get",
    "execute": "do",
    "outstanding": "great",
    "achievement": "result",
    "prevalent": "dominant",
    "tremendous": "huge",
    "infinitesimal": "tiny",
    "substantiate": "verify",
}

# LaTeX-specific patterns
LATEX_PATTERNS = {
    r'\$\\mu\$m': r'You may replace LaTeX expression "$\\mu$m" with "{\\textmu}m" for better looking letter mu.',
    r'\$\\mu\$s': r'You may replace LaTeX expression "$\\mu$s" with "{\\textmu}s" for better looking letter mu.',
    r'\$\\mu\$g': r'You may replace LaTeX expression "$\\mu$g" with "{\\textmu}g" for better looking letter mu.',
    r'\\hslash': r'If by "\\hslash" you mean the reduced Planck constant, use "\\hbar".',
    r'\+/-': r'If you are in LaTeX, use "\\pm" instead of "+/-". Otherwise, find proper plus-minus symbol.',
    r' \$\\^\\circ\$C': 'Degrees Celsius should not be separated from the number with a space',
    r' \$\\^\\circ\$F': 'Degrees Fahrenheit should not be separated from the number with a space.',
    r'Fig\.': 'Most journals prefer capitalized references to figures, e.g. "as shown in Fig. 1".',
    r'figs\.': 'Most journals prefer capitalized references to figures, e.g. "as shown in Figs. 1-2".',
    r'\[Fig': 'Most journals prefer regular brackets for figure references, e.g. (Fig. 1).',
    r'\(see Fig': 'You can omit the word "see" in the figure reference, e.g. (Fig. 1).',
    r'\(see fig': 'You can omit the word "see" in the figure reference, e.g. (Fig. 1).',
    r'\(as shown in Fig': 'You can omit the words "as shown in" in the figure reference, e.g. (Fig. 1).',
    r'\(shown in Fig': 'You can omit the words "shown in" in the figure reference, e.g. (Fig. 1).',
    r'Eq\. \(': 'Brackets around the equation number are usually unnecessary, e.g. Eq. 1., check guidelines for your journal.',
}

# Grammar patterns
GRAMMAR_PATTERNS = {
    # Oxford comma patterns (missing comma before 'and' in lists)
    r'(\w+),\s+(\w+)\s+and\s+(\w+)': 'Consider using Oxford comma: "X, Y, and Z" instead of "X, Y and Z"',
    # Article issues
    r'\ba\s+[aeiouAEIOU]': 'Check if "a" should be "an" before vowel sounds',
    r'\ban\s+[bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ]': 'Check if "an" should be "a" before consonant sounds',
    # Common grammar mistakes
    r'less\s+\w+s\b': 'Verify that "less" is not misused for "fewer" (e.g. "less time", but "fewer samples")',
    r'more\s+then\b': 'Probably "then" should be changed to "than" if this is a comparison.',
    r'less\s+then\b': 'Probably "then" should be changed to "than" if this is a comparison.',
    r'higher\s+then\b': 'Probably "then" should be changed to "than" if this is a comparison.',
    r'lower\s+then\b': 'Probably "then" should be changed to "than" if this is a comparison.',
    r'better\s+then\b': 'Probably "then" should be changed to "than" if this is a comparison.',
    r'data\s+is\b': 'The word "data" is plural, double-check if "data is" is correct.',
    r'data\s+has\b': 'The word "data" is plural, double-check if "data has" is correct.',
    r'data\s+shows\b': 'The word "data" is plural, double-check if "data shows" is correct.',
    r'\s0\s': 'Simple numbers 0-10 are better to be spelled out, e.g. "five samples", "above zero", "equal to one".',
    r'and/or': 'Try to say it without "and/or" monstrosity. Often, just "and" or "or" is enough.',
    r'or/and': 'Try to say it without "or/and" monstrosity. Often, just "and" or "or" is enough.',
    r'\s+the\s+the\s+': 'Seems like "the" is repeated twice.',
    r'\s+a\s+a\s+': 'Seems like "a" is repeated twice.',
    r'\s+an\s+an\s+': 'Seems like "an" is repeated twice.',
    r'irregardless': 'Replace "irregardless" with "regardless".',
    r'Monte-Carlo': 'Spell "Monte-Carlo" without a hyphen, i.e. "Monte Carlo".',
    r'is comprised of': 'Correct "is comprised of" as "comprises". The whole comprises its parts.',
    r'are comprised of': 'Correct "are comprised of" as "comprise". The whole comprises its parts.',
    r'different than': 'Correct "different than" as "different from".',
}


def check_banned_words_realtime(text: str) -> List[Issue]:
    """
    Check for banned words in the text and provide suggestions.
    
    Args:
        text: The text to check
        
    Returns:
        List of Issue objects with locations and suggestions
    """
    issues = []
    lines = text.split('\n')
    
    for line_num, line in enumerate(lines, start=1):
        words = re.findall(r'\b\w+\b', line.lower())
        
        for word_pos, word in enumerate(words, start=1):
            if word in BANNED_WORDS:
                suggestions = ", ".join(BANNED_WORDS[word])
                issues.append(Issue(
                    issue_type=IssueType.BANNED_WORD,
                    location=(line_num, word_pos),
                    text=word,
                    suggestion=f"Replace with: {suggestions}",
                    severity="medium"
                ))
    
    return issues


def check_ai_phrases(text: str) -> List[Issue]:
    """
    Check for AI phrases in the text.
    
    Args:
        text: The text to check
        
    Returns:
        List of Issue objects with detected AI phrases
    """
    issues = []
    lines = text.split('\n')
    
    for line_num, line in enumerate(lines, start=1):
        line_lower = line.lower()
        
        for phrase_pattern, suggestion in AI_PHRASES.items():
            matches = re.finditer(phrase_pattern, line_lower)
            for match in matches:
                issues.append(Issue(
                    issue_type=IssueType.AI_PHRASE,
                    location=(line_num, match.start()),
                    text=match.group(0),
                    suggestion=suggestion,
                    severity="high"
                ))
    
    return issues


def analyze_sentence_patterns(text: str) -> List[Issue]:
    """
    Analyze sentence patterns for AI-favored structures.
    
    Args:
        text: The text to analyze
        
    Returns:
        List of Issue objects with detected patterns
    """
    issues = []
    lines = text.split('\n')
    
    for line_num, line in enumerate(lines, start=1):
        line_lower = line.lower()
        
        # Check for banned patterns
        for pattern_info in BANNED_PATTERNS:
            matches = re.finditer(pattern_info["pattern"], line_lower)
            for match in matches:
                issues.append(Issue(
                    issue_type=IssueType.SENTENCE_PATTERN,
                    location=(line_num, match.start()),
                    text=match.group(0),
                    suggestion=pattern_info["suggestion"],
                    severity="high"
                ))
        
        # Check for rule of three (three-item lists)
        three_item_pattern = r"(\w+),\s+(\w+),\s+and\s+(\w+)"
        matches = re.finditer(three_item_pattern, line_lower)
        if len(list(matches)) > 2:  # More than 2 three-item lists suggests overuse
            issues.append(Issue(
                issue_type=IssueType.REPETITIVE_STRUCTURE,
                location=(line_num, 0),
                text="Multiple three-item lists",
                suggestion="Vary list lengths (2, 4, 5 items when appropriate)",
                severity="low"
            ))
        
        # Check for excessive participial clauses
        participial_pattern = r"(\w+ing\s+\w+,\s+){2,}"  # Two or more -ing clauses
        if re.search(participial_pattern, line_lower):
            issues.append(Issue(
                issue_type=IssueType.SENTENCE_PATTERN,
                location=(line_num, 0),
                text="Excessive participial clauses",
                suggestion="Split into simpler sentences or use relative clauses",
                severity="medium"
            ))
        
        # Check for nominalizations
        nominalization_pattern = r"lead\s+to\s+an\s+increase\s+in|result\s+in\s+a\s+decrease\s+in"
        if re.search(nominalization_pattern, line_lower):
            issues.append(Issue(
                issue_type=IssueType.SENTENCE_PATTERN,
                location=(line_num, 0),
                text="Nominalization detected",
                suggestion="Use verb forms instead (e.g., 'increase' instead of 'lead to an increase in')",
                severity="medium"
            ))
    
    return issues


def suggest_replacements(word: str) -> List[str]:
    """
    Get replacement suggestions for a banned word.
    
    Args:
        word: The word to find replacements for
        
    Returns:
        List of suggested replacements
    """
    word_lower = word.lower()
    if word_lower in BANNED_WORDS:
        return BANNED_WORDS[word_lower]
    return []


def check_style_patterns(text: str) -> List[Issue]:
    """
    Check for style patterns from vim-angry-reviewer.
    
    Args:
        text: The text to check
        
    Returns:
        List of Issue objects with detected style patterns
    """
    issues = []
    lines = text.split('\n')
    
    for line_num, line in enumerate(lines, start=1):
        line_lower = line.lower()
        
        # Check style patterns
        for pattern, suggestion in STYLE_PATTERNS.items():
            if pattern.lower() in line_lower:
                # Find all occurrences
                start = 0
                while True:
                    pos = line_lower.find(pattern.lower(), start)
                    if pos == -1:
                        break
                    issues.append(Issue(
                        issue_type=IssueType.STYLE_RULE,
                        location=(line_num, pos),
                        text=pattern,
                        suggestion=suggestion,
                        severity="medium"
                    ))
                    start = pos + 1
    
    return issues


def check_very_patterns(text: str) -> List[Issue]:
    """
    Check for 'very + adjective' patterns that should use stronger words.
    
    Args:
        text: The text to check
        
    Returns:
        List of Issue objects with detected 'very' patterns
    """
    issues = []
    lines = text.split('\n')
    
    for line_num, line in enumerate(lines, start=1):
        line_lower = line.lower()
        
        for pattern, suggestions in VERY_PATTERNS.items():
            if pattern.lower() in line_lower:
                pos = line_lower.find(pattern.lower())
                issues.append(Issue(
                    issue_type=IssueType.ADVERB_ISSUE,
                    location=(line_num, pos),
                    text=pattern,
                    suggestion=f"Consider replacing '{pattern}' with words like '{suggestions}'",
                    severity="low"
                ))
    
    return issues


def check_redundant_patterns(text: str) -> List[Issue]:
    """
    Check for redundant phrases.
    
    Args:
        text: The text to check
        
    Returns:
        List of Issue objects with detected redundant patterns
    """
    issues = []
    lines = text.split('\n')
    
    for line_num, line in enumerate(lines, start=1):
        line_lower = line.lower()
        
        for pattern, replacement in REDUNDANT_PATTERNS.items():
            if pattern.lower() in line_lower:
                pos = line_lower.find(pattern.lower())
                issues.append(Issue(
                    issue_type=IssueType.REDUNDANT_PHRASE,
                    location=(line_num, pos),
                    text=pattern,
                    suggestion=f"Replace likely redundant '{pattern}' with just '{replacement}'",
                    severity="low"
                ))
    
    return issues


def check_negative_patterns(text: str) -> List[Issue]:
    """
    Check for negative patterns that should use positive alternatives.
    
    Args:
        text: The text to check
        
    Returns:
        List of Issue objects with detected negative patterns
    """
    issues = []
    lines = text.split('\n')
    
    for line_num, line in enumerate(lines, start=1):
        line_lower = line.lower()
        
        for pattern, replacement in NEGATIVE_PATTERNS.items():
            if pattern.lower() in line_lower:
                pos = line_lower.find(pattern.lower())
                issues.append(Issue(
                    issue_type=IssueType.STYLE_RULE,
                    location=(line_num, pos),
                    text=pattern,
                    suggestion=f"Replace negative '{pattern}' with a more positive '{replacement}'",
                    severity="medium"
                ))
    
    return issues


def check_absolute_patterns(text: str) -> List[Issue]:
    """
    Check for absolute words that should be used with caution.
    
    Args:
        text: The text to check
        
    Returns:
        List of Issue objects with detected absolute patterns
    """
    issues = []
    lines = text.split('\n')
    
    for line_num, line in enumerate(lines, start=1):
        line_lower = line.lower()
        
        for pattern, suggestion in ABSOLUTE_PATTERNS.items():
            if pattern.lower() in line_lower:
                pos = line_lower.find(pattern.lower())
                issues.append(Issue(
                    issue_type=IssueType.STYLE_RULE,
                    location=(line_num, pos),
                    text=pattern,
                    suggestion=suggestion,
                    severity="medium"
                ))
    
    return issues


def check_complex_words(text: str) -> List[Issue]:
    """
    Check for complex words that should use simpler synonyms.
    
    Args:
        text: The text to check
        
    Returns:
        List of Issue objects with detected complex words
    """
    issues = []
    lines = text.split('\n')
    
    for line_num, line in enumerate(lines, start=1):
        words = re.findall(r'\b\w+\b', line)
        
        for word_pos, word in enumerate(words, start=1):
            word_lower = word.lower()
            if word_lower in COMPLEX_WORDS:
                issues.append(Issue(
                    issue_type=IssueType.STYLE_RULE,
                    location=(line_num, word_pos),
                    text=word,
                    suggestion=f"Try using simple synonym '{COMPLEX_WORDS[word_lower]}' instead of '{word}'",
                    severity="low"
                ))
    
    return issues


def check_passive_voice(text: str) -> List[Issue]:
    """
    Check for passive voice patterns that could be active.
    
    Args:
        text: The text to check
        
    Returns:
        List of Issue objects with detected passive voice
    """
    issues = []
    lines = text.split('\n')
    
    passive_patterns = [
        (r"has been observed", "Consider rewriting in active voice, e.g. 'we observed that'"),
        (r"have been observed", "Consider rewriting in active voice, e.g. 'we observed that'"),
        (r"was observed", "Consider rewriting in active voice, e.g. 'we observed that'"),
        (r"were observed", "Consider rewriting in active voice, e.g. 'we observed that'"),
        (r"has been shown", "Consider rewriting in active voice, e.g. 'we showed that'"),
        (r"have been shown", "Consider rewriting in active voice, e.g. 'we showed that'"),
        (r"was shown", "Consider rewriting in active voice, e.g. 'we showed that'"),
        (r"were shown", "Consider rewriting in active voice, e.g. 'we showed that'"),
        (r"has been demonstrated", "Consider rewriting in active voice, e.g. 'we demonstrated that'"),
        (r"have been demonstrated", "Consider rewriting in active voice, e.g. 'we demonstrated that'"),
        (r"was demonstrated", "Consider rewriting in active voice, e.g. 'we demonstrated that'"),
        (r"were demonstrated", "Consider rewriting in active voice, e.g. 'we demonstrated that'"),
    ]
    
    for line_num, line in enumerate(lines, start=1):
        line_lower = line.lower()
        
        for pattern, suggestion in passive_patterns:
            matches = re.finditer(pattern, line_lower)
            for match in matches:
                issues.append(Issue(
                    issue_type=IssueType.PASSIVE_VOICE,
                    location=(line_num, match.start()),
                    text=match.group(0),
                    suggestion=suggestion,
                    severity="medium"
                ))
    
    return issues


def check_latex_patterns(text: str) -> List[Issue]:
    """
    Check for LaTeX-specific issues.
    
    Args:
        text: The text to check
        
    Returns:
        List of Issue objects with detected LaTeX issues
    """
    issues = []
    lines = text.split('\n')
    
    for line_num, line in enumerate(lines, start=1):
        for pattern, suggestion in LATEX_PATTERNS.items():
            matches = re.finditer(pattern, line)
            for match in matches:
                issues.append(Issue(
                    issue_type=IssueType.LATEX_ISSUE,
                    location=(line_num, match.start()),
                    text=match.group(0),
                    suggestion=suggestion,
                    severity="low"
                ))
    
    return issues


def check_grammar_patterns(text: str) -> List[Issue]:
    """
    Check for grammar issues including Oxford comma, articles, and common mistakes.
    
    Args:
        text: The text to check
        
    Returns:
        List of Issue objects with detected grammar issues
    """
    issues = []
    lines = text.split('\n')
    
    for line_num, line in enumerate(lines, start=1):
        line_lower = line.lower()
        
        # Check grammar patterns
        for pattern, suggestion in GRAMMAR_PATTERNS.items():
            matches = re.finditer(pattern, line_lower)
            for match in matches:
                issue_type = IssueType.GRAMMAR_ISSUE
                if 'oxford' in suggestion.lower() or 'comma' in suggestion.lower():
                    issue_type = IssueType.OXFORD_COMMA
                elif 'article' in suggestion.lower() or 'a ' in pattern or 'an ' in pattern:
                    issue_type = IssueType.ARTICLE_ISSUE
                
                issues.append(Issue(
                    issue_type=issue_type,
                    location=(line_num, match.start()),
                    text=match.group(0),
                    suggestion=suggestion,
                    severity="low"
                ))
    
    return issues


def check_all_issues(text: str) -> Dict[str, List[Issue]]:
    """
    Check all types of issues in the text.
    
    Args:
        text: The text to check
        
    Returns:
        Dictionary with issue types as keys and lists of issues as values
    """
    return {
        "banned_words": check_banned_words_realtime(text),
        "ai_phrases": check_ai_phrases(text),
        "sentence_patterns": analyze_sentence_patterns(text),
        "style_patterns": check_style_patterns(text),
        "very_patterns": check_very_patterns(text),
        "redundant_patterns": check_redundant_patterns(text),
        "negative_patterns": check_negative_patterns(text),
        "absolute_patterns": check_absolute_patterns(text),
        "complex_words": check_complex_words(text),
        "passive_voice": check_passive_voice(text),
        "latex_patterns": check_latex_patterns(text),
        "grammar_patterns": check_grammar_patterns(text),
    }


def format_issues_for_display(issues: List[Issue]) -> str:
    """
    Format issues for display to the user.
    
    Args:
        issues: List of Issue objects
        
    Returns:
        Formatted string with warnings and suggestions
    """
    if not issues:
        return "No issues detected."
    
    output = []
    for issue in issues:
        line_num, pos = issue.location
        output.append(f"⚠️ WARNING: {issue.issue_type.value.replace('_', ' ').title()}")
        output.append(f"  Location: Line {line_num}, position {pos}")
        output.append(f"  Text: \"{issue.text}\"")
        output.append(f"  Suggestion: {issue.suggestion}")
        output.append(f"  Severity: {issue.severity}")
        output.append("")
    
    return "\n".join(output)


if __name__ == "__main__":
    # Example usage
    sample_text = """
    This article will discuss the intricate complexities of the research.
    It is important to note that we delved into the realm of comprehensive analysis.
    The findings aren't just significant, they're pivotal to understanding the landscape.
    """
    
    all_issues = check_all_issues(sample_text)
    for issue_type, issues in all_issues.items():
        if issues:
            print(f"\n{issue_type.upper()}:")
            print(format_issues_for_display(issues))
