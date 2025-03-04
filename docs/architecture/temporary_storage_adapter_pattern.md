# ADR: Temporary Storage Adapter Pattern

## Status
Implemented

## Context
The Billify system requires a mechanism to temporarily store files during the invoice review process before committing them to permanent storage. This functionality is needed to:

1. Store uploaded invoice files temporarily during review
2. Provide a way to promote approved files to permanent storage
3. Automatically clean up rejected or expired temporary files
4. Track expiration times for temporary files

Two main approaches were considered:
1. Extending the existing `StorageRepository` interface with a new implementation
2. Creating an adapter that wraps any existing storage repository implementation

## Decision
Use the Adapter pattern to implement temporary storage functionality by creating a `TemporaryStorageAdapter` that wraps any `StorageRepository` implementation.

## Rationale

### Adapter Pattern Approach

#### Strengths
1. **Composition over Inheritance**
   - Uses composition to wrap any existing `StorageRepository` implementation
   - Follows the principle that composition is often preferable to inheritance
   - Provides more flexibility than creating a specialized implementation

2. **Separation of Concerns**
   - The adapter focuses solely on temporary file management
   - The underlying repository focuses solely on storage operations
   - Creates cleaner, more focused class responsibilities

3. **Interface Stability**
   - No need to modify the existing `StorageRepository` interface
   - Maintains backward compatibility with existing code
   - Follows the Open/Closed Principle - open for extension, closed for modification

4. **Reuse of Existing Code**
   - Reuses any existing repository implementation (FileStorage, ObjectStorage, etc.)
   - No duplication of storage logic in a new implementation
   - Makes the system more maintainable by reducing redundancy

5. **Infrastructure Separation**
   - Temporary vs. permanent storage is an infrastructure concern, not a domain concept
   - The adapter encapsulates infrastructure details away from domain code
   - Keeps storage implementation details separate from business processes

6. **Better Testability**
   - Makes it easier to mock the storage repository in tests
   - Supports testing temporary storage logic in isolation
   - Provides more focused test coverage

#### Limitations
1. **Indirection**
   - Adds an additional layer of indirection between client code and storage implementation
   - Creates a deeper call stack (client → adapter → repository) complicating debugging
   - Requires developers to understand both adapter and repository responsibilities
   - May introduce minimal performance overhead due to extra method calls

2. **Pattern Consistency**
   - Different from the predominant repository pattern used elsewhere in the codebase
   - May create confusion about when to use adapters vs direct repositories
   - Introduces architectural inconsistency that requires additional documentation
   - New team members face increased learning curve to understand mixed patterns

### Repository Implementation Approach

#### Strengths
1. **Pattern Consistency**
   - Follows the same pattern as existing storage implementations
   - Consistent with the repository pattern used throughout the system
   - Likely more familiar to developers used to the repository pattern

2. **Direct Implementation**
   - No wrapping/delegation layer
   - Potentially simpler call stack
   - More direct traceability

#### Limitations
1. **Duplication**
   - Would duplicate some storage logic
   - Harder to reuse existing implementations
   - Higher maintenance burden

2. **Less Flexible**
   - Tied to a specific storage implementation
   - Harder to adapt to different storage backends
   - Less composable

## Implementation Details

The `TemporaryStorageAdapter` provides the following key features:

1. **Two-Phase Storage**
   - `store_temporary`: Stores files in a temporary location with expiration tracking
   - `promote_to_permanent`: Moves approved files to permanent storage

2. **Expiration Handling**
   - Tracking of creation time for temporary files
   - Configurable expiration period (default: 24 hours)
   - `cleanup_expired`: Automatic removal of expired files

3. **Registry Management**
   - Maintains a simple JSON-based registry of temporary files
   - Tracks file paths and creation timestamps
   - Persists between application restarts

4. **Composition with Any Storage Repository**
   - Works with any implementation of the `StorageRepository` interface
   - Delegates actual storage operations to the wrapped repository

## Consequences

### Positive
1. **Flexibility**
   - Works with any storage repository implementation
   - Can be used with both file system and object storage
   - Easily adapted if storage requirements change

2. **Separation of Concerns**
   - Clear distinction between temporary file management and storage operations
   - Well-defined responsibilities for each component
   - Easier to maintain and extend

### Challenges
1. **Additional Layer**
   - Introduces an extra layer in the architecture
   - Slightly more complex object graph
   - Developers need to understand both repository and adapter patterns

2. **Configuration Complexity**
   - Requires proper configuration of both the adapter and underlying repository
   - More moving parts to manage

## Future Considerations
1. **Performance Monitoring**
   - Add metrics and monitoring for temporary storage usage
   - Track cleanup efficiency and storage reclamation

2. **Enhanced Registry**
   - Consider a more robust registry implementation for high-scale scenarios
   - Potentially move to a database-backed registry instead of JSON file

3. **Additional Features**
   - Implement manual cleanup and reporting tools
   - Add more granular controls for expiration policies 