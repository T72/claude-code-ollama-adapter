# Session Summary Prompt Template

Use this prompt template to create consistent development session summaries. Fill in all sections with relevant information from your session.

````markdown
# Development Session: [Main Focus/Feature Name]

**Date**: [YYYY-MM-DD]  
**Branch**: [branch-name]  
**Focus**: [Brief description of session focus]

## Session Summary

[One-paragraph summary of major accomplishments, challenges overcome, and overall progress. Keep this brief but comprehensive.]

## Initial Context

[Describe the starting point of the session. What was the state of the project before you began? What issues were you trying to address?]

## Accomplishments

[List major accomplishments in detail, structured as sections with bullet points]

### 1. [First Major Accomplishment]

- [Detail point]
- [Detail point]
- [Created/Modified component X with features a, b, c]

### 2. [Second Major Accomplishment]

#### [Subsection if needed]

- [Detail point]
- [Detail point]

[Include code examples if relevant]

```typescript
// Example code if applicable
```
````

## Implementation Status

Note: Implementation status of our features shall be kept updated for each feature individually in here: docs\developer\current-implementation\features

### Working Features

✅ [Feature 1]  
✅ [Feature 2]  
✅ [Feature 3]

### Pending Features

- [ ] [Pending Feature 1]
- [ ] [Pending Feature 2]
- [ ] [Pending Feature 3]

### Implementation Gaps identified and documented

- [ ] [Implementation Gap 1]
      Reference to implementation gap 1 documentation included in current implementation status of feature in docs\developer\current-implementation\features
- [ ] [Implementation Gap 2]
      Reference to implementation gap 2 documentation included in current implementation status of feature in docs\developer\current-implementation\features
- [ ] [Implementation Gap 3]
      Reference to implementation gap 3 documentation included in current implementation status of feature in docs\developer\current-implementation\features

## Key Decisions Made

1. **[Decision Title]**: [Explanation of the decision and rationale. Reference any ADR if applicable]

2. **[Decision Title]**: [Explanation of the decision and rationale]

3. **[Decision Title]**: [Explanation of the decision and rationale]

## Files Created/Modified

### New Features

- `[file/path/to/new/feature]` - [Brief description]
- `[file/path/to/new/feature]` - [Brief description]

### Updates

- `[file/path/to/updated/feature]` - [Brief description of changes]

### Documentation

- `[file/path/to/documentation]` - [Brief description]

## Next Session Focus

[List specific tasks to focus on in the next session, can be formatted as a checklist]

1. **[Focus Area 1]**

   - [Specific task]
   - [Specific task]

2. **[Focus Area 2]**
   - [Specific task]
   - [Specific task]

## Notes

- [Any additional notes, considerations, or warnings]
- [Observations about the implementation]
- [Limitations or technical debt]
- [Future considerations]
  ´´´

## Instructions for Use

1. Copy the entire template above
2. Replace all placeholder text (text inside square brackets `[]`)
3. Remove any sections that are not relevant to your session
4. Add additional subsections as needed
5. Include code examples for complex implementations
6. Be specific about implementation status and next steps
7. Document key decisions and their rationale
8. List all files created or modified
9. Ensure the summary is concise but comprehensive

Checklist:

- [ ] Copy the entire template above
- [ ] Replace all placeholder text (text inside square brackets `[]`)
- [ ] Remove any sections that are not relevant to your session
- [ ] Add additional subsections as needed
- [ ] Include code examples for complex implementations
- [ ] Be specific about implementation status and next steps
- [ ] Document key decisions and their rationale
- [ ] List all files created or modified
- [ ] Ensure the summary is concise but comprehensive enough to allow continuation of our work where we left off

## Best Practices

- Write in past tense for completed work
- Include references to documentation where applicable
- Link to relevant issues, ADRs, or other documentation following our established protocols from: docs\protocols
- Prioritize the use of checkmarks while sparingly using emojs ✅, ⚠️, ❌ to highlight status
- Include specific metrics where available (test results, performance)
- Document lessons learned during the session in docs\developer\development\lessons-learned following our lessons learned template docs\developer\templates\lessons-learned-template.md and integration protocol docs\protocols\lessons-learned-integration-protocol.md
- Keep your audience in mind (other junior developers who may need to understand your work)

## Documentation References

Lessons learned documentation references:

- docs\developer\development\lessons-learned
- docs\developer\templates\lessons-learned-template.md
- docs\protocols\lessons-learned-integration-protocol.md

Feature related documentation references:

Feature specifcations and/or requirements:

- docs\specifications\requirements\features

Feature Implementation Status Reference:

- docs\developer\current-implementation\features
