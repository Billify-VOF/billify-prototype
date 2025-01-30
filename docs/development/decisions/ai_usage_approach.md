# Adr: Using AI as a mentor rather than a code generator

## Status
Accepted

## Context
During early development, we initially used AI to generate code directly. However, this led to several issues:
- Lack of understanding of the generated code
- Difficulty in debugging issues
- Black box solutions with hidden assumptions
- Potential for technical debt due to misaligned design decisions
- Risk of knowledge atrophy in the development team

We needed to decide on a more sustainable approach to leveraging AI in our development process.

## Decision
We decided to use AI as a mentor and guide rather than a direct code generator. This approach is implemented through specific interaction patterns:

### Core principles
1. Never have AI write complete code solutions
2. Use AI to guide and teach while we write the code
3. Focus on understanding and learning
4. Challenge AI's assumptions and suggestions
5. Maintain knowledge parity with the codebase

### Implementation approach
1. Start with analysis and context:
   ```
   Instead of: "Write me code for X"
   Do: "Let's analyze the requirements and design considerations for X"
   ```

2. Question assumptions:
   ```
   Instead of: "Should I use ReChart?"
   Do: "What are the pros and cons of different visualization libraries for our needs?"
   ```

3. Design before code:
   ```
   Instead of: "Generate a class for X"
   Do: "Let's discuss the design patterns and trade-offs for implementing X"
   ```

### Custom instructions
We've established specific .cursorrules (see [.cursorrules](../../../.cursorrules)) that enforce:
1. AI acts as a mentor, not a solution generator
2. Developers must write their own code
3. Focus on understanding and learning
4. Systematic approach to problem-solving

## Rationale

### Knowledge building
- Developers maintain deep understanding of the codebase
- Learning happens alongside development
- Team can effectively debug and maintain code
- Better understanding of design decisions and trade-offs

### Quality control
- Developers make informed micro and macro design decisions
- Better awareness of technical implications
- Reduced risk of misaligned architectural choices
- More maintainable codebase

### Long-term sustainability
- Prevents knowledge atrophy
- Builds stronger engineering capabilities
- Reduces dependency on AI for basic tasks
- Creates a learning-focused development culture

## Alternatives considered

### Full AI code generation
Pros:
- Faster initial development
- Less immediate effort required
- Quick prototyping

Cons:
- Black box solutions
- Limited understanding
- Difficulty in maintenance
- Hidden assumptions
- Potential for misaligned design decisions

### No AI usage
Pros:
- Complete control over code
- Deep understanding guaranteed
- Traditional learning path

Cons:
- Slower development
- Missing out on AI's knowledge base
- Less exposure to alternative approaches

## Consequences

### Positive
- Deeper understanding of codebase
- Better architectural decisions
- More maintainable code
- Stronger engineering team
- Sustainable learning culture
- Better debugging capabilities

### Negative
- Initially slower development
- More upfront effort required
- More time spent on analysis and design
- Need for disciplined approach to AI interaction

## Examples

### Before (problematic approach):
```python
# Directly asking AI to generate code
"Write me a Django model for invoice management"
```

### After (mentor approach):
```python
# Step 1: Analyze requirements
"What are the key considerations for storing invoice data?"

# Step 2: Discuss design
"Let's discuss the trade-offs between CharField and IntegerField for status"

# Step 3: Developer implements with guidance
"Can you review my implementation and suggest improvements?"
```

## Related decisions
- [Database choice](./database_choice.md)
- [Domain vs Django models](./domain_vs_django_models.md)
- [Urgency field type](./urgency_field_type.md)

## Notes
This decision reflects our commitment to building a strong, knowledgeable engineering team while still leveraging AI's capabilities. The mentor-based approach ensures we maintain deep understanding of our codebase while benefiting from AI's insights and guidance.