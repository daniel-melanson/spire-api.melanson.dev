# spire-api.melanson.dev

An API for public information on [UMass Spire](https://www.spire.umass.edu/).

## Purpose

Information about courses, sections, and subjects is publicly available; but retrieving that information from Spire is difficult. This web crawler will retrieve as much information from Spire as possible and serve it on a public RESTful API.

If you have a need that is not met by this API, please open an issue, or email me and I can provide a `pg_dump` of the database.

## Documentation

A list of schemas and endpoints can be found [here](https://spire-api.melanson.dev/docs).

## Crawling Routine

**Requests to endpoints do not immediately query Spire and get the most up-to-date information.** Requests will query a database that is routinely updated. This means that the information in this database is not guaranteed to be accurate.

`Section` and `Course` records have an included `_updated_at` field which document when their information was last updated.

**As of November 2023 section information is scraped once a week (Sunday at 02:00AM EST).**

### Coverage

Every section during or after the Fall 2018 term is scraped. But only sections that will reasonably be updated are scraped routinely. Meaning, once posted, terms are scraped until they are considered over (Spring ends in June 1st, Summer ends in September 15th, Fall ends in January 1st, Winter ends in February 15th).

## Inconsistencies

Instructor names are assumed to be unique. This makes handling cases where staff names are documented without emails nicer to handle. This does come with the drawback that some staff members might be merged together (considered the same person despite having different emails).

`Course` information fields (`details` and `enrollment_information`) are no longer updated as the course catalog is no longer a public page (unlike search). Now, if a new course is encountered, a stub `Course` object is created without the `details` or `enrollment_information` fields.

For general course information, it recommend using information from the most recent offered section.
