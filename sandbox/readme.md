# About

SCTA-people is a project to aggregate distributed work on prosopographies germane to the study of medieval scholasticism.

# Ways to Contribute to scta-people

There are two ways to contribute to scta-people.

Sumbit or update a record by sumitting a github pull request. Application developers can adopt the github api to programmatically contribute submissions another application.

Create a new graph for a given resource hosted in a place that you control and then register that graph with the scta record by submitting a pull request that updates the owl:sameAs property for that record.

An external graphs will be aggregated into the existing graph through a pre-processing build script that rebuilds the scta graph from the distributed sources. The re-built graph will then itself be submitted as a pull request so that this new graph can be compared and reviewed against the previous graph.

To learn how to prepare a graph see our [guidelines](guidelines.md)

To read a tutorial about to contribute via the github api, read our [contributing via github api tutorial](contributing-via-github-api.md).

# Shared Ontologies

To create or update an scta-people graph that will be accepted (as a pull request) or crawled as a connected graph, it must adopt an ontology and vocabulary that the SCTA understands. In this way, the SCTA aims to identify standards to help the global community ensure that we are talking about the same thing. Adopting agreed upon ontologies ensures that we can avoid false conflicts and discover there are places of genuine disagreement or uncertainty within the collective scholarly consensus.
