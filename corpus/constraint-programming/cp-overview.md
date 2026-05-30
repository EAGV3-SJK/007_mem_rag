# Constraint Programming (CP) Overview

Constraint Programming is a paradigm for solving combinatorial problems that works by stating constraints (properties) of a solution and then finding a solution that satisfies all constraints. It is particularly effective for problems in areas like scheduling, planning, and resource allocation.

A CP problem is defined by:
1.  **Variables:** A set of decision variables, each with a domain of possible values (e.g., an integer range, a set of categories).
2.  **Constraints:** A set of relationships between variables that restrict the values they can take simultaneously.

A CP solver explores the search space of possible variable assignments, systematically eliminating values that violate constraints. This process, called **propagation**, reduces the domains of variables. When propagation stops, the solver makes a choice (branching) to assign a value to a variable and repeats the process until a solution is found or the search space is exhausted.

Unlike traditional optimization methods that rely on a single objective function (like Linear Programming), CP excels at finding *feasible* solutions in highly constrained search spaces.