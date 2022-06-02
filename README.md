# spire-api.melanson.dev

A REST API for [UMass Spire](https://www.spire.umass.edu/).

## Purpose

Information about courses, sections, and subjects is publicly available; but retrieving that information from Spire is non-trivial. To enable myself, and other students, to easily create applications that work with this data a cleaner interface needed to be implemented.

## Documentation

A list of schemas and endpoints can be found [here](https://spire-api.melanson.dev/docs).

How some data entries are bundled might not make sense. I tried to be un-opinionated and make the schemas near identical to how information is displayed on Spire. Meaning a `Course` is a collection of data that would be on a course page `Main Menu > Course Guides > Browse Course Catalog > C > COMPSCI > CS 121`. The same idea applies to sections.

This means that no data is ignored and it is up to the end developer to decide which information to use. As an example, `Course`s and `Section`s may optionally have descriptions. However, the description in the most recent `Section` tends to be the more up-to-date version.

## Crawling Routine

Requests to endpoints do not immediately query Spire and get the most up-to-date information. Requests will query a database that is routinely updated. This means that the information in this database is not guaranteed to be accurate.

### Coverage

Every course (and subject) in the course catalog (`Main Menu > Course Guides > Browse Course Catalog`) is scraped.

Every section during or after the Spring 2018 term is scraped. But only sections that will reasonably be updated are scraped routinely. Meaning, once posted, terms are scraped routinely until they are considered over (Spring ends in June, Summer ends in September, Fall ends in January, Winter ends in February).

### Schedule

TO-DO.
