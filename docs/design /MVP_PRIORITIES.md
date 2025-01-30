# MVP focus and priorities

1. Focus on implementing and **validating the core value proposition**—real-time, easy-to-use, and understandable cash flow visibility—with as little complexity as possible. **Mitigate risks and manage limited resources by prioritising simplicity, reducing technical complexity and scope, and minimising third-party dependencies.** How can you simplify the core features of the pitch?

2. How can you develop a basic implementation of core features and facilitate iterative improvement and future feature development over time?

3. Reduce the scope and complexity of the MVP: scale down and simplify initial ambitions.
   1. Focus on one or two key integrations to avoid integrating multiple external financial systems. Building integrations is complex and time-consuming and introduces third-party dependencies. This could delay MVP release, and integration testing and maintenance could consume significant resources.
   2. Avoid sophisticated OCR as it is resource-intensive; instead, focus on a simple solution for the MVP.
   3. Real-time updates for each transaction require a highly efficient event-driven architecture, which might be too complex for an MVP. Begin with batch updates and progressively introduce real-time functionalities. Define a clear transition phase that includes user feedback on the necessity of this feature.
   4. Reduce the file types that can be used to upload invoices manually to only .csv, .xlsx and .pdf.
   5. Reduce infrastructure requirements.

4. Focus on creating a user-friendly design and user experience at every step. Ensure the user experience is intuitive, easy to use, and visually engaging. Validate the UX ease of use by collecting feedback and data from real users.

5. Launch early and frequently to deliver immediate value and fast time to market. Set up a system to collect user feedback, metrics, and data as soon as possible and have a quick iterative loop between feedback, fix implementation, new feature implementation, and testing.

6. Define key metrics for success for each new feature, both technical and on the product side. For example:
   1. Dashboard load time < 3 seconds
   2. Cash flow calculation accuracy > 99%
   3. CSV import success rate > 95%
   4. User satisfaction with the manual input process
   5. Time to complete basic cash flow setup < 30 minutes

7. Design a solid system architecture and use the following evaluation criteria for choosing the tech stack:
   1. Use the technology you are familiar with to move fast and focus on delivering value. Any time spent struggling with unfamiliar tech is precious time wasted.
   2. Use technology that is robust, stable and reliable:
       1. The technology has processes in place to handle security releases;
       2. There exists a lot of tooling and documentation;
       3. There are options for high availability and backups;
       4. There are options for scaling the technology that are clear and well-documented;
       5. There is a strong community of users, documented best practices, and help available to solve edge cases.
   3. Use technology that is proven and widely deployed:
       1. Are enough engineers and developers available who are knowledgeable and have experience working with the technology?
       2. Will it be difficult to migrate away from this technology if we decide to move away?
       3. '*Boring old tech*' > *'Shiny newest toy tech'*.
   4. Using scalable technology and architecture enables the addition of new integrations relatively quickly later on.
   5. Use technology that does not add disproportionate operational or technical complexity and is relatively easy to maintain.
   6. Use technology that is not too expensive.
   7. Use technology with the right balance of pros and cons for the product and the company.

8. Implement rudimentary and essential security, data and legal compliance practices (e.g., data encryption and secure access controls). Create a checklist with specific steps to ensure these compliance requirements are met with every feature release. Expand post-MVP.

9. Requirements should be adaptable and evolve through continuous feedback between the development team and users. Maintain an open line of communication to refine and adjust features based on ongoing user input.
   1. Requirements should be dynamic.
       1. Treat requirements as evolving living documents based on user feedback and real-world usage.
       2. Maintain flexibility to adapt features based on user needs discovered during development.
       3. Document key assumptions and validate them through user testing.
   2. Establish feedback loops.
       1. Create regular contact points between the development team and users.
       2. Set up systems to collect, analyse, and prioritise user feedback.
       3. Schedule periodic requirement reviews to incorporate learnings.
   3. Balance vision with reality.
       1. Start with minimal viable requirements that demonstrate core value.
       2. Add complexity gradually based on validated user needs.
       3. Be willing to modify or abandon features that don't serve user needs.
   4. Maintain clear communication.
       1. Keep stakeholders informed about requirement changes and their rationale.
       2. Document decisions and trade-offs made during development.
       3. Ensure alignment between business goals and technical implementation.