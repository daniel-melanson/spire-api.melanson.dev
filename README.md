# spire-api.melanson.dev (WIP)

An API for public information on [UMass Spire](https://www.spire.umass.edu/).

## Purpose

Information about courses, sections, and subjects is publicly available; but retrieving that information from Spire is non-trivial. To enable myself, and other students, to easily create applications that work with this data a cleaner interface needed to be implemented.

## Documentation

A list of schemas and endpoints can be found [here](https://spire-api.melanson.dev/docs).

## Crawling Routine

Requests to endpoints do not immediately query Spire and get the most up-to-date information. Requests will query a database that is routinely updated. This means that the information in this database is not guaranteed to be accurate.

`Section` and `Course` records have an included `_updated_at` field which document when their information was updated.

### Coverage

Every course (and subject) in the course catalog (`Main Menu > Course Guides > Browse Course Catalog`) is scraped.

Every section during or after the Fall 2018 term is scraped. But only sections that will reasonably be updated are scraped routinely. Meaning, once posted, terms are scraped routinely until they are considered over (Spring ends in June 1st, Summer ends in September 15th, Fall ends in January 1st, Winter ends in February 15th).

### Schedule

The course catalog is scraped once a week. The routine usually finishes within 6 hours.

## Inconsistencies

Instructor names are assumed to be unique. This makes handling cases where staff names are documented without emails nicer to handle. This does come with the drawback that some staff might be merged together (considered the same person despite having different emails). However, I do not think that this will happen frequently and the benefit of matching sections labeled without an email is outweighs this.

## Organization

A `Course` is a unique instance of a id across spire. The default information for a course is first obtained from the course catalog. This will generate structures like a `CourseDetail` and `CourseEnrollmentInformation` based on the present information on a course's catalog page.

`Section`s will reference course objects, if one exists with a matching id, or create stub objects using providing only absolute information (id, subject, number, title). They potentially have their own `alternative_title` if the title listed on the section is different from the title listed for the respective `Course` object.
