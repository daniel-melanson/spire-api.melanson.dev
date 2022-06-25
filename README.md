# spire-api.melanson.dev

An API for public information on [UMass Spire](https://www.spire.umass.edu/).

## Purpose

Information about courses, sections, and subjects is publicly available; but retrieving that information from Spire is non-trivial. To enable myself, and other students, to easily create applications that work with this data a cleaner interface needed to be implemented.

## Documentation

A list of schemas and endpoints can be found [here](https://spire-api.melanson.dev/docs).

How some data entries are bundled might not make sense. I tried to be un-opinionated and make the schemas near identical to how information is displayed on Spire. Meaning a `Course` is a collection of data that would be on a course page `Main Menu > Course Guides > Browse Course Catalog > C > COMPSCI > CS 121`. The same idea applies to sections.

This means that no data is ignored and it is up to the end developer to decide which information to use. As an example, `Course`s and `Section`s may optionally have descriptions. However, the description in the most recent `Section` tends to be the more up-to-date version.

## Crawling Routine

Requests to endpoints do not immediately query Spire and get the most up-to-date information. Requests will query a database that is routinely updated. This means that the information in this database is not guaranteed to be accurate.

`Section` and `Course` records have an included `_updated_at` field which document when their information was updated.

### Coverage

Every course (and subject) in the course catalog (`Main Menu > Course Guides > Browse Course Catalog`) is scraped.

Every section during or after the Fall 2018 term is scraped. But only sections that will reasonably be updated are scraped routinely. Meaning, once posted, terms are scraped routinely until they are considered over (Spring ends in June 1st, Summer ends in September 15th, Fall ends in January 1st, Winter ends in February 15th).

### Schedule

The course catalog is scraped once a week. The routine usually finishes within 6 hours.

Sections (retrieved from the search page) are scraped every two days. The routine usually takes around 8 hours

## Inconsistencies

Instructor names are assumed to be unique. This makes handling cases where staff names are documented without emails nicer to handle. This does come with the drawback that some staff might be merged together (considered the same person despite having different emails). However, I do not think that this will happen frequently and the benefit of matching sections labeled without an email is outweighs this.
